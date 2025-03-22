import warnings
import functools
from typing import Callable


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
