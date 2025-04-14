import pathlib
from selenium import webdriver
from typing import Optional, Union
from osn_bas.types import WindowRect
from osn_bas.webdrivers.types import WebdriverOption
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from osn_bas.browsers_handler import get_path_to_browser
from osn_bas.webdrivers.BaseDriver.webdriver import BrowserWebDriver
from osn_bas.webdrivers.BaseDriver.start_args import BrowserStartArgs
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.BaseDriver.options import (
	BrowserOptionsManager
)


class ChromeOptionsManager(BrowserOptionsManager):
	"""
	Manages Chrome-specific browser options for Selenium WebDriver.

	This class extends BrowserOptionsManager to provide specific configurations
	for Chrome browser options, such as experimental options and arguments.
	It initializes default Chrome options and provides methods to modify them.

	Attributes:
		_options (webdriver.ChromeOptions): Chrome options object.
		_debugging_port_command (WebdriverOption): Configuration for debugging port option.
		_user_agent_command (WebdriverOption): Configuration for user agent option.
		_proxy_command (WebdriverOption): Configuration for proxy option.
		_enable_bidi_command (WebdriverOption): Configuration for enable BiDi option.
	"""
	
	def __init__(self):
		"""
		Initializes ChromeOptionsManager.

		Sets up the Chrome options manager with specific option configurations for
		debugging port, user agent, proxy, and BiDi protocol.
		"""
		
		super().__init__(
				WebdriverOption(
						name="debugger_address_",
						command="debuggerAddress",
						type="experimental"
				),
				WebdriverOption(name="user_agent_", command="--user-agent=\"{value}\"", type="normal"),
				WebdriverOption(name="proxy_", command="--proxy-server=\"{value}\"", type="normal"),
				WebdriverOption(name="enable_bidi_", command="enable_bidi", type="attribute"),
		)
	
	def hide_automation(self, hide: bool):
		"""
		Adds arguments to hide automation features in Chrome.

		This method configures Chrome options to reduce the detectability of automated browsing,
		making it harder for websites to identify the browser as being controlled by automation software.

		Args:
			hide (bool): If True, adds arguments to hide automation; if False, removes them.
		"""
		
		if hide:
			self.set_argument(
					"disable_blink_features_",
					"--disable-blink-features=AutomationControlled"
			)
			self.set_argument("no_first_run_", "--no-first-run")
			self.set_argument("no_service_autorun_", "--no-service-autorun")
			self.set_argument("password_store_", "--password-store=basic")
		else:
			self.remove_argument("disable_blink_features_")
			self.remove_argument("no_first_run_")
			self.remove_argument("no_service_autorun_")
			self.remove_argument("password_store_")
	
	def renew_webdriver_options(self) -> Options:
		"""
		Creates and returns a new Chrome Options object.

		Returns a fresh instance of `webdriver.ChromeOptions`, allowing for a clean
		state of browser options to be configured.

		Returns:
			Options: A new Selenium Chrome Options object.
		"""
		
		return Options()


class ChromeStartArgs(BrowserStartArgs):
	"""
	Manages Chrome-specific browser start arguments for Selenium WebDriver.

	This class extends BrowserStartArgs and is tailored for Chrome. It defines
	command-line arguments specific to starting the Chrome browser with configurations
	suitable for WebDriver control, such as remote debugging port, user profile directory,
	headless mode, and proxy settings.

	Attributes:
		_browser_exe (Union[str, pathlib.Path]): Path to the Chrome executable.
		_debugging_port_command_line (str): Command line argument for debugging port.
		_profile_dir_command_line (str): Command line argument for profile directory.
		_headless_mode_command_line (str): Command line argument for headless mode.
		_mute_audio_command_line (str): Command line argument for mute audio.
		_user_agent_command_line (str): Command line argument for user agent.
		_proxy_server_command_line (str): Command line argument for proxy server.
		start_page_url (str): Default start page URL.
		debugging_port (Optional[int]): Current debugging port number.
		profile_dir (Optional[str]): Current profile directory path.
		headless_mode (Optional[bool]): Current headless mode status.
		mute_audio (Optional[bool]): Current mute audio status.
		user_agent (Optional[str]): Current user agent string.
		proxy_server (Optional[str]): Current proxy server address.
	"""
	
	def __init__(self, browser_exe: Union[str, pathlib.Path]):
		"""
		 Initializes ChromeStartArgs.

		Configures command-line arguments for starting the Chrome browser, including
		settings for remote debugging, user data directory, headless mode, and more.

		 Args:
			browser_exe (Union[str, pathlib.Path]): The path to the Chrome executable.
		"""
		
		super().__init__(
				browser_exe,
				"--remote-debugging-port={value}",
				"--user-data-dir=\"{value}\"",
				"--headless",
				"--mute-audio",
				"--user-agent=\"{value}\"",
				"--proxy-server=\"{value}\"",
		)


class ChromeWebDriver(BrowserWebDriver):
	"""
	Manages a Chrome browser session using Selenium WebDriver.

	This class specializes BrowserWebDriver for Google Chrome. It sets up and manages
	the lifecycle of a Chrome browser instance controlled by Selenium WebDriver,
	including starting the browser with specific options, handling sessions, and managing browser processes.

	Attributes:
		_window_rect (WindowRect): Initial window rectangle settings.
		_js_scripts (dict[str, str]): Collection of JavaScript scripts for browser interaction.
		_browser_exe (Union[str, pathlib.Path]): Path to the Chrome browser executable.
		_webdriver_path (str): Path to the ChromeDriver executable.
		_webdriver_start_args (ChromeStartArgs): Manages Chrome startup arguments.
		_webdriver_options_manager (ChromeOptionsManager): Manages Chrome browser options.
		driver (Optional[webdriver.Chrome]): Selenium Chrome WebDriver instance.
		_base_implicitly_wait (int): Base implicit wait timeout for element searching.
		_base_page_load_timeout (int): Base page load timeout for page loading operations.
		_is_active (bool): Indicates if the WebDriver instance is currently active.
		dev_tools (DevTools): Instance of DevTools for interacting with browser developer tools.
	"""
	
	def __init__(
			self,
			webdriver_path: str,
			enable_devtools: bool,
			browser_exe: Optional[Union[str, pathlib.Path]] = None,
			hide_automation: bool = True,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: bool = False,
			mute_audio: bool = False,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			implicitly_wait: int = 5,
			page_load_timeout: int = 5,
			window_rect: Optional[WindowRect] = None,
			start_page_url: str = "https://www.google.com",
	):
		"""
		Initializes the ChromeWebDriver instance for managing Chrome Browser.

		This constructor sets up the WebDriver specifically for Chrome Browser,
		configuring browser and driver paths, and applying default or user-specified settings
		for browser behavior like headless mode, proxy, and DevTools.

		Args:
			webdriver_path (str): Path to the ChromeDriver executable compatible with Chrome Browser.
			enable_devtools (bool): Enables or disables the use of DevTools for this browser instance.
			browser_exe (Optional[Union[str, pathlib.Path]]): Path to the Chrome Browser executable.
				If None, the path is automatically detected. Defaults to None.
			hide_automation (bool): Hides automation indicators in the browser if True. Defaults to True.
			debugging_port (Optional[int]): Specifies a debugging port for the browser. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory to be used. Defaults to None.
			headless_mode (bool): Runs Chrome Browser in headless mode if True. Defaults to False.
			mute_audio (bool): Mutes audio output in Chrome Browser if True. Defaults to False.
			proxy (Optional[Union[str, list[str]]]): Proxy settings for Chrome Browser.
				Can be a single proxy string or a list of proxy strings. Defaults to None.
			user_agent (Optional[str]): Custom user agent string for Chrome Browser. Defaults to None.
			implicitly_wait (int): Base implicit wait time for WebDriver element searches in seconds. Defaults to 5.
			page_load_timeout (int): Base page load timeout for WebDriver operations in seconds. Defaults to 5.
			window_rect (Optional[WindowRect]): Initial window rectangle settings for the browser window. Defaults to None.
			start_page_url (str): URL to open when the browser starts. Defaults to "https://www.google.com".
		"""
		
		if browser_exe is None:
			browser_exe = get_path_to_browser("Google Chrome")
		
		super().__init__(
				browser_exe=browser_exe,
				webdriver_path=webdriver_path,
				enable_devtools=enable_devtools,
				webdriver_start_args=ChromeStartArgs,
				webdriver_options_manager=ChromeOptionsManager,
				hide_automation=hide_automation,
				debugging_port=debugging_port,
				profile_dir=profile_dir,
				headless_mode=headless_mode,
				mute_audio=mute_audio,
				proxy=proxy,
				user_agent=user_agent,
				implicitly_wait=implicitly_wait,
				page_load_timeout=page_load_timeout,
				window_rect=window_rect,
				start_page_url=start_page_url,
		)
	
	def create_driver(self):
		"""
		Creates the Chrome webdriver instance.

		Initializes the Selenium ChromeDriver with configured options and service,
		sets up window parameters, and applies default timeouts.
		"""
		
		webdriver_options = self._webdriver_options_manager._options
		webdriver_service = Service(executable_path=self._webdriver_path)
		
		self.driver = webdriver.Chrome(options=webdriver_options, service=webdriver_service)
		
		self.set_window_rect(self._window_rect)
		self.set_driver_timeouts(
				page_load_timeout=self._base_page_load_timeout,
				implicit_wait_timeout=self._base_implicitly_wait
		)
	
	def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str):
		"""
		Connects to an existing remote Chrome WebDriver session.

		Establishes a remote connection to an already running Chrome browser session,
		allowing for session reuse and remote control.

		Args:
			command_executor (Union[str, RemoteConnection]): The URL of the remote WebDriver server or a `RemoteConnection` object.
			session_id (str): The ID of the existing WebDriver session to connect to.

		:Usage:
			command_executor, session_id = driver.get_vars_for_remote()
			new_driver = ChromeWebDriver(webdriver_path="path/to/chromedriver")
			new_driver.remote_connect_driver(command_executor, session_id)
			# Now new_driver controls the same browser session as driver
		"""
		
		self.driver = webdriver.Remote(
				command_executor=command_executor,
				options=self._webdriver_options_manager._options
		)
		self.driver.session_id = session_id
		
		self.set_driver_timeouts(
				page_load_timeout=self._base_page_load_timeout,
				implicit_wait_timeout=self._base_implicitly_wait
		)
