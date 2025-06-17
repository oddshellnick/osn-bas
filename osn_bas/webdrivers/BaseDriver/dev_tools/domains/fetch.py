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


class _ContinueWithAuthParametersHandlers(TypedDict):
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
class ContinueWithAuthParameterHandlersSettings:
	response: ParameterHandler
	username: Optional[ParameterHandler] = None
	password: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _ContinueWithAuthParametersHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueWithAuthParametersHandlers(
				response=self.response,
				username=self.username,
				password=self.password,
		)


async def _build_kwargs_from_handlers_func(
		self: "DevTools",
		handlers: dict[str, Optional[ParameterHandler]],
		event: Any
) -> "kwargs_type":
	"""
	Asynchronously builds a dictionary of arguments by executing multiple handlers.

	This function runs multiple parameter handlers concurrently and aggregates their
	results into a single `kwargs` dictionary.

	Args:
		self (DevTools): The DevTools instance.
		handlers (dict[str, Optional[ParameterHandler]]): A dictionary of handlers to execute.
		event (Any): The CDP event that triggered the handlers.

	Returns:
		"kwargs_type": A dictionary of keyword arguments built from the handlers' outputs.
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
		parameters_handlers (_ContinueWithAuthParametersHandlers): Handlers for authentication parameters.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	parameters_handlers: _ContinueWithAuthParametersHandlers


@dataclass
class ContinueWithAuthSettings:
	"""
	Settings for continuing a request that requires authentication.

	Attributes:
		auth_challenge_response (ContinueWithAuthParameterHandlersSettings): Settings for the handlers that provide authentication credentials.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
	"""
	
	auth_challenge_response: ContinueWithAuthParameterHandlersSettings
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
				parameters_handlers=self.auth_challenge_response.to_dict(),
		)


class _AuthRequiredActions(TypedDict, total=False):
	continue_with_auth: Optional[_ContinueWithAuth]


@dataclass
class AuthRequiredActionsSettings:
	continue_with_auth: Optional[ContinueWithAuthSettings] = None
	
	def to_dict(self) -> _AuthRequiredActions:
		"""Converts the settings object to its dictionary representation."""
		
		return _AuthRequiredActions(
				continue_with_auth=self.continue_with_auth.to_dict()
				if self.continue_with_auth is not None
				else None,
		)


class _AuthRequiredActionsHandler(TypedDict):
	choose_action_func: "auth_required_choose_action_func_type"
	actions: _AuthRequiredActions


@dataclass
class AuthRequiredActionsHandlerSettings:
	choose_action_func: "auth_required_choose_action_func_type" = auth_required_choose_func
	actions: Optional[AuthRequiredActionsSettings] = AuthRequiredActionsSettings()
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _AuthRequiredActionsHandler:
		"""Converts the settings object to its dictionary representation."""
		
		return _AuthRequiredActionsHandler(
				choose_action_func=self.choose_action_func,
				actions=self.actions.to_dict(),
		)


class _AuthRequired(TypedDict):
	"""
	Internal TypedDict representing the complete configuration for an 'AuthRequired' event listener.

	Attributes:
		class_to_use_path (str): Path to the CDP event class.
		listen_buffer_size (int): Buffer size for the listener channel.
		handle_function (handle_auth_required_func_type): The main handler function for the event.
		actions_handler (_AuthRequiredActionsHandler): Callbacks specific to this event.
		on_error_func (on_error_type): Function to call on error.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: "handle_auth_required_func_type"
	actions_handler: _AuthRequiredActionsHandler
	on_error_func: "on_error_func_type"


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
	
	chosen_func_names = handler_settings["actions_handler"]["choose_action_func"](self, event)
	
	for func_name in chosen_func_names:
		chosen_func = handler_settings["actions_handler"]["actions"][func_name]
		kwargs = await chosen_func["kwargs_func"](self, chosen_func["parameters_handlers"], event)
		response_handle_func = chosen_func["response_handle_func"]
	
		try:
			response = await cdp_session.execute(self.get_devtools_object(f"fetch.{func_name}")(**kwargs))
	
			if response_handle_func is not None:
				self._nursery_object.start_soon(response_handle_func, self, response)
		except (Exception,) as error:
			on_error = handler_settings["on_error_func"]
	
			if on_error is not None:
				on_error(self, event, error)


@dataclass
class AuthRequiredSettings:
	"""
	Settings for handling the 'fetch.AuthRequired' event.

	Attributes:
		actions_handler (AuthRequiredActionsHandlerSettings): Configuration for the event's actions_handler.
		listen_buffer_size (int): The buffer size for the event listener channel. Defaults to 10.
		on_error_func (on_error_type): An optional function to call on error. Defaults to None.
	"""
	
	actions_handler: AuthRequiredActionsHandlerSettings
	listen_buffer_size: int = 10
	on_error_func: "on_error_func_type" = None
	
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
				actions_handler=self.actions_handler.to_dict(),
				on_error_func=self.on_error_func,
		)


class _ContinueResponseParametersHandlers(TypedDict):
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


class _ContinueResponseAction(TypedDict):
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	parameters_handlers: _ContinueResponseParametersHandlers


class _FulfillRequestParametersHandlers(TypedDict):
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


class _FulfillRequestAction(TypedDict):
	"""
	Internal TypedDict for the 'fulfillRequest' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_FulfillRequestParametersHandlers): Handlers for mock response parameters.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	parameters_handlers: _FulfillRequestParametersHandlers


class _FailRequestParametersHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'failRequest' action.

	Attributes:
		error_reason (ParameterHandler): Handler for providing the network error reason.
	"""
	
	error_reason: ParameterHandler


class _FailRequestAction(TypedDict):
	"""
	Internal TypedDict for the 'failRequest' action configuration.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_FailRequestParametersHandlers): Handlers for the error reason.
	"""
	
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	parameters_handlers: _FailRequestParametersHandlers


class _ContinueRequestParametersHandlers(TypedDict):
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


class _ContinueRequestAction(TypedDict):
	kwargs_func: "build_kwargs_from_handlers_func_type"
	response_handle_func: "response_handle_func_type"
	parameters_handlers: _ContinueRequestParametersHandlers


class _RequestPausedActions(TypedDict):
	continue_request: Optional[_ContinueRequestAction]
	fail_request: Optional[_FailRequestAction]
	fulfill_request: Optional[_FulfillRequestAction]
	continue_response: Optional[_ContinueResponseAction]


class _RequestPausedActionsHandler(TypedDict):
	choose_action_func: "request_paused_choose_action_func_type"
	actions: _RequestPausedActions


class _RequestPaused(TypedDict):
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: "handle_request_paused_func_type"
	actions_handler: _RequestPausedActionsHandler
	on_error_func: "on_error_func_type"


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
	
	chosen_actions_func_names = handler_settings["actions_handler"]["choose_action_func"](self, event)
	
	for action_func_name in chosen_actions_func_names:
		chosen_action_func = handler_settings["actions_handler"]["actions"][action_func_name]
		kwargs = await chosen_action_func["kwargs_func"](self, chosen_action_func["parameters_handlers"], event)
		response_handle_func = chosen_action_func["response_handle_func"]
	
		try:
			response = await cdp_session.execute(self.get_devtools_object(f"fetch.{action_func_name}")(**kwargs))
	
			if response_handle_func is not None:
				self._nursery_object.start_soon(response_handle_func, self, response)
		except (Exception,) as error:
			on_error = handler_settings["on_error_func"]
	
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
	
	def to_dict(self) -> _ContinueResponseParametersHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueResponseParametersHandlers(
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
		parameters_handlers (ContinueResponseHandlersSettings): Configuration for the response parameter handlers.
	"""
	
	response_handle_func: "response_handle_func_type" = None
	parameters_handlers: ContinueResponseHandlersSettings = ContinueResponseHandlersSettings()
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueResponseAction:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueResponseAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
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
	
	def to_dict(self) -> _FulfillRequestParametersHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _FulfillRequestParametersHandlers(
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
		parameters_handlers (FulfillRequestHandlersSettings): Configuration for the mock response parameter handlers.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
	"""
	
	parameters_handlers: FulfillRequestHandlersSettings
	response_handle_func: "response_handle_func_type" = None
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _FulfillRequestAction:
		"""Converts the settings object to its dictionary representation."""
		
		return _FulfillRequestAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
		)


@dataclass
class FailRequestHandlersSettings:
	"""
	Configuration for handlers that specify the reason for failing a request.

	Attributes:
		error_reason (ParameterHandler): Handler for providing the network error reason.
	"""
	
	error_reason: ParameterHandler
	
	def to_dict(self) -> _FailRequestParametersHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _FailRequestParametersHandlers(error_reason=self.error_reason)


@dataclass
class FailRequestSettings:
	"""
	Settings for the 'failRequest' action for a paused request.

	Attributes:
		parameters_handlers (FailRequestHandlersSettings): Configuration for the error reason handler.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the CDP command. Defaults to None.
	"""
	
	parameters_handlers: FailRequestHandlersSettings
	response_handle_func: "response_handle_func_type" = None
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _FailRequestAction:
		"""Converts the settings object to its dictionary representation."""
		
		return _FailRequestAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
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
	
	def to_dict(self) -> _ContinueRequestParametersHandlers:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueRequestParametersHandlers(
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
		parameters_handlers (ContinueRequestHandlersSettings): Configuration for the request parameter handlers.
	"""
	
	response_handle_func: "response_handle_func_type" = None
	parameters_handlers: ContinueRequestHandlersSettings = ContinueRequestHandlersSettings()
	
	@property
	def kwargs_func(self) -> "build_kwargs_from_handlers_func_type":
		"""Returns the function used to build keyword arguments."""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueRequestAction:
		"""Converts the settings object to its dictionary representation."""
		
		return _ContinueRequestAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
		)


@dataclass
class RequestPausedActionsSettings:
	continue_request: Optional[ContinueRequestSettings] = None
	fail_request: Optional[FailRequestSettings] = None
	fulfill_request: Optional[FulfillRequestSettings] = None
	continue_response: Optional[ContinueResponseSettings] = None
	
	def to_dict(self) -> _RequestPausedActions:
		"""Converts the settings object to its dictionary representation."""
		
		return _RequestPausedActions(
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
class RequestPausedActionsHandlerSettings:
	choose_action_func: "request_paused_choose_action_func_type" = request_paused_choose_func
	actions: RequestPausedActionsSettings = RequestPausedActionsSettings()
	
	def to_dict(self) -> _RequestPausedActionsHandler:
		"""Converts the settings object to its dictionary representation."""
		
		return _RequestPausedActionsHandler(
				choose_action_func=self.choose_action_func,
				actions=self.actions.to_dict(),
		)


@dataclass
class RequestPausedSettings:
	listen_buffer_size: int = 50
	actions_handler: RequestPausedActionsHandlerSettings = RequestPausedActionsHandlerSettings()
	on_error_func: "on_error_func_type" = None
	
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
				actions_handler=self.actions_handler.to_dict(),
				on_error_func=self.on_error_func,
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


kwargs_type = dict[str, Any]
kwargs_output_type = Awaitable[kwargs_type]
build_kwargs_from_handlers_func_type = Optional[
	Callable[["DevTools", dict[str, Optional[ParameterHandler]], Any], kwargs_output_type]
]
request_paused_actions_literal = Literal[
	"continue_request",
	"fail_request",
	"fulfill_request",
	"continue_response"
]
auth_required_actions_literal = Literal["continue_with_auth"]
request_paused_choose_action_func_type = Callable[["DevTools", Any], list[request_paused_actions_literal]]
auth_required_choose_action_func_type = Callable[["DevTools", Any], list[auth_required_actions_literal]]
handle_request_paused_func_type = Callable[["DevTools", CdpSession, _RequestPaused, Any], Awaitable[None]]
handle_auth_required_func_type = Callable[["DevTools", CdpSession, _AuthRequired, Any], Awaitable[None]]
parameter_handler_type = Callable[["DevTools", trio.Event, Any, Any, dict[str, Any]], Awaitable[None]]
response_handle_func_type = Optional[Callable[["DevTools", Any], Awaitable[Any]]]
on_error_func_type = Optional[Callable[["DevTools", Any, Exception], None]]
