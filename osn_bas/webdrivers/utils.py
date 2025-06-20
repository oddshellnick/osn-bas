import sys
import traceback


def get_traceback():
	exception_type, exception_value, exception_traceback = sys.exc_info()
	return "".join(
			traceback.format_exception(exception_type, exception_value, exception_traceback)
	)
