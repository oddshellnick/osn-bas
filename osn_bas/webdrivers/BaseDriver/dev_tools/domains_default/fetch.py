import sys
import trio
import logging
import traceback
from typing import (
	Any,
	Literal,
	TYPE_CHECKING,
	TypedDict,
	Union
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools
	from osn_bas.webdrivers.BaseDriver.dev_tools.domains.fetch import request_paused_actions_literal, auth_required_actions_literal


def request_paused_choose_func(self: "DevTools", event: Any) -> list["request_paused_actions_literal"]:
	"""
	Default function to decide which action to take when a request is paused.

	This function is the default implementation for the `choose_action_func` callback for the
	`request_paused` event. It always instructs the system to continue the request
	without modification by returning `["continue_request"]`.

	Args:
		self ("DevTools"): The DevTools instance.
		event (Any): The `fetch.RequestPaused` event object.

	Returns:
		list["request_paused_actions_literal"]: A list containing the action to perform, in this case, `["continue_request"]`.
	"""
	
	return ["continue_request"]


def on_error_func(self: "DevTools", event: Any, error: Exception) -> None:
	"""
	Default error handler for DevTools events.

	This function is called when an exception occurs during the processing of a DevTools event.
	It logs the error using the standard logging module at ERROR level.

	Args:
		self ("DevTools"): The DevTools instance.
		event (Any): The event object that was being processed when the error occurred.
		error (Exception): The exception that was raised.
	"""
	
	exception_type, exception_value, exception_traceback = sys.exc_info()
	error = "".join(
			traceback.format_exception(exception_type, exception_value, exception_traceback)
	)
	
	logging.log(logging.ERROR, error)


class HeaderInstance(TypedDict):
	"""
	Type definition for header modification instructions used by the `headers_handler`.

	This TypedDict is used to specify how a header should be modified when intercepting network requests using DevTools.
	It includes the new value for the header and an instruction on how to apply the change (set, set if exists, remove).

	Attributes:
		value (Union[str, Any]): The new value to set for the header. Can be a string or any other type that can be converted to a string for the header value.
		instruction (Literal["set", "set_exist", "remove"]): Specifies the type of modification to apply to the header.

			- "set": Sets the header to the provided `value`, overwriting any existing value or adding it if not present.
			- "set_exist": Sets the header to the provided `value` only if the header already exists in the request.
			- "remove": Removes the header from the request if it exists.
	"""
	
	value: Union[str, Any]
	instruction: Union[Literal["set", "set_exist", "remove"], Any]


async def headers_handler(
		self: "DevTools",
		ready_event: trio.Event,
		headers_instances: dict[str, HeaderInstance],
		event: Any,
		kwargs: dict[str, Any]
):
	"""
	Parameter handler function to modify request headers for a paused request.

	This handler is typically used with the `fetch.continueRequest` action. It receives
	a dictionary of desired header modifications (`headers_instances`) and applies them
	to the current request headers from the `event` object, then updates the `kwargs`
	dictionary with the modified headers list in the format expected by CDP.

	Args:
		self ("DevTools"): The DevTools instance.
		ready_event (trio.Event): An event to signal when the handler is complete.
		headers_instances (dict[str, HeaderInstance]): A dictionary where keys are header names (case-insensitive)
			and values are `HeaderInstance` dictionaries specifying the value and instruction.
		event (Any): The `fetch.RequestPaused` event object, containing the original request details.
		kwargs (dict[str, Any]): The dictionary of keyword arguments being built for the CDP command (e.g., `fetch.continueRequest`). This dictionary will be modified in place.
	"""
	
	header_entry_class = self.get_devtools_object("fetch.HeaderEntry")
	headers = {name: value for name, value in event.request.headers.items()}
	
	for name, instance in headers_instances.items():
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
	
	kwargs["headers"] = [
		header_entry_class(name=name, value=value)
		for name, value in headers.items()
	]
	
	ready_event.set()


def auth_required_choose_func(self: "DevTools", event: Any) -> list["auth_required_actions_literal"]:
	"""
	Default function to decide which action to take when authentication is required.

	This function is the default implementation for the `choose_action_func` callback for the
	`auth_required` event. It always instructs the system to proceed with authentication
	using `fetch.continueWithAuth` by returning `["continue_with_auth"]`. Specific
	authentication details (like username/password) would be provided by parameter
	handlers associated with the `continue_with_auth` action.

	Args:
		self ("DevTools"): The DevTools instance.
		event (Any): The `fetch.AuthRequired` event object.

	Returns:
		list["auth_required_actions_literal"]: A list containing the action to perform, in this case, `["continue_with_auth"]`.
	"""
	
	return ["continue_with_auth"]
