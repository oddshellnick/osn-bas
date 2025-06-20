import trio
from osn_bas.webdrivers.BaseDriver.dev_tools.utils import log_error, TargetData
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


def request_paused_choose_func(self: "DevTools", target_data: TargetData, event: Any) -> list["request_paused_actions_literal"]:
	return ["continue_request"]


def on_error_func(self: "DevTools", target_data: TargetData, event: Any, error: Exception):
	log_error()


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
		target_data: TargetData,
		ready_event: trio.Event,
		headers_instances: dict[str, HeaderInstance],
		event: Any,
		kwargs: dict[str, Any]
):
	try:
		header_entry_class = await self.get_devtools_object("fetch.HeaderEntry")
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
	except (Exception,) as error:
		await self._log_error(target_data=target_data)
		raise error


def auth_required_choose_func(self: "DevTools", target_data: TargetData, event: Any) -> list["auth_required_actions_literal"]:
	return ["continue_with_auth"]
