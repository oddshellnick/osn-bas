import sys
from osn_bas.browsers_handler.types import Browser
from osn_bas.browsers_handler.windows import get_installed_browsers_win32


def get_installed_browsers() -> list[Browser]:
	"""
	Retrieves a list of installed browsers based on the operating system.

	This function acts as a platform dispatcher, calling the appropriate function to retrieve installed browsers based on the operating system.

	Returns:
		list[Browser]: A list of installed browsers, where each browser is represented by a `Browser` object.

	Raises:
		ValueError: If the platform is not supported.
	"""
	if sys.platform == "win32":
		return get_installed_browsers_win32()
	else:
		raise ValueError(f"Unsupported platform: {sys.platform}")
