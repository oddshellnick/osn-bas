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
from osn_bas.webdrivers.BaseDriver.dev_tools.domains.utils import (
	ParameterHandler,
	build_kwargs_from_handlers_func_type,
	kwargs_type,
	on_error_func_type,
	response_handle_func_type
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
	"""
	Settings for the handlers that provide authentication credentials when required.

	Attributes:
		response (ParameterHandler): Handler for the authentication challenge response. This handler determines the response type (e.g., default, custom credentials, or canceled).
		username (Optional[ParameterHandler]): Optional handler for providing the username if using custom credentials. Defaults to None.
		password (Optional[ParameterHandler]): Optional handler for providing the password if using custom credentials. Defaults to None.
	"""
	
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
) -> kwargs_type:
	"""
	Asynchronously builds a dictionary of arguments by executing multiple handlers.

	This function runs multiple parameter handlers concurrently within the DevTools nursery
	and aggregates their results into a single `kwargs` dictionary, which is then used
	to execute a CDP command.

	Args:
		self ("DevTools"): The DevTools instance managing the handlers and nursery.
		handlers (dict[str, Optional[ParameterHandler]]): A dictionary where keys are the parameter names (e.g., "url", "method") and values are `ParameterHandler` objects or None.
		event (Any): The CDP event object that triggered the execution (e.g., Fetch.RequestPaused, Fetch.AuthRequired).

	Returns:
		kwargs_type: A dictionary of keyword arguments built from the handlers' outputs, typically including the request/auth challenge ID and parameters modified by handlers.
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
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments for the `continueWithAuth` CDP command.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_ContinueWithAuthParametersHandlers): Handlers for authentication parameters.
	"""
	
	kwargs_func: build_kwargs_from_handlers_func_type
	response_handle_func: response_handle_func_type
	parameters_handlers: _ContinueWithAuthParametersHandlers


@dataclass
class ContinueWithAuthSettings:
	"""
	Settings for continuing a request that requires authentication using the `fetch.continueWithAuth` CDP command.

	Attributes:
		auth_challenge_response (ContinueWithAuthParameterHandlersSettings): Settings for the handlers that provide authentication credentials.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the `fetch.continueWithAuth` CDP command. Defaults to None.
	"""
	
	auth_challenge_response: ContinueWithAuthParameterHandlersSettings
	response_handle_func: response_handle_func_type = None
	
	@property
	def kwargs_func(self) -> build_kwargs_from_handlers_func_type:
		"""
		Returns the function used to build keyword arguments for the `continueWithAuth` command.

		Returns:
			build_kwargs_from_handlers_func_type: The internal function `_build_kwargs_from_handlers_func`.
		"""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueWithAuth:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_ContinueWithAuth: The dictionary representation suitable for internal use.
		"""
		
		return _ContinueWithAuth(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.auth_challenge_response.to_dict(),
		)


class _AuthRequiredActions(TypedDict, total=False):
	"""
	Internal TypedDict mapping action names for AuthRequired event to their configurations.

	Attributes:
		continue_with_auth (Optional[_ContinueWithAuth]): Configuration for the 'continueWithAuth' action.
	"""
	
	continue_with_auth: Optional[_ContinueWithAuth]


@dataclass
class AuthRequiredActionsSettings:
	"""
	Container for configurations of possible actions to take when authentication is required.

	Attributes:
		continue_with_auth (Optional[ContinueWithAuthSettings]): Settings for handling the authentication challenge using `fetch.continueWithAuth`. Defaults to None.
	"""
	
	continue_with_auth: Optional[ContinueWithAuthSettings] = None
	
	def to_dict(self) -> _AuthRequiredActions:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_AuthRequiredActions: The dictionary representation suitable for internal use.
		"""
		
		return _AuthRequiredActions(
				continue_with_auth=self.continue_with_auth.to_dict()
				if self.continue_with_auth is not None
				else None,
		)


class _AuthRequiredActionsHandler(TypedDict):
	"""
	Internal TypedDict for the actions handler configuration for the 'AuthRequired' event.

	Attributes:
		choose_action_func (auth_required_choose_action_func_type): A function that determines which actions (by name) should be executed for a given 'AuthRequired' event.
		actions (_AuthRequiredActions): A dictionary mapping action names to their full configurations.
	"""
	
	choose_action_func: "auth_required_choose_action_func_type"
	actions: _AuthRequiredActions


@dataclass
class AuthRequiredActionsHandlerSettings:
	"""
	Settings for handling the 'fetch.AuthRequired' event by choosing and executing specific actions.

	Attributes:
		choose_action_func (auth_required_choose_action_func_type): A function that takes the DevTools instance and the event object and returns a list of action names (Literals) to execute. Defaults to `auth_required_choose_func`.
		actions (AuthRequiredActionsSettings): Container for the configuration of the available actions. Defaults to an empty `AuthRequiredActionsSettings`.
	"""
	
	choose_action_func: "auth_required_choose_action_func_type" = auth_required_choose_func
	actions: AuthRequiredActionsSettings = AuthRequiredActionsSettings()
	
	@property
	def kwargs_func(self) -> build_kwargs_from_handlers_func_type:
		"""
		Returns the function used to build keyword arguments for the actions.

		Returns:
			build_kwargs_from_handlers_func_type: The internal function `_build_kwargs_from_handlers_func`.
		"""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _AuthRequiredActionsHandler:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_AuthRequiredActionsHandler: The dictionary representation suitable for internal use.
		"""
		
		return _AuthRequiredActionsHandler(
				choose_action_func=self.choose_action_func,
				actions=self.actions.to_dict(),
		)


class _AuthRequired(TypedDict):
	"""
	Internal TypedDict representing the complete configuration for an 'AuthRequired' event listener.

	This structure extends `AbstractEvent` with specifics for the Fetch.AuthRequired domain event.

	Attributes:
		class_to_use_path (str): Path to the CDP event class ("fetch.AuthRequired").
		listen_buffer_size (int): Buffer size for the listener channel.
		handle_function (handle_auth_required_func_type): The main handler function for the event (_handle_auth_required).
		actions_handler (_AuthRequiredActionsHandler): Callbacks and configurations for choosing and executing actions based on the event.
		on_error_func (on_error_func_type): Function to call on error during event handling.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: "handle_auth_required_func_type"
	actions_handler: _AuthRequiredActionsHandler
	on_error_func: on_error_func_type


async def _handle_auth_required(
		self: "DevTools",
		cdp_session: CdpSession,
		handler_settings: _AuthRequired,
		event: Any
):
	"""
	Handles the 'fetch.AuthRequired' event.

	This function determines which action to take based on the `choose_action_func` defined
	in the handler settings and executes the corresponding CDP command (e.g., `fetch.continueWithAuth`)
	with arguments built by the associated parameter handlers.

	Args:
		self ("DevTools"): The DevTools instance.
		cdp_session (CdpSession): The active CDP session where the event occurred.
		handler_settings (_AuthRequired): The configuration settings for this 'AuthRequired' event handler.
		event (Any): The 'fetch.AuthRequired' event object received from the CDP session.
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

	This dataclass allows configuring the listener for the 'AuthRequired' CDP event,
	including buffer size, the actions to take, and error handling.

	Attributes:
		actions_handler (AuthRequiredActionsHandlerSettings): Configuration for the event's actions handler, determining which action to take (e.g., continueWithAuth) and how to build its parameters.
		listen_buffer_size (int): The buffer size for the event listener channel. Defaults to 10.
		on_error_func (on_error_func_type): An optional function to call if an error occurs during event handling. Defaults to None.
	"""
	
	actions_handler: AuthRequiredActionsHandlerSettings
	listen_buffer_size: int = 10
	on_error_func: on_error_func_type = None
	
	@property
	def handle_function(self) -> "handle_auth_required_func_type":
		"""
		Returns the main handler function for the 'fetch.AuthRequired' event.

		Returns:
			handle_auth_required_func_type: The internal function `_handle_auth_required`.
		"""
		
		return _handle_auth_required
	
	@property
	def class_to_use_path(self) -> str:
		"""
		Returns the path to the CDP event class for 'fetch.AuthRequired'.

		Returns:
			str: The string "fetch.AuthRequired".
		"""
		
		return "fetch.AuthRequired"
	
	def to_dict(self) -> _AuthRequired:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_AuthRequired: The dictionary representation suitable for internal use.
		"""
		
		return _AuthRequired(
				class_to_use_path=self.class_to_use_path,
				listen_buffer_size=self.listen_buffer_size,
				handle_function=self.handle_function,
				actions_handler=self.actions_handler.to_dict(),
				on_error_func=self.on_error_func,
		)


class _ContinueResponseParametersHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'continueResponse' action parameters.

	Attributes:
		response_code (Optional[ParameterHandler]): Handler for the HTTP response code.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase.
		response_headers (Optional[ParameterHandler]): Handler for the response headers.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers (base64 encoded).
	"""
	
	response_code: Optional[ParameterHandler]
	response_phrase: Optional[ParameterHandler]
	response_headers: Optional[ParameterHandler]
	binary_response_headers: Optional[ParameterHandler]


class _ContinueResponseAction(TypedDict):
	"""
	Internal TypedDict for the 'continueResponse' action configuration within RequestPaused.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments for the `continueResponse` CDP command.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_ContinueResponseParametersHandlers): Handlers for modifying response parameters.
	"""
	
	kwargs_func: build_kwargs_from_handlers_func_type
	response_handle_func: response_handle_func_type
	parameters_handlers: _ContinueResponseParametersHandlers


class _FulfillRequestParametersHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'fulfillRequest' action parameters.

	Attributes:
		response_code (ParameterHandler): Required handler for the HTTP response code (e.g., 200).
		response_headers (Optional[ParameterHandler]): Handler for the response headers.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers (base64 encoded).
		body (Optional[ParameterHandler]): Handler for the response body (base64 encoded string).
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase (e.g., "OK").
	"""
	
	response_code: ParameterHandler
	response_headers: Optional[ParameterHandler]
	binary_response_headers: Optional[ParameterHandler]
	body: Optional[ParameterHandler]
	response_phrase: Optional[ParameterHandler]


class _FulfillRequestAction(TypedDict):
	"""
	Internal TypedDict for the 'fulfillRequest' action configuration within RequestPaused.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments for the `fulfillRequest` CDP command.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_FulfillRequestParametersHandlers): Handlers for mock response parameters.
	"""
	
	kwargs_func: build_kwargs_from_handlers_func_type
	response_handle_func: response_handle_func_type
	parameters_handlers: _FulfillRequestParametersHandlers


class _FailRequestParametersHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'failRequest' action parameters.

	Attributes:
		error_reason (ParameterHandler): Required handler for providing the network error reason (a string from Network.ErrorReason enum).
	"""
	
	error_reason: ParameterHandler


class _FailRequestAction(TypedDict):
	"""
	Internal TypedDict for the 'failRequest' action configuration within RequestPaused.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments for the `failRequest` CDP command.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_FailRequestParametersHandlers): Handlers for the error reason parameter.
	"""
	
	kwargs_func: build_kwargs_from_handlers_func_type
	response_handle_func: response_handle_func_type
	parameters_handlers: _FailRequestParametersHandlers


class _ContinueRequestParametersHandlers(TypedDict):
	"""
	Internal TypedDict for handlers related to the 'continueRequest' action parameters.

	Attributes:
		url (Optional[ParameterHandler]): Handler for modifying the request URL.
		method (Optional[ParameterHandler]): Handler for modifying the HTTP method.
		post_data (Optional[ParameterHandler]): Handler for modifying the request's post data (base64 encoded string).
		headers (Optional[ParameterHandler]): Handler for modifying the request headers.
		intercept_response (Optional[ParameterHandler]): Handler for setting response interception behavior for this request.
	"""
	
	url: Optional[ParameterHandler]
	method: Optional[ParameterHandler]
	post_data: Optional[ParameterHandler]
	headers: Optional[ParameterHandler]
	intercept_response: Optional[ParameterHandler]


class _ContinueRequestAction(TypedDict):
	"""
	Internal TypedDict for the 'continueRequest' action configuration within RequestPaused.

	Attributes:
		kwargs_func (build_kwargs_from_handlers_func_type): Function to build keyword arguments for the `continueRequest` CDP command.
		response_handle_func (response_handle_func_type): A function to process the response from the CDP command.
		parameters_handlers (_ContinueRequestParametersHandlers): Handlers for modifying request parameters.
	"""
	
	kwargs_func: build_kwargs_from_handlers_func_type
	response_handle_func: response_handle_func_type
	parameters_handlers: _ContinueRequestParametersHandlers


class _RequestPausedActions(TypedDict):
	"""
	Internal TypedDict mapping action names for RequestPaused event to their configurations.

	Attributes:
		continue_request (Optional[_ContinueRequestAction]): Configuration for the 'continueRequest' action.
		fail_request (Optional[_FailRequestAction]): Configuration for the 'failRequest' action.
		fulfill_request (Optional[_FulfillRequestAction]): Configuration for the 'fulfillRequest' action.
		continue_response (Optional[_ContinueResponseAction]): Configuration for the 'continueResponse' action.
	"""
	
	continue_request: Optional[_ContinueRequestAction]
	fail_request: Optional[_FailRequestAction]
	fulfill_request: Optional[_FulfillRequestAction]
	continue_response: Optional[_ContinueResponseAction]


class _RequestPausedActionsHandler(TypedDict):
	"""
	Internal TypedDict for the actions handler configuration for the 'RequestPaused' event.

	Attributes:
		choose_action_func (request_paused_choose_action_func_type): A function that determines which actions (by name) should be executed for a given 'RequestPaused' event.
		actions (_RequestPausedActions): A dictionary mapping action names to their full configurations.
	"""
	
	choose_action_func: "request_paused_choose_action_func_type"
	actions: _RequestPausedActions


class _RequestPaused(TypedDict):
	"""
	Internal TypedDict representing the complete configuration for a 'RequestPaused' event listener.

	This structure extends `AbstractEvent` with specifics for the Fetch.RequestPaused domain event.

	Attributes:
		class_to_use_path (str): Path to the CDP event class ("fetch.RequestPaused").
		listen_buffer_size (int): Buffer size for the listener channel.
		handle_function (handle_request_paused_func_type): The main handler function for the event (_handle_request_paused).
		actions_handler (_RequestPausedActionsHandler): Callbacks and configurations for choosing and executing actions based on the event.
		on_error_func (on_error_func_type): Function to call on error during event handling.
	"""
	
	class_to_use_path: str
	listen_buffer_size: int
	handle_function: "handle_request_paused_func_type"
	actions_handler: _RequestPausedActionsHandler
	on_error_func: on_error_func_type


async def _handle_request_paused(
		self: "DevTools",
		cdp_session: CdpSession,
		handler_settings: _RequestPaused,
		event: Any
):
	"""
	Handles the 'fetch.RequestPaused' event.

	This function determines which action(s) to take based on the `choose_action_func` defined
	in the handler settings and executes the corresponding CDP command(s) (e.g., `fetch.continueRequest`, `fetch.failRequest`, `fetch.fulfillRequest`, `fetch.continueResponse`)
	with arguments built by the associated parameter handlers. Multiple actions can potentially be executed
	for a single paused request if specified by the `choose_action_func`.

	Args:
		self ("DevTools"): The DevTools instance.
		cdp_session (CdpSession): The active CDP session where the event occurred.
		handler_settings (_RequestPaused): The configuration settings for this 'RequestPaused' event handler.
		event (Any): The 'fetch.RequestPaused' event object received from the CDP session.
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
	Configuration for handlers that modify a response before it continues using `fetch.continueResponse`.

	These handlers provide parameter values for the `fetch.continueResponse` CDP command.

	Attributes:
		response_code (Optional[ParameterHandler]): Handler for the HTTP response code. Defaults to None.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase. Defaults to None.
		response_headers (Optional[ParameterHandler]): Handler for the response headers. Defaults to None.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers (base64 encoded). Defaults to None.
	"""
	
	response_code: Optional[ParameterHandler] = None
	response_phrase: Optional[ParameterHandler] = None
	response_headers: Optional[ParameterHandler] = None
	binary_response_headers: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _ContinueResponseParametersHandlers:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_ContinueResponseParametersHandlers: The dictionary representation suitable for internal use.
		"""
		
		return _ContinueResponseParametersHandlers(
				response_code=self.response_code,
				response_phrase=self.response_phrase,
				response_headers=self.response_headers,
				binary_response_headers=self.binary_response_headers
		)


@dataclass
class ContinueResponseSettings:
	"""
	Settings for the 'continueResponse' action for a paused request (from RequestPaused event).

	This action is used to modify and continue a request *after* the response has been received but before it is processed by the browser.

	Attributes:
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the `fetch.continueResponse` CDP command. Defaults to None.
		parameters_handlers (ContinueResponseHandlersSettings): Configuration for the response parameter handlers that provide modified response details. Defaults to empty `ContinueResponseHandlersSettings`.
	"""
	
	response_handle_func: response_handle_func_type = None
	parameters_handlers: ContinueResponseHandlersSettings = ContinueResponseHandlersSettings()
	
	@property
	def kwargs_func(self) -> build_kwargs_from_handlers_func_type:
		"""
		Returns the function used to build keyword arguments for the `continueResponse` command.

		Returns:
			build_kwargs_from_handlers_func_type: The internal function `_build_kwargs_from_handlers_func`.
		"""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueResponseAction:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_ContinueResponseAction: The dictionary representation suitable for internal use.
		"""
		
		return _ContinueResponseAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
		)


@dataclass
class FulfillRequestHandlersSettings:
	"""
	Configuration for handlers that provide a mock response to a request using `fetch.fulfillRequest`.

	These handlers provide parameter values for the `fetch.fulfillRequest` CDP command.

	Attributes:
		response_code (ParameterHandler): Required handler for the HTTP response code (e.g., 200).
		response_headers (Optional[ParameterHandler]): Handler for the response headers. Defaults to None.
		binary_response_headers (Optional[ParameterHandler]): Handler for binary response headers (base64 encoded). Defaults to None.
		body (Optional[ParameterHandler]): Handler for the response body (base64 encoded string). Defaults to None.
		response_phrase (Optional[ParameterHandler]): Handler for the HTTP response phrase (e.g., "OK"). Defaults to None.
	"""
	
	response_code: ParameterHandler
	response_headers: Optional[ParameterHandler] = None
	binary_response_headers: Optional[ParameterHandler] = None
	body: Optional[ParameterHandler] = None
	response_phrase: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _FulfillRequestParametersHandlers:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_FulfillRequestParametersHandlers: The dictionary representation suitable for internal use.
		"""
		
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
	Settings for the 'fulfillRequest' action for a paused request (from RequestPaused event).

	This action is used to provide a completely mock response for a request, preventing the browser from sending it to the network.

	Attributes:
		parameters_handlers (FulfillRequestHandlersSettings): Configuration for the mock response parameter handlers.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the `fetch.fulfillRequest` CDP command. Defaults to None.
	"""
	
	parameters_handlers: FulfillRequestHandlersSettings
	response_handle_func: response_handle_func_type = None
	
	@property
	def kwargs_func(self) -> build_kwargs_from_handlers_func_type:
		"""
		Returns the function used to build keyword arguments for the `fulfillRequest` command.

		Returns:
			build_kwargs_from_handlers_func_type: The internal function `_build_kwargs_from_handlers_func`.
		"""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _FulfillRequestAction:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_FulfillRequestAction: The dictionary representation suitable for internal use.
		"""
		
		return _FulfillRequestAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
		)


@dataclass
class FailRequestHandlersSettings:
	"""
	Configuration for handlers that specify the reason for failing a request using `fetch.failRequest`.

	These handlers provide parameter values for the `fetch.failRequest` CDP command.

	Attributes:
		error_reason (ParameterHandler): Required handler for providing the network error reason (a string from Network.ErrorReason enum, e.g., "Aborted", "AccessDenied").
	"""
	
	error_reason: ParameterHandler
	
	def to_dict(self) -> _FailRequestParametersHandlers:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_FailRequestParametersHandlers: The dictionary representation suitable for internal use.
		"""
		
		return _FailRequestParametersHandlers(error_reason=self.error_reason)


@dataclass
class FailRequestSettings:
	"""
	Settings for the 'failRequest' action for a paused request (from RequestPaused event).

	This action is used to cause the request to fail with a specific network error reason.

	Attributes:
		parameters_handlers (FailRequestHandlersSettings): Configuration for the error reason handler.
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the `fetch.failRequest` CDP command. Defaults to None.
	"""
	
	parameters_handlers: FailRequestHandlersSettings
	response_handle_func: response_handle_func_type = None
	
	@property
	def kwargs_func(self) -> build_kwargs_from_handlers_func_type:
		"""
		Returns the function used to build keyword arguments for the `failRequest` command.

		Returns:
			build_kwargs_from_handlers_func_type: The internal function `_build_kwargs_from_handlers_func`.
		"""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _FailRequestAction:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_FailRequestAction: The dictionary representation suitable for internal use.
		"""
		
		return _FailRequestAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
		)


@dataclass
class ContinueRequestHandlersSettings:
	"""
	Configuration for handlers that modify a request before it continues using `fetch.continueRequest`.

	These handlers provide parameter values for the `fetch.continueRequest` CDP command.

	Attributes:
		url (Optional[ParameterHandler]): Handler for modifying the request URL. Defaults to None.
		method (Optional[ParameterHandler]): Handler for modifying the HTTP method. Defaults to None.
		post_data (Optional[ParameterHandler]): Handler for modifying the request's post data (base64 encoded string). Defaults to None.
		headers (Optional[ParameterHandler]): Handler for modifying the request headers. Defaults to None.
		intercept_response (Optional[ParameterHandler]): Handler for setting response interception behavior for this request. Defaults to None.
	"""
	
	url: Optional[ParameterHandler] = None
	method: Optional[ParameterHandler] = None
	post_data: Optional[ParameterHandler] = None
	headers: Optional[ParameterHandler] = None
	intercept_response: Optional[ParameterHandler] = None
	
	def to_dict(self) -> _ContinueRequestParametersHandlers:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_ContinueRequestParametersHandlers: The dictionary representation suitable for internal use.
		"""
		
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
	Settings for the 'continueRequest' action for a paused request (from RequestPaused event).

	This action is used to allow the request to proceed, optionally after modifying it.

	Attributes:
		response_handle_func (response_handle_func_type): An optional awaitable function to process the response from the `fetch.continueRequest` CDP command. Defaults to None.
		parameters_handlers (ContinueRequestHandlersSettings): Configuration for the request parameter handlers that provide modified request details. Defaults to empty `ContinueRequestHandlersSettings`.
	"""
	
	response_handle_func: response_handle_func_type = None
	parameters_handlers: ContinueRequestHandlersSettings = ContinueRequestHandlersSettings()
	
	@property
	def kwargs_func(self) -> build_kwargs_from_handlers_func_type:
		"""
		Returns the function used to build keyword arguments for the `continueRequest` command.

		Returns:
			build_kwargs_from_handlers_func_type: The internal function `_build_kwargs_from_handlers_func`.
		"""
		
		return _build_kwargs_from_handlers_func
	
	def to_dict(self) -> _ContinueRequestAction:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_ContinueRequestAction: The dictionary representation suitable for internal use.
		"""
		
		return _ContinueRequestAction(
				kwargs_func=self.kwargs_func,
				response_handle_func=self.response_handle_func,
				parameters_handlers=self.parameters_handlers.to_dict(),
		)


@dataclass
class RequestPausedActionsSettings:
	"""
	Container for configurations of possible actions to take when a request is paused.

	Attributes:
		continue_request (Optional[ContinueRequestSettings]): Settings for handling the paused request using `fetch.continueRequest`. Defaults to None.
		fail_request (Optional[FailRequestSettings]): Settings for handling the paused request using `fetch.failRequest`. Defaults to None.
		fulfill_request (Optional[FulfillRequestSettings]): Settings for handling the paused request using `fetch.fulfillRequest`. Defaults to None.
		continue_response (Optional[ContinueResponseSettings]): Settings for handling the paused request using `fetch.continueResponse`. Defaults to None.
	"""
	
	continue_request: Optional[ContinueRequestSettings] = None
	fail_request: Optional[FailRequestSettings] = None
	fulfill_request: Optional[FulfillRequestSettings] = None
	continue_response: Optional[ContinueResponseSettings] = None
	
	def to_dict(self) -> _RequestPausedActions:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_RequestPausedActions: The dictionary representation suitable for internal use.
		"""
		
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
	"""
	Settings for handling the 'fetch.RequestPaused' event by choosing and executing specific actions.

	Attributes:
		choose_action_func (request_paused_choose_action_func_type): A function that takes the DevTools instance and the event object and returns a list of action names (Literals) to execute. Defaults to `request_paused_choose_func`.
		actions (RequestPausedActionsSettings): Container for the configuration of the available actions. Defaults to an empty `RequestPausedActionsSettings`.
	"""
	
	choose_action_func: "request_paused_choose_action_func_type" = request_paused_choose_func
	actions: RequestPausedActionsSettings = RequestPausedActionsSettings()
	
	def to_dict(self) -> _RequestPausedActionsHandler:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_RequestPausedActionsHandler: The dictionary representation suitable for internal use.
		"""
		
		return _RequestPausedActionsHandler(
				choose_action_func=self.choose_action_func,
				actions=self.actions.to_dict(),
		)


@dataclass
class RequestPausedSettings:
	"""
	Settings for handling the 'fetch.RequestPaused' event.

	This dataclass allows configuring the listener for the 'RequestPaused' CDP event,
	including buffer size, the actions to take, and error handling.

	Attributes:
		listen_buffer_size (int): The buffer size for the event listener channel. Defaults to 50.
		actions_handler (RequestPausedActionsHandlerSettings): Configuration for the event's actions handler, determining which action(s) to take (e.g., continueRequest, fulfillRequest) and how to build their parameters. Defaults to empty `RequestPausedActionsHandlerSettings`.
		on_error_func (on_error_func_type): An optional function to call if an error occurs during event handling. Defaults to None.
	"""
	
	listen_buffer_size: int = 50
	actions_handler: RequestPausedActionsHandlerSettings = RequestPausedActionsHandlerSettings()
	on_error_func: on_error_func_type = None
	
	@property
	def handle_function(self) -> "handle_request_paused_func_type":
		"""
		Returns the main handler function for the 'fetch.RequestPaused' event.

		Returns:
			handle_request_paused_func_type: The internal function `_handle_request_paused`.
		"""
		
		return _handle_request_paused
	
	@property
	def class_to_use_path(self) -> str:
		"""
		Returns the path to the CDP event class for 'fetch.RequestPaused'.

		Returns:
			str: The string "fetch.RequestPaused".
		"""
		
		return "fetch.RequestPaused"
	
	def to_dict(self) -> _RequestPaused:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_RequestPaused: The dictionary representation suitable for internal use.
		"""
		
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
		request_paused (Optional[_RequestPaused]): Configuration for the 'RequestPaused' event handler.
		auth_required (Optional[_AuthRequired]): Configuration for the 'AuthRequired' event handler.
	"""
	
	request_paused: Optional[_RequestPaused]
	auth_required: Optional[_AuthRequired]


@dataclass
class FetchHandlersSettings:
	"""
	Container for all handler settings within the Fetch domain.

	Attributes:
		request_paused (Optional[RequestPausedSettings]): Settings for the 'RequestPaused' event handler. Defaults to None.
		auth_required (Optional[AuthRequiredSettings]): Settings for the 'AuthRequired' event handler. Defaults to None.
	"""
	
	request_paused: Optional[RequestPausedSettings] = None
	auth_required: Optional[AuthRequiredSettings] = None
	
	def to_dict(self) -> _FetchHandlers:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_FetchHandlers: The dictionary representation suitable for internal use.
		"""
		
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
	Keyword arguments for enabling the Fetch domain using `fetch.enable`.

	These settings are passed to the `fetch.enable` CDP command when the Fetch domain is activated.

	Attributes:
		patterns (Optional[list[Any]]): A list of request patterns to intercept. Each pattern is typically a dictionary matching the CDP `Fetch.RequestPattern` type. If None, all requests are intercepted. Defaults to None.
		handle_auth_requests (Optional[bool]): Whether to intercept authentication requests (`fetch.AuthRequired` events). If True, `auth_required` events will be emitted. Defaults to None.
	"""
	
	patterns: Optional[list[Any]] = None
	handle_auth_requests: Optional[bool] = None
	
	def to_dict(self) -> _FetchEnableKwargs:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_FetchEnableKwargs: The dictionary representation suitable for internal use.
		"""
		
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
		enable_func_path (str): The path to the function to enable the domain ("fetch.enable").
		enable_func_kwargs (Optional[_FetchEnableKwargs]): Keyword arguments for the enable function.
		disable_func_path (str): The path to the function to disable the domain ("fetch.disable").
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

	This dataclass allows configuring the entire Fetch CDP domain within the DevTools manager,
	including its enabling parameters and event handlers.

	Attributes:
		enable_func_kwargs (Optional[FetchEnableKwargsSettings]): Keyword arguments for enabling the Fetch domain using `fetch.enable`. Defaults to None.
		handlers (FetchHandlersSettings): Container for all handler settings within the Fetch domain (e.g., RequestPaused, AuthRequired). Defaults to empty `FetchHandlersSettings`.
	"""
	
	enable_func_kwargs: Optional[FetchEnableKwargsSettings] = None
	handlers: FetchHandlersSettings = FetchHandlersSettings()
	
	@property
	def disable_func_path(self) -> str:
		"""
		Returns the path to the function to disable the domain.

		Returns:
			str: The string "fetch.disable".
		"""
		
		return "fetch.disable"
	
	@property
	def enable_func_path(self) -> str:
		"""
		Returns the path to the function to enable the domain.

		Returns:
			str: The string "fetch.enable".
		"""
		
		return "fetch.enable"
	
	@property
	def name(self) -> str:
		"""
		Returns the name of the domain.

		Returns:
			str: The string "fetch".
		"""
		
		return "fetch"
	
	def to_dict(self) -> _Fetch:
		"""
		Converts the settings object to its dictionary representation.

		Returns:
			_Fetch: The dictionary representation suitable for internal use.
		"""
		
		return _Fetch(
				name=self.name,
				enable_func_path=self.enable_func_path,
				enable_func_kwargs=self.enable_func_kwargs.to_dict()
				if self.enable_func_kwargs is not None
				else _FetchEnableKwargs(),
				disable_func_path=self.disable_func_path,
				handlers=self.handlers.to_dict(),
		)


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
