import pathlib
from selenium import webdriver
from typing import Optional, Union
from osn_bas.utilities import WindowRect
from osn_bas.webdrivers.types import WebdriverOption
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from osn_bas.browsers_handler import get_path_to_browser
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.BaseDriver import (
	BrowserOptionsManager,
	BrowserStartArgs,
	BrowserWebDriver
)


class YandexOptionsManager(BrowserOptionsManager):
	"""
	Manages Yandex webdriver options.

	Attributes:
		options (Options): The Yandex options object.
		debugging_port_command (str): Command-line argument for setting the debugging port.
		user_agent_command (str): Command-line argument for setting the user agent.
		proxy_command (str): Command-line argument for setting the proxy.
	"""
	
	def __init__(self):
		"""
		Initializes YandexOptionsManager.
		"""
		super().__init__(
				WebdriverOption(
						name="debugger_address_",
						command="debuggerAddress",
						type="experimental"
				),
				WebdriverOption(name="user_agent_", command="--user-agent=\"{value}\"", type="normal"),
				WebdriverOption(name="proxy_", command="--proxy-server=\"{value}\"", type="normal"),
		)
	
	def hide_automation(self, hide: bool):
		"""
		Adds arguments to hide automation features in Yandex.

		This method adds Yandex-specific arguments to disable automation detection, making the browser appear more like a regular user.

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

		Returns:
			Options: A new Selenium Yandex options object.
		"""
		return Options()


class YandexStartArgs(BrowserStartArgs):
	"""
	Manages Yandex webdriver startup arguments.

	This class extends `BrowserStartArgs` to provide specific management for Yandex browser startup command-line arguments.
	It configures arguments such as debugging port, user data directory, headless mode, mute audio, and user agent for Yandex.

	Attributes:
		browser_exe (str): Path to the browser executable.
		start_command (str): The assembled start command string for launching Yandex.
		debugging_port_command_line (str): Command-line argument format string for setting the debugging port.
		profile_dir_command_line (str): Command-line argument format string for setting the user data directory (profile directory).
		headless_mode_command_line (str): Command-line argument for launching Yandex in headless mode.
		mute_audio_command_line (str): Command-line argument for muting audio in Yandex.
		user_agent_command_line (str): Command-line argument format string for setting the user agent.
		debugging_port (Optional[int]): The debugging port number. Defaults to None.
		profile_dir (Optional[str]): The user data directory (profile directory) path. Defaults to None.
		user_agent (Optional[str]): The user agent string. Defaults to None.
		headless_mode (bool): Whether headless mode is enabled. Defaults to False.
		mute_audio (bool): Whether mute audio is enabled. Defaults to False.
	"""
	
	def __init__(self, browser_exe: Union[str, pathlib.Path]):
		"""
		 Initializes YandexStartArgs.

		 Args:
		 	browser_exe (Union[str, pathlib.Path]): The name of the Yandex executable.
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
	Controls a local Yandex webdriver instance.

	This class extends `BrowserWebDriver` to provide specific control over a local Yandex browser instance using Selenium WebDriver.
	It manages the creation, configuration, and lifecycle of a Yandex WebDriver, including options and start-up arguments.

	Attributes:
		browser_exe (str): Path to the Yandex browser executable.
		webdriver_path (str): Path to the YandexDriver executable.
		webdriver_start_args (YandexStartArgs): Manages Yandex-specific browser start-up arguments.
		webdriver_options_manager (YandexOptionsManager): Manages Yandex-specific browser options.
		window_rect (WindowRect): The browser window rectangle settings.
		webdriver_is_active (bool): Indicates if the Yandex WebDriver is currently active.
		base_implicitly_wait (int): Base implicit wait time in seconds.
		base_page_load_timeout (int): Base page load timeout in seconds.
		driver (webdriver.Yandex): Selenium Yandex WebDriver instance.
	"""
	
	def __init__(
			self,
			webdriver_path: str,
			browser_exe: Optional[Union[str, pathlib.Path]] = None,
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
		"""
		Initializes YandexWebDriver.

		Args:
			webdriver_path (str): Path to the chromedriver executable.
			browser_exe (Optional[Union[str, pathlib.Path]]): Path to the Yandex browser executable. If None, it tries to find Yandex automatically. Defaults to None.
			debugging_port (Optional[int]): Debugging port number for Yandex. Defaults to None.
			profile_dir (Optional[str]): Path to the Yandex user profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to run Yandex in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in Yandex. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses for Yandex. Defaults to None.
			user_agent (Optional[str]): User agent string for Yandex. Defaults to None.
			implicitly_wait (int): Implicit wait time in seconds for Selenium actions. Defaults to 5.
			page_load_timeout (int): Page load timeout in seconds for page loading. Defaults to 5.
			window_rect (Optional[WindowRect]): Window rectangle object to set initial window position and size. Defaults to None.
		"""
		if browser_exe is None:
			browser_exe = get_path_to_browser("Yandex")
		
		super().__init__(
				browser_exe=browser_exe,
				webdriver_path=webdriver_path,
				webdriver_start_args=YandexStartArgs,
				webdriver_options_manager=YandexOptionsManager,
				debugging_port=debugging_port,
				profile_dir=profile_dir,
				headless_mode=headless_mode,
				mute_audio=mute_audio,
				proxy=proxy,
				user_agent=user_agent,
				implicitly_wait=implicitly_wait,
				page_load_timeout=page_load_timeout,
				window_rect=window_rect,
		)
	
	def create_driver(self):
		"""
		Creates the Yandex webdriver instance.

		This method initializes and sets up the Selenium Yandex WebDriver with configured options and service.
		It also sets the window position, size, implicit wait time, and page load timeout.
		"""
		webdriver_options = self.webdriver_options_manager.options
		webdriver_service = Service(executable_path=self.webdriver_path)
		
		self.driver = webdriver.Chrome(options=webdriver_options, service=webdriver_service)
		
		self.driver.set_window_position(x=self.window_rect.x, y=self.window_rect.y)
		self.driver.set_window_size(width=self.window_rect.width, height=self.window_rect.height)
		
		self.driver.implicitly_wait(self.base_implicitly_wait)
		self.driver.set_page_load_timeout(self.base_page_load_timeout)
	
	def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str):
		"""
		Connects to an existing remote Yandex WebDriver session.

		This method establishes a connection to a remote Selenium WebDriver server and reuses an existing browser session.
		It allows you to control a browser instance that is already running remotely, given the command executor URL and session ID of that session.

		Args:
			command_executor (Union[str, RemoteConnection]): The URL of the remote WebDriver server or a `RemoteConnection` object.
			session_id (str): The ID of the existing WebDriver session to connect to.
		"""
		self.driver = webdriver.Remote(
				command_executor=command_executor,
				options=self.webdriver_options_manager.options
		)
		self.driver.session_id = session_id
		
		self.driver.implicitly_wait(self.base_implicitly_wait)
		self.driver.set_page_load_timeout(self.base_page_load_timeout)
