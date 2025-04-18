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


class YandexOptionsManager(BrowserOptionsManager):
	"""
	Manages Yandex Browser-specific options for Selenium WebDriver.

	This class extends BrowserOptionsManager to provide specific configurations
	for Yandex Browser options, such as experimental options and arguments.

	Attributes:
		_options (webdriver.ChromeOptions): Yandex Browser options object, which is based on ChromeOptions.
		_debugging_port_command (WebdriverOption): Configuration for debugging port option.
		_user_agent_command (WebdriverOption): Configuration for user agent option.
		_proxy_command (WebdriverOption): Configuration for proxy option.
		_enable_bidi_command (WebdriverOption): Configuration for enable BiDi option.
	"""
	
	def __init__(self):
		"""
		Initializes YandexOptionsManager.

		Sets up the Yandex Browser options manager with specific option configurations for
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
		Adds arguments to hide automation features in Yandex Browser.

		This method adds Yandex Browser-specific arguments to disable automation detection, making the browser appear more like a regular user.

		Args:
			hide (bool): If True, adds arguments to hide automation; otherwise, removes them.
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
		Creates and returns a new Options object.

		Returns a fresh instance of `webdriver.ChromeOptions`, as Yandex Browser is based on Chromium,
		allowing for a clean state of browser options to be configured.

		Returns:
			Options: A new Selenium Yandex Browser options object, based on ChromeOptions.
		"""
		
		return Options()


class YandexStartArgs(BrowserStartArgs):
	"""
	Manages Yandex Browser-specific browser start arguments for Selenium WebDriver.

	This class extends BrowserStartArgs and is tailored for Yandex Browser. It defines
	command-line arguments specific to starting the Yandex Browser with configurations
	suitable for WebDriver control, such as remote debugging port, user profile directory,
	headless mode, and proxy settings.

	Attributes:
		_browser_exe (Union[str, pathlib.Path]): Path to the Yandex Browser executable.
		_debugging_port_command_line (str): Command line argument for debugging port.
		_profile_dir_command_line (str): Command line argument for profile directory.
		_headless_mode_command_line (str): Command line argument for headless mode.
		_mute_audio_command_line (str): Command line argument for mute audio.
		_user_agent_command_line (str): Command line argument for user agent.
		_proxy_server_command_line (str): Command line argument for proxy server.
		start_page_url (str): Default start page URL, set to Yandex homepage.
		debugging_port (Optional[int]): Current debugging port number.
		profile_dir (Optional[str]): Current profile directory path.
		headless_mode (Optional[bool]): Current headless mode status.
		mute_audio (Optional[bool]): Current mute audio status.
		user_agent (Optional[str]): Current user agent string.
		proxy_server (Optional[str]): Current proxy server address.
	"""
	
	def __init__(self, browser_exe: Union[str, pathlib.Path]):
		"""
		 Initializes YandexStartArgs.

		Configures command-line arguments for starting the Yandex Browser, including
		settings for remote debugging, user data directory, headless mode, and more.

		 Args:
		 	browser_exe (Union[str, pathlib.Path]): The path to the Yandex executable.
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


class YandexWebDriver(BrowserWebDriver):
	"""
	Manages a Yandex Browser session using Selenium WebDriver.

	This class specializes BrowserWebDriver for Yandex Browser. It sets up and manages
	the lifecycle of a Yandex Browser instance controlled by Selenium WebDriver,
	including starting the browser with specific options, handling sessions, and managing browser processes.
	Yandex Browser is based on Chromium, so it uses ChromeOptions and ChromeDriver.

	Attributes:
		_window_rect (WindowRect): Initial window rectangle settings.
		_js_scripts (dict[str, str]): Collection of JavaScript scripts for browser interaction.
		_browser_exe (Union[str, pathlib.Path]): Path to the Yandex Browser executable.
		_webdriver_path (str): Path to the ChromeDriver executable (Yandex Browser compatible).
		_webdriver_start_args (YandexStartArgs): Manages Yandex Browser startup arguments.
		_webdriver_options_manager (YandexOptionsManager): Manages Yandex Browser options.
		driver (Optional[webdriver.Chrome]): Selenium Chrome WebDriver instance, used for Yandex Browser.
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
			start_page_url: str = "https://www.yandex.com",
	):
		"""
		Initializes the YandexWebDriver instance for managing Yandex Browser.

		This constructor sets up the WebDriver specifically for Yandex Browser,
		configuring browser and driver paths, and applying default or user-specified settings
		for browser behavior like headless mode, proxy, and DevTools.

		Args:
			webdriver_path (str): Path to the ChromeDriver executable compatible with Yandex Browser.
			enable_devtools (bool): Enables or disables the use of DevTools for this browser instance.
			browser_exe (Optional[Union[str, pathlib.Path]]): Path to the Yandex Browser executable.
				If None, the path is automatically detected. Defaults to None.
			hide_automation (bool): Hides automation indicators in the browser if True. Defaults to True.
			debugging_port (Optional[int]): Specifies a debugging port for the browser. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory to be used. Defaults to None.
			headless_mode (bool): Runs Yandex Browser in headless mode if True. Defaults to False.
			mute_audio (bool): Mutes audio output in Yandex Browser if True. Defaults to False.
			proxy (Optional[Union[str, list[str]]]): Proxy settings for Yandex Browser.
				Can be a single proxy string or a list of proxy strings. Defaults to None.
			user_agent (Optional[str]): Custom user agent string for Yandex Browser. Defaults to None.
			implicitly_wait (int): Base implicit wait time for WebDriver element searches in seconds. Defaults to 5.
			page_load_timeout (int): Base page load timeout for WebDriver operations in seconds. Defaults to 5.
			window_rect (Optional[WindowRect]): Initial window rectangle settings for the browser window. Defaults to None.
			start_page_url (str): URL to open when the browser starts. Defaults to "https://www.yandex.com".
		"""
		
		if browser_exe is None:
			browser_exe = get_path_to_browser("Yandex")
		
		super().__init__(
				browser_exe=browser_exe,
				webdriver_path=webdriver_path,
				enable_devtools=enable_devtools,
				webdriver_start_args=YandexStartArgs,
				webdriver_options_manager=YandexOptionsManager,
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
		Creates the Yandex webdriver instance.

		This method initializes and sets up the Selenium Yandex WebDriver using ChromeDriver with configured options and service.
		It also sets the window position, size, implicit wait time, and page load timeout.
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
		Connects to an existing remote Yandex WebDriver session.

		This method establishes a connection to a remote Selenium WebDriver server and reuses an existing browser session of Yandex Browser.
		It allows you to control a browser instance that is already running remotely, given the command executor URL and session ID of that session.

		Args:
			command_executor (Union[str, RemoteConnection]): The URL of the remote WebDriver server or a `RemoteConnection` object.
			session_id (str): The ID of the existing WebDriver session to connect to.

		:Usage:
		  command_executor, session_id = driver.get_vars_for_remote()
		  new_driver = YandexWebDriver(webdriver_path="path/to/chromedriver")
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
