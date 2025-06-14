from selenium.webdriver.common.bidi.cdp import CdpSession
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


class AbstractEvent(TypedDict):
	"""
	A dictionary representing the configuration for a CDP event listener.

	This structure defines all the necessary components to listen for and handle
	a specific Chrome DevTools Protocol (CDP) event.

	Attributes:
		class_to_use_path (str): The dot-separated path to the CDP event class (e.g., "fetch.RequestPaused").
		listen_buffer_size (int): The buffer size for the event listener channel.
		handle_function (Callable): The asynchronous function to execute when an event is received.
		callbacks (TypedDict): A dictionary of callback functions and settings specific to the event handler.
		on_error (Optional[Callable]): An optional function to call if an error occurs during event handling.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: Callable[["DevTools", CdpSession, Any, Any], Awaitable[None]]
	callbacks: TypedDict
	on_error: Optional[Callable[["DevTools", Any, Exception], None]]
