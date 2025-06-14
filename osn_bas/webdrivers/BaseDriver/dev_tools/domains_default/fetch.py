import logging
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

	This function is the default implementation for the `choose_func` callback for the
	`request_paused` event. It always instructs the system to continue the request.

	Args:
		self (DevTools): The DevTools instance.
		event (Any): The `request_paused` event object.

	Returns:
		list["request_paused_actions_literal"]: A list containing the action to perform, in this case, `["continue_request"]`.
	"""
	
	return ["continue_request"]


def on_error(self: "DevTools", event: Any, error: Exception) -> None:
	"""
	Default error handler for DevTools events.

	This function is called when an exception occurs during the processing of a DevTools event.
	It logs the error using the logging module.

	Args:
		self (DevTools): The DevTools instance.
		event (Any): The event object that caused the error.
		error (Exception): The exception that was raised.
	"""
	
	logging.log(logging.ERROR, error)


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


async def headers_handler(
		self: "DevTools",
		headers_instances: dict[str, HeaderInstance],
		event: Any,
		kwargs: dict[str, Any]
):
	"""
	Handles the modification of request headers based on a set of instructions.

	This function iterates through a dictionary of header modification instructions and
	applies them to the request's headers. The modified headers are then added to the
	`kwargs` dictionary, which is used to continue the request. This function modifies
	the `kwargs` dictionary in place.

	Args:
		self (DevTools): The DevTools instance.
		headers_instances (dict[str, HeaderInstance]): A dictionary where keys are header names and values are `HeaderInstance` objects defining the modifications.
		event (Any): The `request_paused` event object.
		kwargs (dict[str, Any]): A dictionary of arguments that will be passed to the CDP command (e.g., `continue_request`). This dictionary is modified in place.
	"""
	
	header_entry_class = self._get_devtools_object("fetch.HeaderEntry")
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


def auth_required_choose_func(self: "DevTools", event: Any) -> list["auth_required_actions_literal"]:
	"""
	Default function to decide which action to take when authentication is required.

	This function is the default implementation for the `choose_func` callback for the
	`auth_required` event. It always instructs the system to proceed with authentication.

	Args:
		self (DevTools): The DevTools instance.
		event (Any): The `auth_required` event object.

	Returns:
		list["auth_required_actions_literal"]: A list containing the action to perform, in this case, `["continue_with_auth"]`.
	"""
	
	return ["continue_with_auth"]
