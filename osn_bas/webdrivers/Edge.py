import pathlib
from selenium import webdriver
from osn_bas.types import WindowRect
from typing import (
	Optional,
	TypedDict,
	Union
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from osn_bas.browsers_handler import get_path_to_browser
from osn_bas.webdrivers.BaseDriver.webdriver import BlinkWebDriver, CaptchaWorkerSettings
from osn_bas.webdrivers.BaseDriver.flags import (
	BlinkArguments,
	BlinkAttributes,
	BlinkExperimentalOptions,
	BlinkFeatures,
	BlinkFlagsManager,
	FlagDefinition,
	FlagType
)


class EdgeFlagsManager(BlinkFlagsManager):
	"""
	Manages Edge Browser-specific options for Selenium WebDriver.

	This class extends BrowserOptionsManager to provide specific configurations
	for Edge Browser options, such as experimental options and arguments.

	Attributes:
	"""
	
	def __init__(
			self,
			browser_exe: Optional[Union[str, pathlib.Path]] = None,
			start_page_url: Optional[str] = None,
			flags_types: Optional[dict[str, FlagType]] = None,
			flags_definitions: Optional[dict[str, FlagDefinition]] = None
	):
		"""
		Initializes EdgeOptionsManager.

		Sets up the Edge Browser options manager with specific option configurations for
		debugging port, user agent, proxy, and BiDi protocol.
		"""
		
		edge_flags_types = {}
		
		if flags_types is not None:
			edge_flags_types.update(flags_types)
		
		edge_flags_definitions = {}
		
		if flags_definitions is not None:
			edge_flags_definitions.update(flags_definitions)
		
		super().__init__(
				browser_exe=browser_exe,
				start_page_url=start_page_url,
				flags_types=edge_flags_types,
				flags_definitions=edge_flags_definitions,
		)
	
	def _renew_webdriver_options(self) -> Options:
		"""
		Creates and returns a new Options object.

		Returns a fresh instance of `webdriver.EdgeOptions`, as Edge Browser is based on Chromium,
		allowing for a clean state of browser options to be configured.

		Returns:
			Options: A new Selenium Edge Browser options object, based on EdgeOptions.
		"""
		
		return Options()


class EdgeFeatures(BlinkFeatures, total=False):
	pass


class EdgeAttributes(BlinkAttributes, total=False):
	pass


class EdgeExperimentalOptions(BlinkExperimentalOptions, total=False):
	pass


class EdgeArguments(BlinkArguments, total=False):
	pass


class EdgeFlags(TypedDict, total=False):
	argument: EdgeArguments
	experimental_option: EdgeExperimentalOptions
	attribute: EdgeAttributes
	blink_feature: EdgeFeatures


class EdgeWebDriver(BlinkWebDriver):
	"""
	Manages a Edge Browser session using Selenium WebDriver.

	This class specializes BlinkWebDriver for Edge Browser. It sets up and manages
	the lifecycle of a Edge Browser instance controlled by Selenium WebDriver,
	including starting the browser with specific options, handling sessions, and managing browser processes.
	Edge Browser is based on Chromium, so it uses EdgeOptions and EdgeDriver.

	Attributes:
		_window_rect (Optional[WindowRect]): The window size and position settings.
		_js_scripts (dict[str, str]): A dictionary of pre-loaded JavaScript scripts.
		_webdriver_path (str): The file path to the WebDriver executable.
		_webdriver_flags_manager (EdgeFlagsManager): The manager for browser flags and options.
		driver (Optional[Union[webdriver.Edge, webdriver.Edge, webdriver.Firefox]]): The active Selenium WebDriver instance.
		_base_implicitly_wait (int): The default implicit wait time in seconds.
		_base_page_load_timeout (int): The default page load timeout in seconds.
		_captcha_workers (list[CaptchaWorkerSettings]): A list of configured captcha worker settings.
		_is_active (bool): A flag indicating if the browser process is active.
		trio_capacity_limiter (trio.CapacityLimiter): A capacity limiter for controlling concurrent async operations.
		dev_tools (DevTools): An interface for interacting with the browser's DevTools protocol.
		_console_encoding (str): The encoding of the system console.
		_ip_pattern (re.Pattern): A compiled regex pattern to match IP addresses and ports.
	"""
	
	def __init__(
			self,
			webdriver_path: str,
			use_browser_exe: bool = True,
			browser_exe: Optional[Union[str, pathlib.Path]] = None,
			flags: Optional[EdgeFlags] = None,
			start_page_url: str = "https://www.chrome.com",
			implicitly_wait: int = 5,
			page_load_timeout: int = 5,
			window_rect: Optional[WindowRect] = None,
			trio_tokens_limit: Union[int, float] = 40,
			captcha_workers: Optional[list[CaptchaWorkerSettings]] = None,
	):
		"""
		Initializes the EdgeWebDriver instance for managing Edge Browser.

		This constructor sets up the WebDriver specifically for Edge Browser,
		configuring browser and driver paths, and applying default or user-specified settings
		for browser behavior like headless mode, proxy, and DevTools.

		Args:
			webdriver_path (str): Path to the EdgeDriver executable compatible with Edge Browser.
			use_browser_exe (bool): If True, attempts to automatically detect or uses the provided `browser_exe` path. If False, does not configure the browser executable path. Defaults to True.
			browser_exe (Optional[Union[str, pathlib.Path]]): Path to the Edge Browser executable. If `use_browser_exe` is True and `browser_exe` is None, the path is automatically detected. If `use_browser_exe` is False, this parameter is ignored. Defaults to None.
			flags (Optional[EdgeFlags]): Specific Edge Browser flags and options to apply. Defaults to None.
			start_page_url (str): URL to open when the browser starts. Defaults to "https://www.chrome.com".
			implicitly_wait (int): Base implicit wait time for WebDriver element searches in seconds. Defaults to 5.
			page_load_timeout (int): Base page load timeout for WebDriver operations in seconds. Defaults to 5.
			window_rect (Optional[WindowRect]): Initial window rectangle settings for the browser window. Defaults to None.
			trio_tokens_limit (Union[int, float]): The total number of tokens for the Trio capacity limiter used for concurrent operations. Use `float('inf')` for unlimited. Defaults to 40.
			captcha_workers (Optional[list[CaptchaWorkerSettings]]): A list of configured captcha worker settings. Defaults to None.
		"""
		
		if browser_exe is None and use_browser_exe:
			browser_exe = get_path_to_browser("Microsoft Edge")
		elif browser_exe is not None and not use_browser_exe:
			browser_exe = None
		
		super().__init__(
				browser_exe=browser_exe,
				webdriver_path=webdriver_path,
				flags_manager_type=EdgeFlagsManager,
				flags=flags,
				start_page_url=start_page_url,
				implicitly_wait=implicitly_wait,
				page_load_timeout=page_load_timeout,
				window_rect=window_rect,
				trio_tokens_limit=trio_tokens_limit,
				captcha_workers=captcha_workers,
		)
	
	def _create_driver(self):
		"""
		Creates the Edge webdriver instance.

		This method initializes and sets up the Selenium Edge WebDriver using EdgeDriver with configured options and service.
		It also sets the window position, size, implicit wait time, and page load timeout.
		"""
		
		webdriver_options = self._webdriver_flags_manager.options
		webdriver_service = Service(
				executable_path=self._webdriver_path,
				port=self.debugging_port if self.browser_exe is None else 0,
				service_args=self._webdriver_flags_manager.start_args
				if self.browser_exe is None
				else None
		)
		
		self.driver = webdriver.Edge(options=webdriver_options, service=webdriver_service)
		
		if self._window_rect is not None:
			self.set_window_rect(self._window_rect)
		
		self.set_driver_timeouts(
				page_load_timeout=self._base_page_load_timeout,
				implicit_wait_timeout=self._base_implicitly_wait
		)
