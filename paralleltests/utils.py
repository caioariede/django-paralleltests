import os


def get_env_options():
    """
    Get test options from environment variables
    """
    args = []
    kwargs = {}

    if 'TEST_LABELS' in os.environ:
        args.extend(os.environ['TEST_LABELS'].split())

    kwargs.update({
        'testrunner': os.environ.get('TEST_RUNNER'),
    })

    return args, kwargs


def wrap_test_tuple(tupl):
    head, tail = tupl[0], list(tupl[1:])
    tail.insert(0, (head.__class__, head._testMethodName))
    return tail


def unwrap_test_tuple(tupl):
    (cls, method_name), tail = tupl[0], list(tupl[1:])
    tail.insert(0, cls(method_name))
    return tail


def wrap_result(result):
    result._original_stdout = None
    result._original_stderr = None

    result.errors = map(wrap_test_tuple, result.errors)
    result.failures = map(wrap_test_tuple, result.failures)
    result.skipped = map(wrap_test_tuple, result.skipped)
    result.expectedFailures = map(wrap_test_tuple, result.expectedFailures)
    result.unexpectedSuccesses = map(wrap_test_tuple,
                                     result.unexpectedSuccesses)


def unwrap_result(result):
    result.errors = map(unwrap_test_tuple, result.errors)
    result.failures = map(unwrap_test_tuple, result.failures)
    result.skipped = map(unwrap_test_tuple, result.skipped)
    result.expectedFailures = map(unwrap_test_tuple, result.expectedFailures)
    result.unexpectedSuccesses = map(unwrap_test_tuple,
                                     result.unexpectedSuccesses)
