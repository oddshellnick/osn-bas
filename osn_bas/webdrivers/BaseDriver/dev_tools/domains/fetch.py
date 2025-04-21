import base64
import logging
from typing import (
	Any,
	Awaitable,
	Callable,
	Literal,
	Optional,
	TYPE_CHECKING,
	TypeVar,
	TypedDict,
	Union
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools


class HeaderInstance(TypedDict):
	"""
	Type definition for header modification instructions.

	This TypedDict is used to specify how a header should be modified when intercepting network requests using DevTools.
	It includes the new value for the header and an instruction on how to apply the change (set, set if exists, remove).

	Attributes:
		value (Union[str, Any]): The new value to set for the header. Can be a string or any other type that can be converted to a string.
		instruction (Union[Literal["set", "set_exist", "remove"], Any]): Specifies the type of modification to apply to the header.

			- "set": Sets the header to the provided `value`, overwriting any existing value.
			- "set_exist": Sets the header to the provided `value` only if the header already exists in the request.
			- "remove": Removes the header from the request.
	"""
	
	value: Union[str, Any]
	instruction: Union[Literal["set", "set_exist", "remove"], Any]


class RequestPausedHandlerSettings(TypedDict):
	"""
	Configuration settings for handling Chrome DevTools Protocol 'fetch.requestPaused' events.

	This TypedDict defines the structure for configuring how intercepted network requests
	(paused via the Fetch domain) should be handled. It allows specifying conditions for handling
	(matching post data), modifications to make (headers), and custom logic to apply (handlers),
	as well as how to handle errors during processing.

	Attributes:
		class_to_use_path (str): The import path (e.g., 'selenium.webdriver.common.devtools.v125.fetch.RequestPaused')
								 to the specific DevTools event class this handler targets.
								 Used internally to route events correctly.
		listen_buffer_size (int): The size of the buffer for the Trio channel listening for these events.
								  Determines how many pending events can be queued before blocking.
		post_data_instances (Optional[Any]): Data structure(s) to match against the request's post data.
											 If provided and not None, the handlers might only be triggered
											 if the request's post data matches one of these instances,
											 depending on the custom handler logic. Defaults to None.
		headers_instances (Optional[Dict[str, HeaderInstance]]): Configuration for modifying request headers
																 based on predefined instructions. Keys are header names,
																 and values are `HeaderInstance` objects defining the modification.
																 Defaults to None.
		post_data_handler (post_data_handler_type): A callable (function or method) responsible for potentially
													modifying the request's post data. It receives the handler
													settings and the `fetch.RequestPaused` event object.
													It should return the modified post data (as a string) or None.
		headers_handler (headers_handler_type): A callable (function or method) responsible for potentially
												modifying the request's headers. It receives the handler settings,
												the CDP header entry class (e.g., `fetch.HeaderEntry`), and the
												`fetch.RequestPaused` event object. It should return a list of
												header dictionaries representing the final headers.
		on_error (on_error_type): A callable (function or method) that is invoked when an error
								  occurs within the `post_data_handler` or `headers_handler`
								  while processing an event. It receives the `DevTools` instance,
								  the event object, and the exception raised.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	post_data_instances: Optional[Any]
	headers_instances: Optional[dict[str, HeaderInstance]]
	post_data_handler: "post_data_handler_type"
	headers_handler: "headers_handler_type"
	on_error: "on_error_type"


def default_post_data_handler(handler_settings: RequestPausedHandlerSettings, event: Any) -> Optional[str]:
	"""
	Default handler for processing request post data when a 'requestPaused' event is triggered.
	This handler simply returns the original post data of the request without any modification.
	It serves as a fallback when no custom post data handler is provided in the settings.

	Args:
		handler_settings (RequestPausedHandlerSettings): The settings configured for handling 'requestPaused' events.
		event (Any): The 'fetch.RequestPaused' event object from DevTools, containing details about the paused request.

	Returns:
		Optional[str]: The original post data of the request, returned as is.
	"""
	
	post_data = event.request.post_data
	
	if post_data is None:
		return post_data
	
	return base64.b64encode(event.request.post_data.encode()).decode()


def default_on_error(self: "DevTools", event: Any, error: Exception) -> None:
	"""
	Default error handler for DevTools event listeners.

	This handler simply logs the caught exception at the ERROR level using the standard
	Python `logging` module. It does not prevent the listener loop from continuing
	to process subsequent events.

	Args:
		self (DevTools): The instance of the DevTools class managing the event.
		event (Any): The event object (or related context) that was being processed when the error occurred.
					 Could be a CDP event object like `fetch.RequestPaused`.
		error (Exception): The exception instance that was raised during event processing.
	"""
	
	logging.log(logging.ERROR, error)


def default_headers_handler(
		handler_settings: RequestPausedHandlerSettings,
		header_entry_class: "header_entry_type",
		event: Any
) -> list["header_entry_type"]:
	"""
	Default handler for processing and modifying request headers when a 'requestPaused' event is triggered.
	This handler modifies request headers based on the 'mode' specified in the handler settings
	(e.g., 'change', 'set', 'change_exist') and the header instances to be changed.

	Args:
		handler_settings (RequestPausedHandlerSettings): The settings configured for handling 'requestPaused' events,
			including the modification mode and header instances.
		header_entry_class (header_entry_type): The class for header entry from the DevTools protocol, e.g., `fetch.HeaderEntry`.
		event (Any): The 'fetch.RequestPaused' event object from DevTools, containing details about the paused request, including its headers.

	Returns:
		list[header_entry_type]: A list of header entries, each an instance of `header_entry_class`, representing the modified headers,
			ready to be sent back to DevTools to continue the request.
	"""
	
	headers = {name: value for name, value in event.request.headers.items()}
	
	for name, instance in handler_settings["headers_instances"].items():
		value = instance["value"]
		instruction = instance["instruction"]
	
		if instruction == "set":
			headers[name] = value
			continue
	
		if instruction == "set_exist":
			if name in headers:
				headers[name] = value
	
			continue
	
		if instruction == "remove":
			if name in headers:
				headers.pop(name)
	
			continue
	
	return [
		header_entry_class(name=name, value=value)
		for name, value in headers.items()
	]


post_data_handler_type = Callable[
	[RequestPausedHandlerSettings, Any],
	Union[Optional[str], Awaitable[Optional[str]]]
]
headers_handler_type = Callable[
	[RequestPausedHandlerSettings, type, Any],
	Union[list[Any], Awaitable[list[Any]]]
]
on_error_type = Callable[["DevTools", Any, Exception], None]
header_entry_type = TypeVar("header_entry_type")
