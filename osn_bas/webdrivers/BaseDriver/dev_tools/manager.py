import sys
import trio
import logging
import traceback
from types import TracebackType
from collections.abc import Sequence
from selenium.webdriver.common.bidi.cdp import CdpSession, open_cdp
from selenium.webdriver.remote.bidi_connection import BidiConnection
from contextlib import (
	AbstractAsyncContextManager,
	asynccontextmanager
)
from osn_bas.webdrivers.BaseDriver.dev_tools.domains.abstract import AbstractEvent
from osn_bas.webdrivers.BaseDriver.protocols import (
	TrioWebDriverWrapperProtocol
)
from typing import (
	Any,
	AsyncGenerator,
	Optional,
	TYPE_CHECKING,
	Union,
	cast
)
from osn_bas.webdrivers.BaseDriver.dev_tools.errors import (
	CantEnterDevToolsContextError
)
from osn_bas.webdrivers.BaseDriver.dev_tools._utils import (
	log_on_error,
	validate_handler_settings,
	warn_if_active
)
from osn_bas.webdrivers.BaseDriver.dev_tools.domains import (
	Domains,
	DomainsSettings,
	domains_classes_type,
	domains_type
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.webdriver import BrowserWebDriver


class DevTools:
	"""
	Base class for handling DevTools functionalities in Selenium WebDriver.

	Provides an interface to interact with Chrome DevTools Protocol (CDP)
	for advanced browser control and monitoring. This class supports event handling
	and allows for dynamic modifications of browser behavior, such as network request interception,
	by using an asynchronous context manager.

	Attributes:
		_webdriver (BrowserWebDriver): The parent WebDriver instance associated with this DevTools instance.
		_bidi_connection (Optional[AbstractAsyncContextManager[BidiConnection, Any]]): Asynchronous context manager for the BiDi connection.
		_bidi_connection_object (Optional[BidiConnection]): The BiDi connection object when active.
		_bidi_devtools (Optional[Any]): The DevTools API object from the BiDi connection.
		_is_active (bool): Flag indicating if the DevTools event handler is currently active.
		_nursery (Optional[AbstractAsyncContextManager[trio.Nursery, Optional[bool]]]): Asynchronous context manager for the Trio nursery.
		_nursery_object (Optional[trio.Nursery]): The Trio nursery object when active, managing concurrent tasks.
		_exit_event (Optional[trio.Event]): Trio Event to signal exiting of DevTools event handling.
		_domains_settings (Domains): Settings for configuring DevTools domain handlers.
		cache (dict[Any, Any]): A dictionary for caching data across DevTools event handlers.

	EXAMPLES
	________
	async with driver.dev_tools as driver_wrapper:
		# DevTools event handling is active within this block.
		# Configure domain handlers here.
		await driver_wrapper.get("https://example.com")
	# DevTools event handling is deactivated after exiting the block.
	"""
	
	def __init__(self, parent_webdriver: "BrowserWebDriver"):
		"""
		Initializes the DevTools instance.

		Args:
			parent_webdriver ("BrowserWebDriver"): The parent WebDriver instance that this DevTools instance will be associated with.
		"""
		
		self._webdriver = parent_webdriver
		self._bidi_connection: Optional[AbstractAsyncContextManager[BidiConnection, Any]] = None
		self._bidi_connection_object: Optional[BidiConnection] = None
		self._bidi_devtools: Optional[Any] = None
		self._is_active = False
		self._nursery: Optional[AbstractAsyncContextManager[trio.Nursery, Optional[bool]]] = None
		self._nursery_object: Optional[trio.Nursery] = None
		self._exit_event: Optional[trio.Event] = None
		self._domains_settings: Domains = {}
		self.cache = {}
	
	async def _start_listeners(self, cdp_session: CdpSession):
		"""
		Starts all configured DevTools event listeners.

		This method initiates listeners for all domains configured in `_domains_settings`.
		It enables target discovery, starts a nursery task to process new targets, enables
		each configured domain, and starts the individual event listeners.

		Args:
			cdp_session (CdpSession): The CDP session object to use for starting listeners.
		"""
		
		try:
			await cdp_session.execute(self._get_devtools_object("target.set_discover_targets")(True))
			self._nursery_object.start_soon(self._process_new_targets, cdp_session)
		
			for domain_name, domain_config in self._domains_settings.items():
				if domain_config.get("enable_func_path", None) is not None:
					enable_func_kwargs = domain_config.get("enable_func_kwargs", {})
					await cdp_session.execute(
							self._get_devtools_object(domain_config["enable_func_path"])(**enable_func_kwargs)
					)
		
				for event_name, event_config in domain_config["handlers"].items():
					if event_config is not None:
						handler_type = validate_handler_settings(event_config)
		
						if handler_type == "class":
							self._nursery_object.start_soon(self._run_event_listener, cdp_session, event_config)
		
			await trio.sleep(0.0)
		except (trio.Cancelled, trio.EndOfChannel):
			pass
	
	async def _process_new_targets(self, cdp_session: CdpSession):
		"""
		Processes new browser targets as they are created.

		Listens for 'target.TargetCreated' events, which are emitted when new targets (like tabs or windows) are created in the browser.
		For each new target of type 'page', it starts a new nursery task to handle events for that target.

		Args:
			cdp_session (CdpSession): The CDP session object to listen for target creation events.
		"""
		
		receiver_channel: trio.MemoryReceiveChannel = cdp_session.listen(self._get_devtools_object("target.TargetCreated"))
		
		while True:
			try:
				event = await receiver_channel.receive()
		
				if event.target_info.type_ == "page":
					self._nursery_object.start_soon(self._handle_new_target, event.target_info.target_id)
			except (trio.Cancelled, trio.EndOfChannel):
				break
			except (Exception,):
				exception_type, exception_value, exception_traceback = sys.exc_info()
				error = "".join(
						traceback.format_exception(exception_type, exception_value, exception_traceback)
				)
		
				logging.log(logging.ERROR, error)
	
	async def _handle_new_target(self, target_id: str):
		"""
		Handles events for a newly created browser target.

		Manages a new CDP session for a given target ID. It uses `_new_session_manager` to open a session for the target,
		starts event listeners for this new session, and waits for a cancellation event before closing the session.

		Args:
			target_id (str): The ID of the new browser target to handle.
		"""
		
		try:
			async with self._new_session_manager(target_id) as new_session:
				await self._start_listeners(new_session)
				await self._exit_event.wait()
		except (trio.Cancelled, trio.EndOfChannel):
			pass
	
	def _get_devtools_object(self, path: str) -> Any:
		"""
		Navigates and retrieves a specific object within the DevTools API structure.

		Using a dot-separated path, this method traverses the nested DevTools API objects to retrieve a target object.
		For example, a path like "fetch.enable" would access `self._bidi_devtools.fetch.enable`.

		Args:
			path (str): A dot-separated string representing the path to the desired DevTools API object.

		Returns:
			Any: The DevTools API object located at the specified path.
		"""
		
		object_ = self._bidi_devtools
		
		for path_part in path.split("."):
			object_ = getattr(object_, path_part)
		
		return object_
	
	async def _run_event_listener(self, cdp_session: CdpSession, event_config: AbstractEvent):
		"""
		Runs a specific event listener, processing events from a CDP channel.

		This method sets up a listener for a specific CDP event using the provided configuration.
		It continuously receives events from the channel and starts a new task in the nursery
		to execute the handler function for each event.

		Args:
			cdp_session (CdpSession): The CDP session to listen on.
			event_config (AbstractEvent): The configuration for the event listener.
		"""
		
		handler = event_config["handle_function"]
		
		class_to_use = self._get_devtools_object(event_config["class_to_use_path"])
		receiver_channel: trio.MemoryReceiveChannel = cdp_session.listen(class_to_use, buffer_size=event_config["listen_buffer_size"])
		
		while True:
			try:
				event = await receiver_channel.receive()
		
				if handler:
					self._nursery_object.start_soon(handler, self, cdp_session, event_config, event)
			except (trio.Cancelled, trio.EndOfChannel):
				break
			except (Exception,):
				exception_type, exception_value, exception_traceback = sys.exc_info()
				error = "".join(
						traceback.format_exception(exception_type, exception_value, exception_traceback)
				)
		
				logging.log(logging.ERROR, error)
	
	@property
	def _websocket_url(self) -> Optional[str]:
		"""
		Retrieves the WebSocket URL for DevTools from the WebDriver.

		This method attempts to get the WebSocket URL from the WebDriver capabilities or by directly querying the CDP details.
		The WebSocket URL is necessary to establish a connection to the browser's DevTools.

		Returns:
			Optional[str]: The WebSocket URL for DevTools, or None if it cannot be retrieved.
		"""
		
		driver = self._webdriver.driver
		
		if driver is None:
			return None
		
		if driver.caps.get("se:cdp"):
			return driver.caps.get("se:cdp")
		
		return driver._get_cdp_details()[1]
	
	@asynccontextmanager
	async def _new_session_manager(self, target_id: str) -> AsyncGenerator[CdpSession, None]:
		"""
		Manages a new CDP session for a specific target, using async context management.

		This context manager opens a new CDP session for a given target ID and ensures that the session is properly closed after use.
		It's used to handle the lifecycle of CDP sessions for different browser targets.

		Args:
			target_id (str): The ID of the browser target for which to open a new CDP session.

		Returns:
			AsyncGenerator[CdpSession, None]: An asynchronous generator that yields a CdpSession object, allowing for operations within the session context.
		"""
		
		async with open_cdp(self._websocket_url) as new_connection:
			async with new_connection.open_session(target_id) as new_session:
				yield new_session
	
	async def __aenter__(self) -> TrioWebDriverWrapperProtocol:
		"""
		Asynchronously enters the DevTools event handling context.

		This method is called when entering an `async with` block with a DevTools instance.
		It initializes the BiDi connection, starts a Trio nursery to manage event listeners,
		and then starts listening for DevTools events.

		Returns:
			TrioWebDriverWrapperProtocol: Returns a wrapped WebDriver object that can be used to interact with the browser
				while DevTools event handling is active.

		Raises:
			CantEnterDevToolsContextError: If the WebDriver driver is not initialized, indicating that a browser session has not been started yet.

		EXAMPLES
		________
		async with driver.dev_tools as driver_wrapper:
			# DevTools event handling is active within this block
			await driver.dev_tools.set_domains_handlers(...)
			await driver_wrapper.get("https://example.com")
		# DevTools event handling is deactivated after exiting the block
		"""
		
		if self._webdriver.driver is None:
			raise CantEnterDevToolsContextError("Driver is not initialized")
		
		self._bidi_connection: AbstractAsyncContextManager[BidiConnection, Any] = self._webdriver.driver.bidi_connection()
		self._bidi_connection_object = await self._bidi_connection.__aenter__()
		self._bidi_devtools = self._bidi_connection_object.devtools
		
		self._nursery = trio.open_nursery()
		self._nursery_object = await self._nursery.__aenter__()
		
		await self._start_listeners(self._bidi_connection_object.session)
		
		self._is_active = True
		self._exit_event = trio.Event()
		
		return cast(TrioWebDriverWrapperProtocol, self._webdriver.to_wrapper())
	
	async def __aexit__(
			self,
			exc_type: Optional[type],
			exc_val: Optional[BaseException],
			exc_tb: Optional[TracebackType]
	):
		"""
		Asynchronously exits the DevTools event handling context.

		This method is called when exiting an `async with` block with a DevTools instance.
		It ensures that all event listeners are cancelled, the Trio nursery is closed,
		and the BiDi connection is properly shut down.

		Args:
			exc_type (Optional[type[BaseException]]): The exception type, if any, that caused the context to be exited.
			exc_val (Optional[BaseException]): The exception value, if any.
			exc_tb (Optional[TracebackType]): The exception traceback, if any.
		"""
		
		@log_on_error
		def _close_nursery_object():
			"""Closes the Trio nursery object and cancels all tasks within it."""
			
			if self._nursery_object is not None:
				self._nursery_object.cancel_scope.cancel()
				self._nursery_object = None
		
		@log_on_error
		async def _close_nursery():
			"""Asynchronously exits the Trio nursery context manager."""
			
			if self._nursery is not None:
				await self._nursery.__aexit__(exc_type, exc_val, exc_tb)
				self._nursery = None
		
		@log_on_error
		async def _close_bidi_connection():
			"""Asynchronously exits the BiDi connection context manager."""
			
			if self._bidi_connection is not None:
				await self._bidi_connection.__aexit__(exc_type, exc_val, exc_tb)
				self._bidi_connection = None
				self._bidi_connection_object = None
				self._bidi_devtools = None
		
		@log_on_error
		def _activate_exit_event():
			"""Sets the exit event to signal listeners to stop."""
			
			if self._exit_event is not None:
				self._exit_event.set()
				self._exit_event = None
		
		if self._is_active:
			_activate_exit_event()
			_close_nursery_object()
			await _close_nursery()
			await _close_bidi_connection()
		
			self._is_active = False
	
	@property
	def is_active(self) -> bool:
		"""
		Checks if DevTools is currently active.

		Returns:
			bool: True if DevTools event handler context manager is active, False otherwise.
		"""
		
		return self._is_active
	
	@warn_if_active
	def _remove_handler_settings(self, domain: domains_type):
		"""
		Removes the settings for a specific domain.

		Args:
			domain (domains_type): The name of the domain to remove settings for.
		"""
		
		self._domains_settings.pop(domain, None)
	
	def remove_domains_handlers(self, domains: Union[domains_type, Sequence[domains_type]]):
		"""
		Removes handler settings for one or more DevTools domains.

		This method can be called with a single domain name or a sequence of domain names.

		Args:
			domains (Union[domains_type, Sequence[domains_type]]): A single domain name as a string,
				or a sequence of domain names to be removed.

		Raises:
			TypeError: If the `domains` argument is not a string or a sequence of strings.
		"""
		
		if isinstance(domains, Sequence) and all(isinstance(domain, str) for domain in domains):
			for domain in domains:
				self._remove_handler_settings(domain)
		elif isinstance(domains, str):
			self._remove_handler_settings(domains)
		else:
			raise TypeError(f"domains must be a str or a sequence of str, got {type(domains)}.")
	
	@warn_if_active
	def _set_handler_settings(self, domain: domains_type, settings: domains_classes_type,):
		"""
		Sets the handler settings for a specific domain.

		Args:
			domain (domains_type): The name of the domain to configure.
			settings (domains_classes_type): The configuration settings for the domain.
		"""
		
		self._domains_settings[domain] = settings
	
	def set_domains_handlers(self, settings: DomainsSettings):
		"""
		Sets handler settings for multiple domains from a DomainsSettings object.

		This method iterates through the provided settings and applies them to the corresponding domains.

		Args:
			settings (DomainsSettings): An object containing the configuration for one or more domains.
		"""
		
		for domain_name, domain_settings in settings.to_dict().items():
			self._set_handler_settings(domain_name, domain_settings)
