import trio
import pathlib
from selenium import webdriver
from types import TracebackType
from osn_bas.utilities import WindowRect
from selenium.webdriver.common.by import By
from selenium.webdriver.common.bidi.cdp import CdpSession
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.bidi_connection import BidiConnection
from osn_bas.webdrivers.BaseDriver.start_args import BrowserStartArgs
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.BaseDriver.options import (
	BrowserOptionsManager
)
from contextlib import (
	AbstractAsyncContextManager,
	asynccontextmanager
)
from osn_bas.webdrivers.BaseDriver.dev_tools.domains import (
	CallbacksSettings,
	fetch
)
from typing import (
	Any,
	AsyncGenerator,
	Callable,
	Coroutine,
	Mapping,
	Optional,
	Protocol,
	TYPE_CHECKING,
	Union,
	runtime_checkable
)


if TYPE_CHECKING:
	from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools
	from osn_bas.webdrivers.BaseDriver.webdriver import BrowserWebDriver, TrioBrowserWebDriverWrapper


@runtime_checkable
class TrioWebDriverWrapperProtocol(Protocol):
	"""
	Protocol defining the asynchronous interface for TrioBrowserWebDriverWrapper.
	"""
	
	driver: "BrowserWebDriver"
	
	def __init__(self, driver: "BrowserWebDriver"):
		...
	
	async def check_webdriver_active(self) -> bool:
		...
	
	async def close_all_windows(self) -> None:
		...
	
	async def close_webdriver(self) -> None:
		...
	
	async def close_window(self, window: Optional[Union[str, int]] = None) -> None:
		...
	
	async def create_driver(self) -> None:
		...
	
	@property
	async def current_url(self) -> str:
		...
	
	@property
	async def debugging_port(self) -> Optional[int]:
		...
	
	async def execute_js_script(self, script: str, *args) -> Any:
		...
	
	async def find_debugging_port(self, debugging_port: Optional[int], profile_dir: Optional[str]) -> int:
		...
	
	async def find_inner_web_element(
			self,
			parent_element: WebElement,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None,
	) -> WebElement:
		...
	
	async def find_inner_web_elements(
			self,
			parent_element: WebElement,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None,
	) -> list[WebElement]:
		...
	
	async def find_web_element(
			self,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> WebElement:
		...
	
	async def find_web_elements(
			self,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> list[WebElement]:
		...
	
	async def get_element_css_style(self, element: WebElement) -> dict[str, str]:
		...
	
	async def get_vars_for_remote(self) -> tuple[RemoteConnection, str]:
		...
	
	async def hover_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	@property
	async def html(self) -> str:
		...
	
	@property
	async def is_active(self) -> bool:
		...
	
	async def open_new_tab(self, link: str = "") -> None:
		...
	
	@property
	async def rect(self) -> WindowRect:
		...
	
	async def refresh_webdriver(self) -> None:
		...
	
	async def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str) -> None:
		...
	
	async def reset_settings(
			self,
			enable_devtools: bool,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	async def restart_webdriver(
			self,
			enable_devtools: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	async def scroll_by_amount(self, x: int = 0, y: int = 0, duration: int = 250) -> None:
		...
	
	async def scroll_down_of_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	async def scroll_from_origin(
			self,
			origin: ScrollOrigin,
			x: int = 0,
			y: int = 0,
			duration: int = 250
	) -> None:
		...
	
	async def scroll_to_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	async def scroll_up_of_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	async def search_url(
			self,
			url: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> None:
		...
	
	async def set_debugging_port(self, debugging_port: Optional[int]) -> None:
		...
	
	async def set_driver_timeouts(self, page_load_timeout: float, implicit_wait_timeout: float) -> None:
		...
	
	async def set_enable_devtools(self, enable_devtools: bool) -> None:
		...
	
	async def set_headless_mode(self, headless_mode: bool) -> None:
		...
	
	async def set_implicitly_wait_timeout(self, timeout: float) -> None:
		...
	
	async def set_mute_audio(self, mute_audio: bool) -> None:
		...
	
	async def set_page_load_timeout(self, timeout: float) -> None:
		...
	
	async def set_profile_dir(self, profile_dir: Optional[str]) -> None:
		...
	
	async def set_proxy(self, proxy: Optional[Union[str, list[str]]]) -> None:
		...
	
	async def set_user_agent(self, user_agent: Optional[str]) -> None:
		...
	
	async def set_window_rect(self, rect: WindowRect) -> None:
		...
	
	async def start_webdriver(
			self,
			enable_devtools: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	async def stop_window_loading(self) -> None:
		...
	
	async def switch_to_frame(self, frame: Union[str, int, WebElement]) -> None:
		...
	
	async def switch_to_window(self, window: Optional[Union[str, int]] = None) -> None:
		...
	
	async def update_settings(
			self,
			enable_devtools: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	async def update_times(
			self,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> None:
		...
	
	@property
	async def window(self) -> str:
		...
	
	@property
	async def windows_names(self) -> list[str]:
		...


@runtime_checkable
class DevToolsProtocol(Protocol):
	"""
	Protocol defining the interface for DevTools.
	"""
	
	_webdriver: "BrowserWebDriver"
	_bidi_connection: Optional[AbstractAsyncContextManager[BidiConnection, Any]]
	_bidi_connection_object: Optional[BidiConnection]
	_bidi_devtools: Optional[Any]
	_is_active: bool
	_nursery: Optional[AbstractAsyncContextManager[trio.Nursery, Optional[bool]]]
	_nursery_object: Optional[trio.Nursery]
	_cancel_event: Optional[trio.Event]
	_callbacks_settings: CallbacksSettings
	
	async def __aenter__(self) -> TrioWebDriverWrapperProtocol:
		...
	
	async def __aexit__(
			self,
			exc_type: Optional[type],
			exc_val: Optional[BaseException],
			exc_tb: Optional[TracebackType]
	) -> None:
		...
	
	def __init__(self, parent_webdriver: "BrowserWebDriver"):
		...
	
	def _get_devtools_object(self, path: str) -> Any:
		...
	
	def _get_handler_to_use(self, event_type: str, event_name: str) -> Optional[
		Callable[
			[CdpSession, fetch.RequestPausedHandlerSettings, Any],
			Coroutine[None, None, Any]
		]
	]:
		...
	
	async def _handle_fetch_request_paused(
			self,
			cdp_session: CdpSession,
			handler_settings: fetch.RequestPausedHandlerSettings,
			event: Any
	) -> None:
		...
	
	async def _handle_new_target(self, target_id: str) -> None:
		...
	
	@asynccontextmanager
	async def _new_session_manager(self, target_id: str) -> AsyncGenerator[CdpSession, None]:
		...
	
	async def _process_new_targets(self, cdp_session: CdpSession) -> None:
		...
	
	def _remove_handler_settings(self, event_type: str, event_name: str) -> None:
		...
	
	async def _run_event_listener(self, cdp_session: CdpSession, event_type: str, event_name: str) -> None:
		...
	
	def _set_handler_settings(
			self,
			event_type: str,
			event_name: str,
			settings_type: type,
			**kwargs: Any
	) -> None:
		...
	
	async def _start_listeners(self, cdp_session: CdpSession) -> None:
		...
	
	@property
	def _websocket_url(self) -> Optional[str]:
		...
	
	@property
	def is_active(self) -> bool:
		...
	
	def remove_request_paused_handler_settings(self) -> None:
		...
	
	def set_request_paused_handler(
			self,
			post_data_instances: Optional[Any] = None,
			headers_instances: Optional[Mapping[str, fetch.HeaderInstance]] = None,
			post_data_handler: Optional[Callable[[fetch.RequestPausedHandlerSettings, Any], Optional[str]]] = None,
			headers_handler: Optional[Callable[[fetch.RequestPausedHandlerSettings, Any], Optional[Mapping]]] = None
	) -> None:
		...


@runtime_checkable
class BrowserWebDriverProtocol(Protocol):
	"""
	Protocol defining the interface for BrowserWebDriver (synchronous).
	"""
	
	_window_rect: WindowRect
	_js_scripts: dict[str, str]
	_browser_exe: Union[str, pathlib.Path]
	_webdriver_path: str
	_webdriver_start_args: BrowserStartArgs
	_webdriver_options_manager: BrowserOptionsManager
	driver: Optional[Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox]]
	_base_implicitly_wait: int
	_base_page_load_timeout: int
	_is_active: bool
	_enable_devtools: bool
	dev_tools: "DevTools"
	
	def __init__(
			self,
			browser_exe: Union[str, pathlib.Path],
			webdriver_path: str,
			enable_devtools: bool,
			webdriver_start_args: type,
			webdriver_options_manager: type,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			implicitly_wait: int = 5,
			page_load_timeout: int = 5,
			window_rect: Optional[WindowRect] = None,
	):
		...
	
	def check_webdriver_active(self) -> bool:
		...
	
	def close_all_windows(self) -> None:
		...
	
	def close_webdriver(self) -> None:
		...
	
	def close_window(self, window: Optional[Union[str, int]] = None) -> None:
		...
	
	def create_driver(self) -> None:
		...
	
	@property
	def current_url(self) -> str:
		...
	
	@property
	def debugging_port(self) -> Optional[int]:
		...
	
	def execute_js_script(self, script: str, *args) -> Any:
		...
	
	def find_debugging_port(self, debugging_port: Optional[int], profile_dir: Optional[str]) -> int:
		...
	
	def find_inner_web_element(
			self,
			parent_element: WebElement,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None,
	) -> WebElement:
		...
	
	def find_inner_web_elements(
			self,
			parent_element: WebElement,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None,
	) -> list[WebElement]:
		...
	
	def find_web_element(
			self,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> WebElement:
		...
	
	def find_web_elements(
			self,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> list[WebElement]:
		...
	
	def get_element_css_style(self, element: WebElement) -> dict[str, str]:
		...
	
	def get_vars_for_remote(self) -> tuple[RemoteConnection, str]:
		...
	
	def hover_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	@property
	def html(self) -> str:
		...
	
	@property
	def is_active(self) -> bool:
		...
	
	def open_new_tab(self, link: str = "") -> None:
		...
	
	@property
	def rect(self) -> WindowRect:
		...
	
	def refresh_webdriver(self) -> None:
		...
	
	def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str) -> None:
		...
	
	def reset_settings(
			self,
			enable_devtools: bool,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	def restart_webdriver(
			self,
			enable_devtools: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	def scroll_by_amount(self, x: int = 0, y: int = 0, duration: int = 250) -> None:
		...
	
	def scroll_down_of_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	def scroll_from_origin(
			self,
			origin: ScrollOrigin,
			x: int = 0,
			y: int = 0,
			duration: int = 250
	) -> None:
		...
	
	def scroll_to_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	def scroll_up_of_element(self, element: WebElement, duration: int = 250) -> None:
		...
	
	def search_url(
			self,
			url: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> None:
		...
	
	def set_debugging_port(self, debugging_port: Optional[int]) -> None:
		...
	
	def set_driver_timeouts(self, page_load_timeout: float, implicit_wait_timeout: float) -> None:
		...
	
	def set_enable_devtools(self, enable_devtools: bool) -> None:
		...
	
	def set_headless_mode(self, headless_mode: bool) -> None:
		...
	
	def set_implicitly_wait_timeout(self, timeout: float) -> None:
		...
	
	def set_mute_audio(self, mute_audio: bool) -> None:
		...
	
	def set_page_load_timeout(self, timeout: float) -> None:
		...
	
	def set_profile_dir(self, profile_dir: Optional[str]) -> None:
		...
	
	def set_proxy(self, proxy: Optional[Union[str, list[str]]]) -> None:
		...
	
	def set_user_agent(self, user_agent: Optional[str]) -> None:
		...
	
	def set_window_rect(self, rect: WindowRect) -> None:
		...
	
	def start_webdriver(
			self,
			enable_devtools: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	def stop_window_loading(self) -> None:
		...
	
	def switch_to_frame(self, frame: Union[str, int, WebElement]) -> None:
		...
	
	def switch_to_window(self, window: Optional[Union[str, int]] = None) -> None:
		...
	
	def to_wrapper(self) -> "TrioBrowserWebDriverWrapper":
		...
	
	def update_settings(
			self,
			enable_devtools: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	) -> None:
		...
	
	def update_times(
			self,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> None:
		...
	
	@property
	def window(self) -> str:
		...
	
	@property
	def windows_names(self) -> list[str]:
		...
