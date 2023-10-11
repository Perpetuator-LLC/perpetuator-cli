import argparse


class TestExpectedError(ValueError):
    pass


def assert_raises(this, func, args, regex_match=None):
    try:
        expected_exception = TestExpectedError
        with this.assertRaises(expected_exception,
                               msg=f"Test failed due to unexpected exception type, was expecting: {expected_exception}") as cm:
            func(TestArgParserWithErrorRaises, args)
    except Exception as e:
        this.fail(
            f"Test failed due to unexpected exception type: {type(e).__name__}, was expecting: {expected_exception}. Exception message: {str(e)}")
    if regex_match is not None:
        this.assertRegex(str(cm.exception), regex_match)


class TestArgParserWithErrorRaises(argparse.ArgumentParser):
    def error(self, message):
        """
        Override the error method to raise a TestExpectedError instead of exiting
        :param message: Error message
        :return:
        """
        raise TestExpectedError(message)
