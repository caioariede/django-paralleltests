from __future__ import absolute_import

import unittest
import pickle
import warnings
import hashlib
import base64

from django.test.runner import DiscoverRunner
from django.conf import settings

from ..utils import wrap_result


class PickleTestRunner(object):
    resultclass = unittest.TestResult

    def __init__(self, failfast=False):
        self.failfast = failfast

    def _makeResult(self):
        return self.resultclass()

    def run(self, test):
        result = self._makeResult()
        unittest.registerResult(result)
        result.failfast = self.failfast
        self.run_test(test, result)
        return result

    def run_test(self, test, result):
        hash_ = '--- {}'.format(hashlib.sha1().hexdigest())
        self.output(hash_)
        with warnings.catch_warnings(record=True) as warnings_:
            test(result)
            self.output(self.serialize_result(result, warnings_))
        self.output(hash_)

    def serialize_result(self, result, warnings_):
        wrap_result(result)
        return base64.b64encode(pickle.dumps(result))

    def output(self, response):
        print(response)


class PickleRunner(DiscoverRunner):
    def run_suite(self, suite, **kwargs):
        return PickleTestRunner(failfast=self.failfast).run(suite)

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, *args, **kwargs):
        pass
