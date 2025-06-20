import sys
import logging
import warnings
import traceback
import functools
from dataclasses import dataclass
from selenium.webdriver.common.bidi.cdp import CdpSession
from typing import (
	Any,
	Callable,
	Literal,
	Optional,
	TYPE_CHECKING
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools


def warn_if_active(func: Callable) -> Callable:
	"""
	Decorator to warn if DevTools operations are attempted while DevTools is active.

	This decorator is used to wrap methods in the DevTools class that should not be called
	while the DevTools event handler context manager is active. It checks the `is_active` flag
	of the DevTools instance. If DevTools is active, it issues a warning; otherwise, it proceeds
	to execute the original method.

	Args:
		func (Callable): The function to be wrapped. This should be a method of the DevTools class.

	Returns:
		Callable: The wrapped function. When called, it will check if DevTools is active and either
				  execute the original function or issue a warning.
	"""
	
	@functools.wraps(func)
	def wrapper(self: "DevTools", *args, **kwargs):
		if self.is_active:
			warnings.warn("DevTools is active. Exit dev_tools context before changing settings.")
		
		return func(self, *args, **kwargs)
	
	return wrapper


def log_on_error(func: Callable) -> Callable:
	"""
	Decorator to log any exceptions that occur during the execution of the decorated function.

	This decorator wraps a function and executes it within a try-except block.
	If an exception is raised during the function's execution, it logs the full traceback
	using the logging.ERROR level and then returns None. If no exception occurs, it returns the result of the function as usual.

	Args:
		func (Callable): The function to be decorated.

	Returns:
		Callable: The wrapped function. Returns the result of the decorated function if execution is successful, otherwise returns None if an exception occurs.
	"""

	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		try:
			return func(*args, **kwargs)
		except (Exception,):
			log_error()
			return None
	
	return wrapper


class ExceptionThrown:
	def __init__(self, exception: Exception):
		self.exception = exception


def log_error():
	exception_type, exception_value, exception_traceback = sys.exc_info()
	error = "".join(
			traceback.format_exception(exception_type, exception_value, exception_traceback)
	)
	
	logging.log(logging.ERROR, error)


@dataclass
class TargetData:
	cdp_session: Optional[CdpSession] = None
	target_id: Optional[str] = None
	type_: Optional[str] = None
	title: Optional[str] = None
	url: Optional[str] = None
	attached: Optional[bool] = None
	
	def to_dict(self) -> dict[str, Any]:
		return {
			"cdp_session": self.cdp_session,
			"target_id": self.target_id,
			"type": self.type_,
			"title": self.title,
			"url": self.url,
		}


async def execute_cdp_command(
		self: "DevTools",
		target_data: TargetData,
		error_mode: Literal["raise", "log", "pass"],
		function: Callable,
		*args,
		**kwargs
) -> Any:
	try:
		return await target_data.cdp_session.execute(function(*args, **kwargs))
	except (Exception,) as error:
		if error_mode == "raise":
			raise error
		elif error_mode == "log":
			await self._log_error(target_data=target_data)
			log_error()
	
			return ExceptionThrown(error)
		elif error_mode == "pass":
			return ExceptionThrown(error)
	
		raise ValueError(f"Wrong error_mode: {error_mode}. Expected: 'raise', 'log', 'pass'.")
