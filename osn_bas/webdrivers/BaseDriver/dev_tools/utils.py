import sys
import logging
import warnings
import traceback
import functools
from typing import Callable, Literal
from osn_bas.webdrivers.BaseDriver.dev_tools.errors import (
	WrongHandlerSettingsError,
	WrongHandlerSettingsTypeError
)


def warn_if_active(func: Callable) -> Callable:
	"""
	Decorator to warn if DevTools operations are attempted while DevTools is active.

	This decorator is used to wrap methods in the DevTools class that should not be called
	while the DevTools event handler context manager is active. It checks the `_is_active` flag
	of the DevTools instance. If DevTools is active, it issues a warning; otherwise, it proceeds
	to execute the original method.

	Args:
		func (Callable): The function to be wrapped. This should be a method of the DevTools class.

	Returns:
		Callable: The wrapped function. When called, it will check if DevTools is active and either
				  execute the original function or issue a warning.
	"""
	
	@functools.wraps(func)
	def wrapper(self, *args, **kwargs):
		if not self._is_active:
			return func(self, *args, **kwargs)
		else:
			warnings.warn(
					message="DevTools is active. Exit dev_tools context before changing settings."
			)
	
	return wrapper


def validate_handler_settings(handler_settings: dict) -> Literal["class", "function"]:
	"""
	Validates the structure of event handler settings.

	This function checks if the provided dictionary of handler settings is correctly structured.
	It ensures that the settings are a dictionary and contains exactly one of the required keys:
	'class_to_use_path' or 'function_to_use_path'. If the settings are invalid, it raises a specific exception.

	Args:
		handler_settings (dict): The dictionary containing event handler settings to be validated.

	Returns:
		Literal["class", "function"]:
			- "class" if 'class_to_use_path' key is present.
			- "function" if 'function_to_use_path' key is present.

	Raises:
		WrongHandlerSettingsTypeError: If the handler_settings is not a dictionary.
		WrongHandlerSettingsError: If the handler_settings does not contain exactly one of the required keys.
	"""
	
	if not isinstance(handler_settings, dict):
		raise WrongHandlerSettingsTypeError(type(handler_settings))
	
	one_of_keys = ["class_to_use_path", "function_to_use_path"]
	if sum(1 for key in one_of_keys if handler_settings.get(key, None) is not None) != 1:
		raise WrongHandlerSettingsError(handler_settings, one_of_keys)
	
	if "class_to_use_path" in handler_settings:
		return "class"
	
	if "function_to_use_path" in handler_settings:
		return "function"


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
			exception_type, exception_value, exception_traceback = sys.exc_info()
			error = "".join(
					traceback.format_exception(exception_type, exception_value, exception_traceback)
			)
		
			logging.log(logging.ERROR, error)
		
			return None
	
	return wrapper
