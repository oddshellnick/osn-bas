from selenium import webdriver
from typing import Optional, Union
from osn_bas.utilities import WindowRect
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from osn_bas.webdrivers.BaseDriver import (
	BrowserOptionsManager,
	BrowserStartArgs,
	BrowserWebDriver,
	EmptyWebDriver
)


class EdgeOptionsManager(BrowserOptionsManager):
	"""
	Manages Edge webdriver options.

	Attributes:
		options (Options): The Edge options object.
		debugging_port_command (str): Command-line argument for setting the debugging port.
		user_agent_command (str): Command-line argument for setting the user agent.
		proxy_command (str): Command-line argument for setting the proxy.
		debugging_port (Optional[int]): The debugging port number. Defaults to None.
		user_agent (Optional[list[str]]): The user agent string as a list of parts. Defaults to None.
		proxy (Optional[Union[str, list[str]]]): The proxy server address or a list of addresses. Defaults to None.

	:Usage:
		options_manager = EdgeOptionsManager(debugging_port=9222, user_agent="MyUserAgent", proxy="127.0.0.1:8080")
		options_manager.hide_automation()
	"""
	
	def __init__(
			self,
			debugging_port: Optional[int] = None,
			user_agent: Optional[list[str]] = None,
			proxy: Optional[Union[str, list[str]]] = None,
	):
		"""
		Initializes EdgeOptionsManager.

		Args:
			debugging_port (Optional[int]): Port for remote debugging. Defaults to None.
			user_agent (Optional[list[str]]): User agent string or list of strings. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.

		:Usage:
			 options_manager = EdgeOptionsManager(debugging_port=9222, user_agent=["My","User","Agent"], proxy="127.0.0.1:8080")
		"""
		super().__init__(
				"127.0.0.1:%d",
				"user-agent=%s",
				"--proxy-server=%s",
				debugging_port,
				user_agent,
				proxy
		)
	
	def hide_automation(self):
		"""
		Adds arguments to hide automation features.

		:Usage:
			options_manager = EdgeOptionsManager()
			options_manager.hide_automation()
		"""
		self.options.add_argument("--disable-blink-features=AutomationControlled")
		self.options.add_argument("--no-first-run")
		self.options.add_argument("--no-service-autorun")
		self.options.add_argument("--password-store=basic")
	
	def renew_webdriver_options(self) -> Options:
		"""
		Creates and returns a new Options object.

		Returns:
			Options: A new Selenium Edge options object.

		:Usage:
			options_manager = EdgeOptionsManager()
			new_options = options_manager.renew_webdriver_options()
		"""
		return Options()


class EdgeStartArgs(BrowserStartArgs):
	"""
	Manages Edge webdriver startup arguments.

	Attributes:
		start_command (str): The assembled start command.
		browser_exe (str): Path to the browser executable.
		debugging_port_command_line (str): Command-line argument for the debugging port.
		profile_dir_command_line (str): Command-line argument for the webdriver directory.
		headless_mode_command_line (str): Command-line argument for headless mode.
		mute_audio_command_line (str): Command-line argument for muting audio.
		debugging_port (Optional[int]): The debugging port number. Defaults to None.
		webdriver_dir (Optional[str]): The webdriver directory. Defaults to None.
		headless_mode (bool): Whether to run in headless mode. Defaults to False.
		mute_audio (bool): Whether to mute audio. Defaults to False.
	"""
	
	def __init__(
			self,
			browser_exe: str = "msedge.exe",
			profile_dir: Optional[str] = None,
			debugging_port: Optional[int] = None,
			headless_mode: bool = False,
			mute_audio: bool = False,
	):
		"""
		Initializes EdgeStartArgs.

		Args:
			browser_exe (str): The name of the Yandex Browser executable. Defaults to "msedge.exe".
			profile_dir (Optional[str]): Directory for profile storing. Defaults to None.
			debugging_port (Optional[int]): Port for remote debugging. Defaults to None.
			headless_mode (bool): Run Yandex in headless mode. Defaults to False.
			mute_audio (bool): Mute audio in Yandex. Defaults to False.
		"""
		super().__init__(
				browser_exe,
				"--remote-debugging-port=%d",
				'--user-data-dir="%s"',
				"--headless=new",
				"--mute-audio",
				profile_dir,
				debugging_port,
				headless_mode,
				mute_audio,
		)


class EdgeWebDriver(BrowserWebDriver):
	"""
	Controls an Edge webdriver instance.

	Attributes:
		browser_exe (str): Path to the browser executable.
		bsa_debugging_port_command_line (str): BrowserStartArgs command-line argument for debugging port.
		bsa_webdriver_dir_command_line (str): BrowserStartArgs command-line argument for webdriver directory.
		bsa_headless_mode_command_line (str): BrowserStartArgs command-line argument for headless mode.
		bsa_mute_audio_command_line (str): BrowserStartArgs command-line argument for muting audio.
		bom_debugging_port_command (str): BrowserOptionsManager command for debugging port.
		bom_user_agent_command (str): BrowserOptionsManager command for user agent.
		bom_proxy_command (str): BrowserOptionsManager command for proxy.
		webdriver_path (str): Path to the webdriver executable.
		webdriver_start_args (EdgeStartArgs): Manages browser start-up arguments.
		webdriver_options_manager (EdgeOptionsManager): Manages browser options.
		debugging_port (Optional[int]): The debugging port number. Defaults to None.
		webdriver_dir (Optional[str]): The webdriver directory. Defaults to None.
		headless_mode (bool): Whether to run in headless mode. Defaults to False.
		mute_audio (bool): Whether to mute audio. Defaults to False.
		user_agent (Optional[list[str]]): The user agent. Defaults to None.
		proxy (Optional[Union[str, list[str]]]): The proxy server(s). Defaults to None.
		window_rect (WindowRect): The browser window rectangle.
		webdriver_is_active (bool): Indicates if the webdriver is currently active.
		webdriver_service (Optional[Service]): The webdriver service. Defaults to None.
		webdriver_options (Optional[Options]): The webdriver options. Defaults to None.
	"""
	
	def __init__(
			self,
			webdriver_path: str,
			webdriver_start_args: EdgeStartArgs = EdgeStartArgs(),
			webdriver_options_manager: EdgeOptionsManager = EdgeOptionsManager(),
			implicitly_wait: int = 5,
			page_load_timeout: int = 5,
			window_rect: WindowRect = WindowRect(),
	):
		"""
		Initializes EdgeWebDriver.

		Args:
			webdriver_path (str): Path to the msedgedriver executable.
			webdriver_start_args (EdgeStartArgs): Startup arguments for Edge. Defaults to EdgeStartArgs().
			webdriver_options_manager (EdgeOptionsManager): Options manager for Edge. Defaults to EdgeOptionsManager().
			implicitly_wait (int): Implicit wait time in seconds. Defaults to 5.
			page_load_timeout (int): Page load timeout in seconds. Defaults to 5.
			window_rect (WindowRect): Window rectangle for setting window position and size. Defaults to WindowRect().
		"""
		super().__init__(
				"msedge.exe",
				"--remote-debugging-port=%d",
				'--user-data-dir="%s"',
				"--headless=new",
				"--mute-audio",
				"127.0.0.1:%d",
				"user-agent=%s",
				"--proxy-server=%s",
				webdriver_path,
				webdriver_start_args,
				webdriver_options_manager,
				implicitly_wait,
				page_load_timeout,
				window_rect,
		)
	
	def create_driver(self):
		"""
		Creates the Edge webdriver instance.

		:Usage:
			webdriver = EdgeWebDriver(webdriver_path="/path/to/msedgedriver")
			webdriver.create_driver()
		"""
		self.webdriver_service = Service(executable_path=self.webdriver_path)
		self.webdriver_options = self.webdriver_options_manager.options
		
		self.driver = webdriver.Edge(options=self.webdriver_options, service=self.webdriver_service)
		
		self.driver.set_window_position(x=self.window_rect.x, y=self.window_rect.y)
		self.driver.set_window_size(width=self.window_rect.width, height=self.window_rect.height)
		
		self.driver.implicitly_wait(self.base_implicitly_wait)
		self.driver.set_page_load_timeout(self.base_page_load_timeout)
	
	def renew_bas_and_bom(self):
		"""
		Renews the BrowserStartArgs and BrowserOptionsManager.

		:Usage:
			 webdriver = EdgeWebDriver(webdriver_path="/path/to/msedgedriver")
			 webdriver.renew_bas_and_bom()
		"""
		self.webdriver_start_args = EdgeStartArgs(
				self.browser_exe,
				self.webdriver_dir,
				self.debugging_port,
				self.headless_mode,
				self.mute_audio
		)
		self.webdriver_options_manager = EdgeOptionsManager(self.debugging_port, self.user_agent, self.proxy)


class EdgeRemoteWebDriver(EmptyWebDriver):
	"""
	Controls a remote Edge webdriver instance.

	Attributes:
		base_implicitly_wait (int): The base implicit wait time in seconds.
		base_page_load_timeout (int): The base page load timeout in seconds.
		driver (webdriver.Remote | None): Selenium remote webdriver instance. Defaults to None.
		command_executor (str): The address of the remote webdriver server.
		session_id (str): The session ID of the remote webdriver.
		webdriver_options_manager (EdgeOptionsManager): The options manager for the webdriver.

	:Usage:
		remote_webdriver = EdgeRemoteWebDriver(command_executor="http://127.0.0.1:4444", session_id="some_session_id")
		remote_webdriver.create_driver()
	"""
	
	def __init__(
			self,
			command_executor: str,
			session_id: str,
			webdriver_options_manager: EdgeOptionsManager = EdgeOptionsManager(),
			implicitly_wait: int = 5,
			page_load_timeout: int = 5,
	):
		"""
		Initializes a new instance of the EdgeRemoteWebDriver class.

		Args:
			command_executor (str): The address of the remote webdriver server.
			session_id (str): The session ID of the existing webdriver session.
			webdriver_options_manager (EdgeOptionsManager): An instance of EdgeOptionsManager for customizing browser options. Defaults to EdgeOptionsManager().
			implicitly_wait (int): The implicit wait timeout in seconds. Defaults to 5.
			page_load_timeout (int): The page load timeout in seconds. Defaults to 5.

		:Usage:
		   remote_webdriver = EdgeRemoteWebDriver(command_executor="http://127.0.0.1:4444", session_id="your_session_id")
		"""
		super().__init__(implicitly_wait, page_load_timeout)
		
		self.command_executor = command_executor
		self.session_id = session_id
		self.webdriver_options_manager = webdriver_options_manager
		self.driver = None
	
	def close_webdriver(self):
		self.driver.close()
		self.driver = None
	
	def create_driver(
			self,
			command_executor: Optional[str] = None,
			session_id: Optional[str] = None
	):
		"""
		Create a remote webdriver instance connected to an Edge browser.

		Args:
			command_executor (Optional[str]): URL of the remote webdriver server. If provided will overwrite server URL during initialization. Defaults to None.
			session_id (Optional[str]): ID of an existing session to connect to. If provided, will overwrite session ID specified during initialization. Defaults to None.

		:Usage:
			driver = EdgeRemoteWebDriver("http://localhost:4444/wd/hub", "my_session")
			driver.create_driver()
			# Or for subsequent calls with the same parameters:
			driver.create_driver()
			# Or to connect with different session ID:
			driver.create_driver(session_id="another_session")
		"""
		if command_executor is not None:
			self.command_executor = command_executor
		
		if session_id is not None:
			self.session_id = session_id
		
		self.driver = webdriver.Remote(
				command_executor=self.command_executor,
				options=self.webdriver_options_manager.options
		)
		
		self.close_window()
		self.driver.session_id = self.session_id
		self.switch_to_window()
		
		self.driver.implicitly_wait(self.base_implicitly_wait)
		self.driver.set_page_load_timeout(self.base_page_load_timeout)
