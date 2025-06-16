import trio
from dataclasses import dataclass
from selenium.webdriver.common.bidi.cdp import CdpSession
from typing import (
	Any,
	Awaitable,
	Callable,
	Literal,
	Optional,
	TYPE_CHECKING,
	TypedDict
)
from osn_bas.webdrivers.BaseDriver.dev_tools.domains_default.fetch import (
	auth_required_choose_func,
	request_paused_choose_func
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools


class _FetchEnableKwargs(TypedDict, total=False):
	"""
	Internal TypedDict for keyword arguments to enable the Fetch domain.

	Attributes:
		patterns (Optional[list[Any]]): A list of request patterns to intercept.
		handle_auth_requests (Optional[bool]): Whether to intercept authentication requests.
	"""
	
	patterns: Optional[list[Any]]
	handle_auth_requests: Optional[bool]


class ParameterHandler(TypedDict):
	"""
	A dictionary defining a parameter handler function and its instances.

	Attributes:
		func (parameter_handler_type): The handler function to be executed.
		instances (Any): The data or configuration to be passed to the handler function.
	"""
	
	func: "parameter_handler_type"
	instances: Any


class _ContinueWithAuthHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'continueWithAuth' action.

	Attributes:
		response (ParameterHandler): Handler for the auth challenge response.
		username (Optional[ParameterHandler]): Handler for providing the username.
		password (Optional[ParameterHandler]): Handler for providing the password.
	"""
	
	response: ParameterHandler
	username: Optional[ParameterHandler]
	password: Optional[ParameterHandler]


@dataclass
class ContinueWithAuthHandlersSettings:
	"""
	Configuration for handlers that provide authentication credentials.

	Attributes:
		response (ParameterHandler): Handler for the auth challenge response.
		username (Optional[ParameterHandler]): Handler for providing the username. Defaults to None.
		password (Optional[ParameterHandler]): Handler for providing the password. Defaults to None.
	"""
	
	response: ParameterHandler
	username: Optional[ParameterHandler] = None
	password: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _ContinueWithAuthHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueWithAuthHandlers(
				response=self.response,
				username=self.username,
				password=self.password,
		)


async def _build_kwargs_from_handlers_func(
		self: "DevTools",
		handlers: dict[str, Optional[ParameterHandler]],
		event: Any
) -> dict[str, Any]:
	"""
	Asynchronously builds a dictionary of arguments by executing multiple handlers.

	This function runs multiple parameter handlers concurrently and aggregates their
	results into a single `kwargs` dictionary.

	Args:
		self (DevTools): The DevTools instance.
		handlers (dict[str, Optional[ParameterHandler]]): A dictionary of handlers to execute.
		event (Any): The CDP event that triggered the handlers.

	Returns:
		dict[str, Any]: A dictionary of keyword arguments built from the handlers' outputs.
	"""
	
	kwargs = {"request_id": event.request_id}
	
	kwargs_ready_events: list[trio.Event] = []
	
	for handler_name, handler_settings in handlers.items():
		if handler_settings is not None:
			kwargs_ready_event = trio.Event()
			kwargs_ready_events.append(kwargs_ready_event)
	
			self._nursery_object.start_soon(
					handler_settings["func"],
					self,
					kwargs_ready_event,
					handler_settings["instances"],
					event,
					kwargs
			)
	
	for kwargs_ready_event in kwargs_ready_events:
		await kwargs_ready_event.wait()
	
	return kwargs


class _ContinueWithAuth(TypedDict):
	"""
	Internal TypedDict for the 'continueWithAuth' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		handlers (_ContinueWithAuthHandlers): Handlers for authentication parameters.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	handlers: _ContinueWithAuthHandlers


@dataclass
class ContinueWithAuthSettings:
	"""
	Settings for continuing a request that requires authentication.

	Attributes:
		auth_challenge_response (ContinueWithAuthHandlersSettings): Settings for the handlers that provide authentication credentials.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
	"""
	
	auth_challenge_response: ContinueWithAuthHandlersSettings
	response_handle_func: "response_handle_func_type" = None
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueWithAuth:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueWithAuth(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				handlers=self.auth_challenge_response.to_dict(),
		)


class _AuthRequiredCallbacks(TypedDict):
	"""
	Internal TypedDict for callbacks of the 'AuthRequired' event.

	Attributes:
		choose_func (auth_required_choose_func_type): Function to decide the action to take.
		continue_with_auth (Optional[_ContinueWithAuth]): Configuration for the 'continueWithAuth' action.
	"""
	
	choose_func: "auth_required_choose_func_type"
	continue_with_auth: Optional[_ContinueWithAuth]


@dataclass
class AuthRequiredCallbacksSettings:
	"""
	Configuration for callbacks that handle authentication-required events.

	Attributes:
		choose_func (auth_required_choose_func_type): A function that decides which action to take. Defaults to `auth_required_choose_func`.
		continue_with_auth (Optional[ContinueWithAuthSettings]): Settings for the 'continueWithAuth' action. Defaults to None.
	"""
	
	choose_func: "auth_required_choose_func_type" = auth_required_choose_func
	continue_with_auth: Optional[ContinueWithAuthSettings] = None
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _AuthRequiredCallbacks:
		"""Converts the settings object to its dictionary representation."""
		
		return _AuthRequiredCallbacks(
				choose_func=self.choose_func,
				continue_with_auth=self.continue_with_auth.to_dict()
				if self.continue_with_auth is not None
				else None,
		)


class _AuthRequired(TypedDict):
	"""
	Internal TypedDict representing the complete configuration for an 'AuthRequired' event listener.

	Attributes:
		class_to_use_path (str): Path to the CDP event class.
		listen_buffer_size (int): Buffer size for the listener channel.
		handle_function (handle_auth_required_func_type): The main handler function for the event.
		callbacks (_AuthRequiredCallbacks): Callbacks specific to this event.
		on_error (Optional[on_error_type]): Function to call on error.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: "handle_auth_required_func_type"
	callbacks: _AuthRequiredCallbacks
	on_error: Optional["on_error_type"]


async def _handle_auth_required(
		self: "DevTools",
		cdp_session: CdpSession,
		handler_settings: _AuthRequired,
		event: Any
):
	"""
	Handles the 'fetch.AuthRequired' event.

	This function determines which action to take based on the `choose_func` and
	executes the corresponding CDP command with arguments built by the handlers.

	Args:
		self (DevTools): The DevTools instance.
		cdp_session (CdpSession): The active CDP session.
		handler_settings (_AuthRequired): The settings for this handler.
		event (Any): The 'fetch.AuthRequired' event object.
	"""
	
	chosen_func_names = handler_settings["callbacks"]["choose_func"](self, event)
	
	for func_name in chosen_func_names:
		chosen_func = handler_settings["callbacks"][func_name]
		kwargs = await chosen_func["kwargs_func"](self, chosen_func["handlers"], event)
		cache_func = chosen_func["response_handle_func"]
	
		try:
			response = await cdp_session.execute(self.get_devtools_object(f"fetch.{func_name}")(**kwargs))
	
			if cache_func is not None:
				self._nursery_object.start_soon(cache_func, self, response)
		except (Exception,) as error:
			on_error = handler_settings["on_error"]
	
			if on_error is not None:
				on_error(self, event, error)


@dataclass
class AuthRequiredSettings:
	"""
	Settings for handling the 'fetch.AuthRequired' event.

	Attributes:
		callbacks (AuthRequiredCallbacksSettings): Configuration for the event's callbacks.
		listen_buffer_size (int): The buffer size for the event listener channel. Defaults to 10.
		on_error (Optional[on_error_type]): An optional function to call on error. Defaults to None.
	"""
	
	callbacks: AuthRequiredCallbacksSettings
	listen_buffer_size: int = 10
	on_error: Optional["on_error_type"] = None
	
	@property
	def handle_function(self) -> "handle_auth_required_func_type":
		"""Returns the main handler function for the event."""
		
		return _handle_auth_required
	
	@property
	def class_to_use_path(self) -> str:
		"""Returns the path to the CDP event class."""
		
		return "fetch.AuthRequired"
	
	def to_dict(self) -> _AuthRequired:
		"""Converts the settings object to its dictionary representation."""
		
		return _AuthRequired(
				class_to_use_path=self.class_to_use_path,
				listen_buffer_size=self.listen_buffer_size,
				handle_function=self.handle_function,
				callbacks=self.callbacks.to_dict(),
				on_error=self.on_error,
		)


class _ContinueResponseHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'continueResponse' action.

	Attributes:
		response_code (Optional[ParameterHandler]): Handler for the HTTP response code.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase.
		response_headers (Optional[ParameterHandler]): Handler for the response headers.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers.
	"""
	
	response_code: Optional[ParameterHandler]
	response_phrase: Optional[ParameterHandler]
	response_headers: Optional[ParameterHandler]
	binary_response_headers: Optional[ParameterHandler]


class _ContinueResponse(TypedDict):
	"""
	Internal TypedDict for the 'continueResponse' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		handlers (_ContinueResponseHandlers): Handlers for response parameters.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	handlers: _ContinueResponseHandlers


class _FulfillRequestHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'fulfillRequest' action.

	Attributes:
		response_code (ParameterHandler): Handler for the HTTP response code.
		response_headers (Optional[ParameterHandler]): Handler for the response headers.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers.
		body (Optional[ParameterHandler]): Handler for the response body.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase.
	"""
	
	response_code: ParameterHandler
	response_headers: Optional[ParameterHandler]
	binary_response_headers: Optional[ParameterHandler]
	body: Optional[ParameterHandler]
	response_phrase: Optional[ParameterHandler]


class _FulfillRequest(TypedDict):
	"""
	Internal TypedDict for the 'fulfillRequest' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		handlers (_FulfillRequestHandlers): Handlers for mock response parameters.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	handlers: _FulfillRequestHandlers


class _FailRequestHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'failRequest' action.

	Attributes:
		error_reason (ParameterHandler): Handler for providing the network error reason.
	"""
	
	error_reason: ParameterHandler


class _FailRequest(TypedDict):
	"""
	Internal TypedDict for the 'failRequest' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		handlers (_FailRequestHandlers): Handlers for the error reason.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	handlers: _FailRequestHandlers


class _ContinueRequestHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'continueRequest' action.

	Attributes:
		url (Optional[ParameterHandler]): Handler for modifying the request URL.
		method (Optional[ParameterHandler]): Handler for modifying the HTTP method.
		post_data (Optional[ParameterHandler]): Handler for modifying the request's post data.
		headers (Optional[ParameterHandler]): Handler for modifying the request headers.
		intercept_response (Optional[ParameterHandler]): Handler for setting response interception behavior.
	"""
	
	url: Optional[ParameterHandler]
	method: Optional[ParameterHandler]
	post_data: Optional[ParameterHandler]
	headers: Optional[ParameterHandler]
	intercept_response: Optional[ParameterHandler]


class _ContinueRequest(TypedDict):
	"""
	Internal TypedDict for the 'continueRequest' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		handlers (_ContinueRequestHandlers): Handlers for request parameters.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	handlers: _ContinueRequestHandlers


class _RequestPausedCallbacks(TypedDict):
	"""
	Internal TypedDict for callbacks of the 'RequestPaused' event.

	Attributes:
		choose_func (request_paused_choose_func_type): Function to decide which action to take.
		continue_request (Optional[_ContinueRequest]): Configuration for the 'continueRequest' action.
		fail_request (Optional[_FailRequest]): Configuration for the 'failRequest' action.
		fulfill_request (Optional[_FulfillRequest]): Configuration for the 'fulfillRequest' action.
		continue_response (Optional[_ContinueResponse]): Configuration for the 'continueResponse' action.
	"""
	
	choose_func: "request_paused_choose_func_type"
	continue_request: Optional[_ContinueRequest]
	fail_request: Optional[_FailRequest]
	fulfill_request: Optional[_FulfillRequest]
	continue_response: Optional[_ContinueResponse]


class _RequestPaused(TypedDict):
	"""
	Internal TypedDict representing the complete configuration for a 'RequestPaused' event listener.

	Attributes:
		class_to_use_path (str): Path to the CDP event class.
		listen_buffer_size (int): Buffer size for the listener channel.
		handle_function (handle_request_paused_func_type): The main handler function for the event.
		callbacks (_RequestPausedCallbacks): Callbacks specific to this event.
		on_error (Optional[on_error_type]): Function to call on error.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: "handle_request_paused_func_type"
	callbacks: _RequestPausedCallbacks
	on_error: Optional["on_error_type"]


async def _handle_request_paused(
		self: "DevTools",
		cdp_session: CdpSession,
		handler_settings: _RequestPaused,
		event: Any
):
	"""
	Handles the 'fetch.RequestPaused' event.

	This function determines which action to take based on the `choose_func` and
	executes the corresponding CDP command with arguments built by the handlers.

	Args:
		self (DevTools): The DevTools instance.
		cdp_session (CdpSession): The active CDP session.
		handler_settings (_RequestPaused): The settings for this handler.
		event (Any): The 'fetch.RequestPaused' event object.
	"""
	
	chosen_func_names = handler_settings["callbacks"]["choose_func"](self, event)
	
	for func_name in chosen_func_names:
		chosen_func = handler_settings["callbacks"][func_name]
		kwargs = await chosen_func["kwargs_func"](self, chosen_func["handlers"], event)
		cache_func = chosen_func["response_handle_func"]
	
		try:
			response = await cdp_session.execute(self.get_devtools_object(f"fetch.{func_name}")(**kwargs))
	
			if cache_func is not None:
				self._nursery_object.start_soon(cache_func, self, response)
		except (Exception,) as error:
			on_error = handler_settings["on_error"]
	
			if on_error is not None:
				on_error(self, event, error)


@dataclass
class ContinueResponseHandlersSettings:
	"""
	Configuration for handlers that modify a response before it continues.

	Attributes:
		response_code (Optional[ParameterHandler]): Handler for the HTTP response code.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase.
		response_headers (Optional[ParameterHandler]): Handler for the response headers.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers.
	"""
	
	response_code: Optional[ParameterHandler] = None
	response_phrase: Optional[ParameterHandler] = None
	response_headers: Optional[ParameterHandler] = None
	binary_response_headers: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _ContinueResponseHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueResponseHandlers(
				response_code=self.response_code,
				response_phrase=self.response_phrase,
				response_headers=self.response_headers,
				binary_response_headers=self.binary_response_headers
		)


@dataclass
class ContinueResponseSettings:
	"""
	Settings for the 'continueResponse' action for a paused request.

	Attributes:
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
		handlers (ContinueResponseHandlersSettings): Configuration for the response parameter handlers.
	"""
	
	response_handle_func: "response_handle_func_type" = None
	handlers: ContinueResponseHandlersSettings = ContinueResponseHandlersSettings()
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueResponse:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueResponse(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				handlers=self.handlers.to_dict(),
		)


@dataclass
class FulfillRequestHandlersSettings:
	"""
	Configuration for handlers that provide a mock response to a request.

	Attributes:
		response_code (ParameterHandler): Handler for the HTTP response code.
		response_headers (Optional[ParameterHandler]): Handler for the response headers.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers.
		body (Optional[ParameterHandler]): Handler for the response body.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase.
	"""
	
	response_code: ParameterHandler
	response_headers: Optional[ParameterHandler] = None
	binary_response_headers: Optional[ParameterHandler] = None
	body: Optional[ParameterHandler] = None
	response_phrase: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _FulfillRequestHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _FulfillRequestHandlers(
				response_code=self.response_code,
				response_headers=self.response_headers,
				binary_response_headers=self.binary_response_headers,
				body=self.body,
				response_phrase=self.response_phrase,
		)


@dataclass
class FulfillRequestSettings:
	"""
	Settings for the 'fulfillRequest' action for a paused request.

	Attributes:
		handlers (FulfillRequestHandlersSettings): Configuration for the mock response parameter handlers.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
	"""
	
	handlers: FulfillRequestHandlersSettings
	response_handle_func: "response_handle_func_type" = None
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _FulfillRequest:
		"""Converts the settings object to its dictionary representation."""
		
		return _FulfillRequest(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				handlers=self.handlers.to_dict(),
		)


@dataclass
class FailRequestHandlersSettings:
	"""
	Configuration for handlers that specify the reason for failing a request.

	Attributes:
		error_reason (ParameterHandler): Handler for providing the network error reason.
	"""
	
	error_reason: ParameterHandler
	
	def to_dict(self) -> _FailRequestHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _FailRequestHandlers(error_reason=self.error_reason)


@dataclass
class FailRequestSettings:
	"""
	Settings for the 'failRequest' action for a paused request.

	Attributes:
		handlers (FailRequestHandlersSettings): Configuration for the error reason handler.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
	"""
	
	handlers: FailRequestHandlersSettings
	response_handle_func: "response_handle_func_type" = None
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _FailRequest:
		"""Converts the settings object to its dictionary representation."""
		
		return _FailRequest(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				handlers=self.handlers.to_dict(),
		)


@dataclass
class ContinueRequestHandlersSettings:
	"""
	Configuration for handlers that modify a request before it continues.

	Attributes:
		url (Optional[ParameterHandler]): Handler for modifying the request URL.
		method (Optional[ParameterHandler]): Handler for modifying the HTTP method.
		post_data (Optional[ParameterHandler]): Handler for modifying the request's post data.
		headers (Optional[ParameterHandler]): Handler for modifying the request headers.
		intercept_response (Optional[ParameterHandler]): Handler for setting response interception behavior.
	"""
	
	url: Optional[ParameterHandler] = None
	method: Optional[ParameterHandler] = None
	post_data: Optional[ParameterHandler] = None
	headers: Optional[ParameterHandler] = None
	intercept_response: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _ContinueRequestHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueRequestHandlers(
				url=self.url,
				method=self.method,
				post_data=self.post_data,
				headers=self.headers,
				intercept_response=self.intercept_response,
		)


@dataclass
class ContinueRequestSettings:
	"""
	Settings for the 'continueRequest' action for a paused request.

	Attributes:
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
		handlers (ContinueRequestHandlersSettings): Configuration for the request parameter handlers.
	"""
	
	response_handle_func: "response_handle_func_type" = None
	handlers: ContinueRequestHandlersSettings = ContinueRequestHandlersSettings()
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueRequest:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueRequest(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				handlers=self.handlers.to_dict(),
		)


@dataclass
class RequestPausedCallbacksSettings:
	"""
	Configuration for callbacks that handle paused request events.

	Attributes:
		choose_func (request_paused_choose_func_type): A function that decides which action to take.
		continue_request (Optional[ContinueRequestSettings]): Settings for the 'continueRequest' action.
		fail_request (Optional[FailRequestSettings]): Settings for the 'failRequest' action.
		fulfill_request (Optional[FulfillRequestSettings]): Settings for the 'fulfillRequest' action.
		continue_response (Optional[ContinueResponseSettings]): Settings for the 'continueResponse' action.
	"""
	
	choose_func: "request_paused_choose_func_type" = request_paused_choose_func
	continue_request: Optional[ContinueRequestSettings] = None
	fail_request: Optional[FailRequestSettings] = None
	fulfill_request: Optional[FulfillRequestSettings] = None
	continue_response: Optional[ContinueResponseSettings] = None
	
	def to_dict(self) -> _RequestPausedCallbacks:
		"""Converts the settings object to its dictionary representation."""
		
		return _RequestPausedCallbacks(
				choose_func=self.choose_func,
				continue_request=self.continue_request.to_dict()
				if self.continue_request
				else None,
				fail_request=self.fail_request.to_dict()
				if self.fail_request
				else None,
				fulfill_request=self.fulfill_request.to_dict()
				if self.fulfill_request
				else None,
				continue_response=self.continue_response.to_dict()
				if self.continue_response
				else None,
		)


@dataclass
class RequestPausedSettings:
	"""
	Settings for handling the 'fetch.RequestPaused' event.

	Attributes:
		listen_buffer_size (int): The buffer size for the event listener channel.
		callbacks (RequestPausedCallbacksSettings): Configuration for the event's callbacks.
		on_error (Optional[on_error_type]): An optional function to call on error.
	"""
	
	listen_buffer_size: int = 50
	callbacks: RequestPausedCallbacksSettings = RequestPausedCallbacksSettings()
	on_error: Optional["on_error_type"] = None
	
	@property
	def handle_function(self) -> "handle_request_paused_func_type":
		"""Returns the main handler function for the event."""
		
		return _handle_request_paused
	
	@property
	def class_to_use_path(self) -> str:
		"""Returns the path to the CDP event class."""
		
		return "fetch.RequestPaused"
	
	def to_dict(self) -> _RequestPaused:
		"""Converts the settings object to its dictionary representation."""
		
		return _RequestPaused(
				class_to_use_path=self.class_to_use_path,
				listen_buffer_size=self.listen_buffer_size,
				handle_function=self.handle_function,
				callbacks=self.callbacks.to_dict(),
				on_error=self.on_error,
		)


class _FetchHandlers(TypedDict):
	"""
	Internal TypedDict for all event handlers within the Fetch domain.

	Attributes:
		request_paused (Optional[_RequestPaused]): Configuration for the 'RequestPaused' event.
		auth_required (Optional[_AuthRequired]): Configuration for the 'AuthRequired' event.
	"""
	
	request_paused: Optional[_RequestPaused]
	auth_required: Optional[_AuthRequired]


@dataclass
class FetchHandlersSettings:
	"""
	Container for all handler settings within the Fetch domain.

	Attributes:
		request_paused (Optional[RequestPausedSettings]): Settings for the 'RequestPaused' event.
		auth_required (Optional[AuthRequiredSettings]): Settings for the 'AuthRequired' event.
	"""
	
	request_paused: Optional[RequestPausedSettings] = None
	auth_required: Optional[AuthRequiredSettings] = None
	
	def to_dict(self) -> _FetchHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _FetchHandlers(
				request_paused=self.request_paused.to_dict()
				if self.request_paused is not None
				else None,
				auth_required=self.auth_required.to_dict()
				if self.auth_required is not None
				else None,
		)


@dataclass
class FetchEnableKwargsSettings:
	"""
	Keyword arguments for enabling the Fetch domain.

	Attributes:
		patterns (Optional[list[Any]]): A list of request patterns to intercept. If None, all requests are intercepted.
		handle_auth_requests (Optional[bool]): Whether to intercept authentication requests.
	"""
	
	patterns: Optional[list[Any]] = None
	handle_auth_requests: Optional[bool] = None
	
	def to_dict(self) -> _FetchEnableKwargs:
		"""Converts the settings object to its dictionary representation."""
		
		kwargs = {}
		
		if self.patterns is not None:
			kwargs["patterns"] = self.patterns
		
		if self.handle_auth_requests is not None:
			kwargs["handle_auth_requests"] = self.handle_auth_requests
		
		return _FetchEnableKwargs(**kwargs)


class _Fetch(TypedDict):
	"""
	Internal TypedDict for the complete Fetch domain configuration.

	This structure is used internally by the DevTools manager to configure the
	Fetch domain, including how to enable/disable it and what event handlers to use.

	Attributes:
		name (str): The name of the domain ('fetch').
		enable_func_path (str): The path to the function to enable the domain.
		enable_func_kwargs (Optional[_FetchEnableKwargs]): Keyword arguments for the enable function.
		disable_func_path (str): The path to the function to disable the domain.
		handlers (_FetchHandlers): The configured event handlers for the domain.
	"""
	
	name: str
	enable_func_path: str
	enable_func_kwargs: Optional[_FetchEnableKwargs]
	disable_func_path: str
	handlers: _FetchHandlers


@dataclass
class FetchSettings:
	"""
	Top-level configuration for the Fetch domain.

	Attributes:
		enable_func_kwargs (Optional[FetchEnableKwargsSettings]): Keyword arguments for enabling the Fetch domain.
		handlers (FetchHandlersSettings): Container for all handler settings within the Fetch domain.
	"""
	
	enable_func_kwargs: Optional[FetchEnableKwargsSettings] = None
	handlers: FetchHandlersSettings = FetchHandlersSettings()
	
	@property
	def disable_func_path(self) -> str:
		"""Returns the path to the function to disable the domain."""
		
		return "fetch.disable"
	
	@property
	def enable_func_path(self) -> str:
		"""Returns the path to the function to enable the domain."""
		
		return "fetch.enable"
	
	@property
	def name(self) -> str:
		"""Returns the name of the domain."""
		
		return "fetch"
	
	def to_dict(self) -> _Fetch:
		"""Converts the settings object to its dictionary representation."""
		
		return _Fetch(
				name=self.name,
				enable_func_path=self.enable_func_path,
				enable_func_kwargs=self.enable_func_kwargs.to_dict()
				if self.enable_func_kwargs is not None
				else _FetchEnableKwargs(),
				disable_func_path=self.disable_func_path,
				handlers=self.handlers.to_dict(),
		)


build_kwargs_from_handlers_func_type = Callable[
	["DevTools", dict[str, Optional[ParameterHandler]], Any],
	Awaitable[dict[str, Any]]
]
request_paused_actions_literal = Literal[
	"continue_request",
	"fail_request",
	"fulfill_request",
	"continue_response"
]
auth_required_actions_literal = Literal["continue_with_auth"]
request_paused_choose_func_type = Callable[["DevTools", Any], list[request_paused_actions_literal]]
auth_required_choose_func_type = Callable[["DevTools", Any], list[auth_required_actions_literal]]
handle_request_paused_func_type = Callable[["DevTools", CdpSession, _RequestPaused, Any], Awaitable[None]]
handle_auth_required_func_type = Callable[["DevTools", CdpSession, _AuthRequired, Any], Awaitable[None]]
parameter_handler_type = Callable[["DevTools", trio.Event, Any, Any, dict[str, Any]], Awaitable[None]]
kwargs_output_type = Awaitable[dict[str, Any]]
response_handle_func_type = Optional[Callable[["DevTools", Any], Awaitable[Any]]]
on_error_type = Callable[["DevTools", Any, Exception], None]
