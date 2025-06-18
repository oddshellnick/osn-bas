import trio
from typing import (
	Any,
	Awaitable,
	Callable,
	Optional,
	TYPE_CHECKING,
	TypedDict
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools


class ParameterHandler(TypedDict):
	"""
	A dictionary defining a parameter handler function and its instances.

	Attributes:
		func (parameter_handler_type): The handler function to be executed. This function should modify a `kwargs` dictionary used for a CDP command.
		instances (Any): The data or configuration specific to this handler instance, passed to the `func`.
	"""
	
	func: "parameter_handler_type"
	instances: Any


kwargs_type = dict[str, Any]
kwargs_output_type = Awaitable[kwargs_type]
build_kwargs_from_handlers_func_type = Optional[
	Callable[["DevTools", dict[str, Optional[ParameterHandler]], Any], kwargs_output_type]
]
parameter_handler_type = Callable[["DevTools", trio.Event, Any, Any, dict[str, Any]], Awaitable[None]]
response_handle_func_type = Optional[Callable[["DevTools", Any], Awaitable[Any]]]
on_error_func_type = Optional[Callable[["DevTools", Any, Exception], None]]
