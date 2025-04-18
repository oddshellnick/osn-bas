import base64
from typing import (
	Any,
	Awaitable,
	Callable,
	Literal,
	Optional,
	TypeVar,
	TypedDict,
	Union
)


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
	Settings for handling 'fetch.requestPaused' events.

	This TypedDict defines the configuration structure for handling 'fetch.requestPaused' events from DevTools.
	It includes settings for matching instances in post data, header modifications, and custom handler functions for post data and headers.

	Attributes:
		class_to_use_path (str): Path to the class in the DevTools API representing the 'RequestPaused' event.
			Used internally to correctly identify and process 'requestPaused' events.
		post_data_instances (Optional[Any]): Optional instances to match against request post data.
			If provided, the handler will only be triggered for requests whose post data matches one of these instances.
		headers_instances (Optional[dict[str, HeaderInstance]]): Optional dictionary of header modification instructions.
			Keys are header names, and values are `HeaderInstance` objects specifying how to modify each header.
		post_data_handler (post_data_handler_type): Handler function for processing request post data.
			This function is called when a 'requestPaused' event is intercepted, allowing for custom logic to modify the post data.
			It should take `RequestPausedHandlerSettings` and the event object as arguments and return the modified post data as a string or None.
		headers_handler (headers_handler_type): Handler function for processing request headers.
			Similar to `post_data_handler`, but for headers. It takes `RequestPausedHandlerSettings`, the header entry class from DevTools API,
			and the event object, and should return a list of modified header entries.
	"""
	
	class_to_use_path: str
	post_data_instances: Optional[Any]
	headers_instances: Optional[dict[str, HeaderInstance]]
	post_data_handler: "post_data_handler_type"
	headers_handler: "headers_handler_type"


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
header_entry_type = TypeVar("header_entry_type")
