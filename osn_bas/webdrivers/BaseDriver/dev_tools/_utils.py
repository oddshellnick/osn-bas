import sys
import logging
import warnings
import traceback
import functools
from typing import (
	Any,
	Callable,
	Literal
)
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


def validate_handler_settings(handler_settings: dict[str, Any]) -> Literal["class", "function"]:
	"""
	Validates the structure and necessary keys of event handler settings.

	This function checks if the provided dictionary of handler settings is correctly structured
	for defining either a class-based or function-based event handler. It ensures that:

	1. The input is a dictionary (or mapping).
	2. It contains exactly one of the keys 'class_to_use_path' or 'function_to_use_path' with a non-None value.
	3. It contains the key 'listen_buffer_size'.

	Args:
		handler_settings (dict[str, Any]): The dictionary containing event handler settings to validate.
											  Expected keys depend on the handler type, but must include
											  'listen_buffer_size' and exactly one of 'class_to_use_path'
											  or 'function_to_use_path'.

	Returns:
		Literal["class", "function"]: Indicates the type of handler configuration identified:

			- "class" if 'class_to_use_path' key is present and valid according to the checks.
			- "function" if 'function_to_use_path' key is present and valid according to the checks.

	Raises:
		WrongHandlerSettingsTypeError: If `handler_settings` is not a dictionary or mapping-like object.
		WrongHandlerSettingsError: If `handler_settings` does not contain exactly one of the keys
								   'class_to_use_path' or 'function_to_use_path' with a non-None value.
		AttributeError: If the `handler_settings` dictionary is missing the required 'listen_buffer_size' key.
	"""
	
	if not isinstance(handler_settings, dict):
		raise WrongHandlerSettingsTypeError(type(handler_settings))
	
	one_of_keys = ["class_to_use_path", "function_to_use_path"]
	if sum(1 for key in one_of_keys if handler_settings.get(key, None) is not None) != 1:
		raise WrongHandlerSettingsError(handler_settings, one_of_keys)
	
	if "listen_buffer_size" not in handler_settings:
		raise AttributeError("Handler settings must contain 'listen_buffer_size' key.")
	
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
