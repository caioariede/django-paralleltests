from __future__ import absolute_import

import unittest
import itertools
import multiprocessing
import docker
import os.path
import shlex
import pickle
import base64
import time
import ctypes

from docker.utils import kwargs_from_env

from django.test.simple import DjangoTestSuiteRunner
from django.utils.unittest import defaultTestLoader
from django.conf import settings

from ..utils import unwrap_result


RUNTEST_CMD = getattr(
    settings, 'RUNTEST_CMD',
    'python {}/runtest.py'.format(os.path.dirname(os.path.dirname(__file__))))


_docker_cli = None
def get_docker_cli():
    global _docker_cli

    if _docker_cli is None:
        kwargs = kwargs_from_env()
        kwargs['tls'].assert_hostname = False
        _docker_cli = docker.Client(**kwargs)

    return _docker_cli


def split_tests(test):
    def _fmt(item):
        return '{}.{}.{}'.format(item.__class__.__module__,
                                 item.__class__.__name__,
                                 item._testMethodName)
    for cls, group in itertools.groupby(test, type):
        yield map(_fmt, group)


def run_test_container(tests):
    cmd = shlex.split(RUNTEST_CMD)

    env = {
        'TEST_RUNNER': 'paralleltests.runner.pickle.PickleRunner',
        'TEST_LABELS': ' '.join(tests),
    }

    cli = get_docker_cli()

    # Here we disable proxies entirely by setting trust_env=False as
    # indicated in: http://stackoverflow.com/a/28521696/639465
    #
    # The reason for doing this is to prevent the call to getproxies() in the
    # urllib that seems to not work well in some systems:
    #
    # https://bugs.python.org/issue9405
    cli.trust_env = False

    startTime = time.time()
    container = cli.create_container(
        image='paralleltest:latest', command=cmd, environment=env,
        host_config={'network_mode': 'host'})

    contid = container.get('Id')

    cli.start(contid)
    cli.wait(contid)

    buf = None
    mark = None
    done = False
    output = cli.logs(contid, stderr=True, stdout=True)
    lines = output.splitlines()

    for line in lines:
        if buf is None:
            if line.startswith('--- ') and len(line) == 44:
                buf = ''
                mark = line
        elif line == mark:
            done = True
            break
        else:
            buf += line
    stopTime = time.time()
    timeTaken = stopTime - startTime

    if done:
        return pickle.loads(base64.b64decode(buf))


class ParallelTestRunner(unittest.TextTestRunner):
    resultclass = unittest.TextTestResult

    def run(self, test):
        result = self._makeResult()
        unittest.registerResult(result)
        result.failfast = self.failfast
        startTime = time.time()
        self._run_tests(split_tests(test), result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run != 1 and "s" or "", timeTaken))
        self.stream.writeln()
        expectedFails = unexpectedSuccesses = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
        except AttributeError:
            pass
        else:
            expectedFails, unexpectedSuccesses, skipped = results

        infos = []
        if not result.wasSuccessful():
            self.stream.write("FAILED")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
        else:
            self.stream.write("OK")
        if skipped:
            infos.append("skipped=%d" % skipped)
        if expectedFails:
            infos.append("expected failures=%d" % expectedFails)
        if unexpectedSuccesses:
            infos.append("unexpected successes=%d" % unexpectedSuccesses)
        if infos:
            self.stream.writeln(" (%s)" % (", ".join(infos),))
        else:
            self.stream.write("\n")
        return result

    def _run_tests(self, tests, result):
        pool = multiprocessing.Pool(processes=4)

        for test_result in pool.imap_unordered(run_test_container, tests):
            unwrap_result(test_result)

            result.failures += test_result.failures
            result.errors += test_result.errors
            result.testsRun += test_result.testsRun
            result.skipped = test_result.skipped
            result.expectedFailures = test_result.expectedFailures
            result.unexpectedSuccesses = test_result.unexpectedSuccesses

            success = test_result.testsRun
            success -= len(test_result.failures)
            success -= len(test_result.errors)

            self.stream.write('.' * success)

            for f in test_result.failures:
                self.stream.write('F')

            for f in test_result.errors:
                self.stream.write('E')

            for f in test_result.skipped:
                self.stream.write('s')

            for f in test_result.expectedFailures:
                self.stream.write('x')

            for f in test_result.unexpectedSuccesses:
                self.stream.write('u')


class ParallelRunner(DjangoTestSuiteRunner):
    def run_suite(self, suite, **kwargs):
        return ParallelTestRunner(failfast=self.failfast).run(suite)
