import trio
import pathlib
from random import random
from subprocess import Popen
from selenium import webdriver
from typing import Any, Optional, Union
from osn_bas.utilities import WindowRect
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from osn_windows_cmd.taskkill.parameters import TaskKillTypes
from osn_bas.webdrivers.BaseDriver.dev_tools.manager import DevTools
from osn_bas.webdrivers.BaseDriver.start_args import BrowserStartArgs
from osn_windows_cmd.taskkill import (
	ProcessID,
	taskkill_windows
)
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.BaseDriver.options import (
	BrowserOptionsManager
)
from osn_bas.webdrivers.functions import (
	find_browser_previous_session,
	read_js_scripts
)
from osn_windows_cmd.netstat import (
	get_localhost_minimum_free_port,
	get_localhost_processes_with_pids
)


class BrowserWebDriver:
	"""
	Manages a browser session using Selenium WebDriver.

	This class provides an interface to control a web browser using Selenium WebDriver.
	It supports various browser configurations, including headless mode, proxy settings,
	user agent manipulation, and DevTools integration. It also handles browser and
	WebDriver lifecycle, including startup, shutdown, and session management.

	Attributes:
		_window_rect (WindowRect): Initial window rectangle settings.
		_js_scripts (dict[str, str]): Collection of JavaScript scripts for browser interaction.
		_browser_exe (Union[str, pathlib.Path]): Path to the browser executable.
		_webdriver_path (str): Path to the WebDriver executable.
		_webdriver_start_args (BrowserStartArgs): Manages WebDriver startup arguments.
		_webdriver_options_manager (BrowserOptionsManager): Manages browser options.
		driver (Optional[Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox]]):
			Selenium WebDriver instance. Initialized to None before driver creation.
		_base_implicitly_wait (int): Base implicit wait timeout for element searching.
		_base_page_load_timeout (int): Base page load timeout for page loading operations.
		_is_active (bool): Indicates if the WebDriver instance is currently active.
		dev_tools (DevTools): Instance of DevTools for interacting with browser developer tools.
	"""
	
	def __init__(
			self,
			browser_exe: Union[str, pathlib.Path],
			webdriver_path: str,
			enable_devtools: bool,
			webdriver_start_args: type,
			webdriver_options_manager: type,
			hide_automation: bool = False,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: bool = False,
			mute_audio: bool = False,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			implicitly_wait: int = 5,
			page_load_timeout: int = 5,
			window_rect: Optional[WindowRect] = None,
			start_page_url: str = "",
	):
		"""
		Initializes the BrowserWebDriver instance.

		Configures and sets up the WebDriver for browser automation, including
		settings for browser executable path, WebDriver path, and various browser options.

		Args:
			browser_exe (Union[str, pathlib.Path]): Path to the browser executable.
			webdriver_path (str): Path to the WebDriver executable.
			enable_devtools (bool): Enables or disables DevTools integration.
			webdriver_start_args (type[BrowserStartArgs]): Class for managing WebDriver startup arguments.
			webdriver_options_manager (type[BrowserOptionsManager]): Class for managing browser options.
			hide_automation (bool): Hides automation indicators in the browser. Defaults to False.
			debugging_port (Optional[int]): Specifies a debugging port for the browser. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (bool): Runs the browser in headless mode if True. Defaults to False.
			mute_audio (bool): Mutes audio output in the browser. Defaults to False.
			proxy (Optional[Union[str, list[str]]]): Proxy settings for the browser. Can be a single proxy string or a list. Defaults to None.
			user_agent (Optional[str]): Custom user agent string for the browser. Defaults to None.
			implicitly_wait (int): Base implicit wait time for WebDriver element searches. Defaults to 5 seconds.
			page_load_timeout (int): Base page load timeout for WebDriver operations. Defaults to 5 seconds.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to a default WindowRect instance if None.
			start_page_url (str): The URL to navigate to when the browser starts. Defaults to an empty string.
		"""
		
		if window_rect is None:
			window_rect = WindowRect()
		
		self._window_rect = window_rect
		self._js_scripts = read_js_scripts()
		self._browser_exe = browser_exe
		self._webdriver_path = webdriver_path
		
		self._webdriver_start_args: BrowserStartArgs = webdriver_start_args(browser_exe=browser_exe)
		
		self._webdriver_options_manager: BrowserOptionsManager = webdriver_options_manager()
		self.driver: Optional[Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox]] = None
		self._base_implicitly_wait = implicitly_wait
		self._base_page_load_timeout = page_load_timeout
		self._is_active = False
		self.dev_tools = DevTools(self)
		
		self.update_settings(
				enable_devtools=enable_devtools,
				hide_automation=hide_automation,
				debugging_port=debugging_port,
				profile_dir=profile_dir,
				headless_mode=headless_mode,
				mute_audio=mute_audio,
				proxy=proxy,
				user_agent=user_agent,
				start_page_url=start_page_url,
		)
	
	def switch_to_window(self, window: Optional[Union[str, int]] = None):
		"""
		Switches focus to the specified window.

		Allows switching the WebDriver's focus to a different browser window or tab.
		Windows can be specified by their handle, index, or name.

		Args:
			window (Optional[Union[str, int]]): The name, index, or handle of the window to switch to.
				If a string, it's treated as window name or handle. If an integer, it's the window index (0-based).
				If None, switches to the current window. Defaults to None.
		"""
		
		if isinstance(window, str):
			self.driver.switch_to.window(window)
		elif isinstance(window, int):
			self.driver.switch_to.window(self.driver.window_handles[window])
		else:
			self.driver.switch_to.window(self.driver.current_window_handle)
	
	def close_window(self, window: Optional[Union[str, int]] = None):
		"""
		Closes the specified window.

		Closes a browser window or tab. If multiple windows are open, it's possible to specify
		which window to close by handle, index, or name. After closing, if there are still
		windows open, the driver switches focus to the last window in the handles list.

		Args:
			window (Optional[Union[str, int]]): The name, index, or handle of the window to close.
				If a string, it's treated as window name or handle. If an integer, it's the window index (0-based).
				If None, closes the current window. Defaults to None.
		"""
		
		if window is not None:
			switch_to_new_window = window == self.driver.current_window_handle
		
			self.switch_to_window(window)
			self.driver.close()
		
			if switch_to_new_window and len(self.driver.window_handles) > 0:
				self.switch_to_window(-1)
	
	def close_all_windows(self):
		"""
		Closes all open windows.

		Iterates through all window handles and closes each window associated with the WebDriver instance.
		This effectively closes the entire browser session managed by the driver.
		"""
		
		for window in self.driver.window_handles:
			self.close_window(window)
	
	@property
	def current_url(self) -> str:
		"""
		Gets the current URL.

		Retrieves the URL of the current page loaded in the browser window under WebDriver control.

		Returns:
			str: The current URL of the webpage.
		"""
		
		return self.driver.current_url
	
	def set_implicitly_wait_timeout(self, timeout: float):
		"""
		Sets the implicit wait timeout for WebDriver element searches.

		Configures the implicit wait time, which is the maximum time WebDriver will wait
		when searching for elements before throwing a `NoSuchElementException`. This setting
		applies globally to all element searches for the duration of the WebDriver session.

		Args:
			timeout (float): The implicit wait timeout value in seconds.
		"""
		
		self.driver.implicitly_wait(timeout)
	
	def set_page_load_timeout(self, timeout: float):
		"""
		Sets the page load timeout for WebDriver operations.

		Defines the maximum time WebDriver will wait for a page to fully load before timing out
		and throwing a `TimeoutException`. This is useful to prevent tests from hanging indefinitely
		on slow-loading pages.

		Args:
			timeout (float): The page load timeout value in seconds.
		"""
		
		self.driver.set_page_load_timeout(timeout)
	
	def set_driver_timeouts(self, page_load_timeout: float, implicit_wait_timeout: float):
		"""
		Sets both page load timeout and implicit wait timeout for WebDriver.

		A convenience method to set both the page load timeout and the implicit wait timeout
		in a single operation. This can simplify timeout configuration at the start of tests or
		when adjusting timeouts dynamically.

		Args:
			page_load_timeout (float): The page load timeout value in seconds.
			implicit_wait_timeout (float): The implicit wait timeout value in seconds.
		"""
		
		self.set_page_load_timeout(page_load_timeout)
		self.set_implicitly_wait_timeout(implicit_wait_timeout)
	
	def update_times(
			self,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	):
		"""
		Updates the implicit wait and page load timeout.

		Updates the WebDriver's timeouts, potentially using temporary values for specific operations.
		If temporary values are provided, they are used; otherwise, the base default timeouts are used
		with a small random addition to avoid potential caching or timing issues.

		Args:
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds. If provided, overrides the base timeout temporarily. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds. If provided, overrides the base timeout temporarily. Defaults to None.
		"""
		
		if temp_implicitly_wait:
			implicitly_wait = temp_implicitly_wait + random()
		else:
			implicitly_wait = self._base_implicitly_wait + random()
		
		if temp_page_load_timeout:
			page_load_timeout = temp_page_load_timeout + random()
		else:
			page_load_timeout = self._base_page_load_timeout + random()
		
		self.set_driver_timeouts(
				page_load_timeout=page_load_timeout,
				implicit_wait_timeout=implicitly_wait
		)
	
	def find_inner_web_element(
			self,
			parent_element: WebElement,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None,
	) -> WebElement:
		"""
		Finds a single web element within another element.

		Searches for a specific web element that is a descendant of a given parent web element.
		This is useful for locating elements within a specific section or component of a webpage.

		Args:
			parent_element (WebElement): The parent web element to search within. The search is scoped to this element's descendants.
			by (By): Locator strategy to use for finding the element (e.g., By.ID, By.XPATH).
			value (str): Locator value. The actual string used by the locator strategy to find the element.
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Overrides default if provided. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Overrides default if provided. Defaults to None.

		Returns:
			WebElement: The found web element. If no element is found within the timeout, a `NoSuchElementException` is raised.
		"""
		
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		return parent_element.find_element(by, value)
	
	def find_inner_web_elements(
			self,
			parent_element: WebElement,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None,
	) -> list[WebElement]:
		"""
		Finds multiple web elements within another element.

		Searches for all web elements that match the given criteria and are descendants of a
		specified parent web element. Returns a list of all matching elements found within the parent.

		Args:
			parent_element (WebElement): The parent web element to search within. The search is limited to this element's children.
			by (By): Locator strategy to use (e.g., By.CLASS_NAME, By.CSS_SELECTOR).
			value (str): Locator value. Used in conjunction with the 'by' strategy to locate elements.
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			list[WebElement]: A list of found web elements. Returns an empty list if no elements are found.
		"""
		
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		return parent_element.find_elements(by, value)
	
	def find_web_element(
			self,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> WebElement:
		"""
		Finds a single web element on the page.

		Searches the entire webpage DOM for the first web element that matches the specified locator
		strategy and value. Returns the found element or raises an exception if no element is found within the timeout.

		Args:
			by (By): Locator strategy to use (e.g., By.ID, By.NAME).
			value (str): Locator value. Used with the 'by' strategy to identify the element.
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			WebElement: The found web element.

		Raises:
			selenium.common.exceptions.NoSuchElementException: If no element is found within the implicit wait timeout.
		"""
		
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		return self.driver.find_element(by, value)
	
	def find_web_elements(
			self,
			by: By,
			value: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	) -> list[WebElement]:
		"""
		Finds multiple web elements on the page.

		Searches the entire webpage for all web elements that match the specified locator strategy and value.
		Returns a list containing all matching elements. If no elements are found, an empty list is returned.

		Args:
			by (By): Locator strategy (e.g., By.TAG_NAME, By.LINK_TEXT).
			value (str): Locator value. Used with the 'by' strategy to locate elements.
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			list[WebElement]: A list of found web elements. Returns an empty list if no elements are found.
		"""
		
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		return self.driver.find_elements(by, value)
	
	def execute_js_script(self, script: str, *args) -> Any:
		"""
		Executes a JavaScript script in the current browser context.

		Executes arbitrary JavaScript code within the currently loaded webpage. This allows for
		performing actions that are not directly supported by WebDriver commands, such as complex
		DOM manipulations or accessing browser APIs.

		Args:
			script (str): The JavaScript code to execute as a string.
			*args: Arguments to pass to the JavaScript script. These are accessible in the script as `arguments[0]`, `arguments[1]`, etc.

		Returns:
			Any: The result of the JavaScript execution. JavaScript return values are converted to Python types.
				For example, JavaScript objects become Python dictionaries, arrays become lists, and primitives are converted directly.
		"""
		
		return self.driver.execute_script(script, *args)
	
	def get_element_css_style(self, element: WebElement) -> dict[str, str]:
		"""
		Retrieves the computed CSS style of a WebElement.

		Uses JavaScript to get all computed CSS properties and their values for a given web element.
		Returns a dictionary where keys are CSS property names and values are their computed values.

		Args:
			element (WebElement): The WebElement for which to retrieve the CSS style.

		Returns:
			dict[str, str]: A dictionary of CSS property names and their computed values as strings.
		"""
		
		return self.execute_js_script(self._js_scripts["get_element_css"], element)
	
	def get_vars_for_remote(self) -> tuple[RemoteConnection, str]:
		"""
		Gets variables necessary to create a remote WebDriver instance.

		Provides the command executor and session ID of the current WebDriver instance.
		These are needed to re-establish a connection to the same browser session from a different WebDriver client,
		for example, in a distributed testing environment.

		Returns:
			tuple[RemoteConnection, str]: A tuple containing the command executor (for establishing connection) and session ID (for session identification).
		"""
		
		return self.driver.command_executor, self.driver.session_id
	
	def hover_element(self, element: WebElement, duration: int = 250):
		"""
		Hovers the mouse over an element.

		Simulates a mouse hover action over a specified web element. This can trigger hover effects
		in the webpage, such as dropdown menus or tooltips.

		Args:
			element (WebElement): The element to hover over.
			duration (int): Duration of the hover action in milliseconds. Defaults to 250ms.
		"""
		
		ActionChains(driver=self.driver, duration=duration).move_to_element(element).perform()
	
	@property
	def html(self) -> str:
		"""
		Gets the current page source.

		Retrieves the HTML source code of the currently loaded webpage. This is useful for
		inspecting the page structure and content, especially for debugging or data extraction purposes.

		Returns:
			str: The HTML source code of the current page.
		"""
		
		return self.driver.page_source
	
	@property
	def is_active(self) -> bool:
		"""
		Checks if the WebDriver instance is currently active and connected.

		This property provides a way to determine the current status of the WebDriver.
		It reflects whether the WebDriver is initialized and considered operational.

		Returns:
			bool: True if the WebDriver is active, False otherwise.
		"""
		
		return self._is_active
	
	def open_new_tab(self, link: str = ""):
		"""
		Opens a new tab with the given URL.

		Opens a new browser tab and optionally navigates it to a specified URL. If no URL is provided, a blank tab is opened.

		Args:
			link (str): URL to open in the new tab. If empty, opens a blank tab. Defaults to "".
		"""
		
		self.execute_js_script(self._js_scripts["open_new_tab"], link)
	
	@property
	def rect(self) -> WindowRect:
		"""
		Gets the window rectangle.

		Retrieves the current position and size of the browser window as a `WindowRect` object.
		This object contains the x and y coordinates of the window's top-left corner, as well as its width and height.

		Returns:
			WindowRect: The window rectangle object containing x, y, width, and height.
		"""
		
		window_rect = self.driver.get_window_rect()
		
		return WindowRect(
				window_rect["x"],
				window_rect["y"],
				window_rect["width"],
				window_rect["height"]
		)
	
	def refresh_webdriver(self):
		"""
		Refreshes the current page.

		Reloads the currently loaded webpage in the browser. This action fetches the latest version of the page from the server.
		"""
		
		self.driver.refresh()
	
	def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str):
		"""
		Connects to an existing remote WebDriver session.

		This method establishes a connection to a remote Selenium WebDriver server and reuses an existing browser session, instead of creating a new one.
		It's useful when you want to attach to an already running browser instance, managed by a remote WebDriver service like Selenium Grid or cloud-based Selenium providers.

		Args:
			command_executor (Union[str, RemoteConnection]): The URL of the remote WebDriver server or a `RemoteConnection` object.
			session_id (str): The ID of the existing WebDriver session to connect to.

		Raises:
			NotImplementedError: This function must be implemented in child classes.
		"""
		
		raise NotImplementedError("This function must be implemented in child classes.")
	
	def set_start_page_url(self, start_page_url: str):
		self._webdriver_start_args.start_page_url = start_page_url
	
	def set_user_agent(self, user_agent: Optional[str]):
		"""
		Sets the user agent.

		Configures the browser to use a specific user agent string. Overriding the default user agent
		can be useful for testing website behavior under different browser or device conditions, or for privacy purposes.

		Args:
			user_agent (Optional[str]): User agent string to use. If None, the user agent setting is removed, reverting to the browser's default.
		"""
		
		self._webdriver_start_args.user_agent = user_agent
	
	def set_headless_mode(self, headless_mode: bool):
		"""
		Sets headless mode.

		Enables or disables headless browsing. In headless mode, the browser runs in the background without a visible UI.
		This is often used for automated testing and scraping to save resources and improve performance.

		Args:
			headless_mode (bool): Whether to start the browser in headless mode. True for headless, False for visible browser UI.
		"""
		
		self._webdriver_start_args.headless_mode = headless_mode
	
	def set_mute_audio(self, mute_audio: bool):
		"""
		Sets mute audio mode.

		Configures the browser to mute or unmute audio output. Muting audio can be useful in automated testing
		environments to prevent sound from interfering with tests or to conserve system resources.

		Args:
			mute_audio (bool): Whether to mute audio in the browser. True to mute, False to unmute.
		"""
		
		self._webdriver_start_args.mute_audio = mute_audio
	
	def set_proxy(self, proxy: Optional[Union[str, list[str]]]):
		"""
		Sets the proxy.

		Configures the browser to use a proxy server for network requests. This can be a single proxy server or a list
		of proxy servers, from which one will be randomly selected for use. Proxies are used to route browser traffic
		through an intermediary server, often for anonymity, security, or accessing geo-restricted content.

		Args:
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. If a list is provided, a proxy will be randomly chosen from the list.
				If None, proxy settings are removed.
		"""
		
		self._webdriver_start_args.proxy_server = proxy
	
	def set_profile_dir(self, profile_dir: Optional[str]):
		"""
		Sets the profile directory.

		Specifies a custom browser profile directory to be used by the browser instance. Browser profiles store user-specific
		data such as bookmarks, history, cookies, and extensions. Using profiles allows for persistent browser settings
		across sessions and can be useful for testing with specific browser states.

		Args:
			profile_dir (Optional[str]): Path to the browser profile directory. If None, a default or temporary profile is used.
		"""
		
		self._webdriver_start_args.profile_dir = profile_dir
	
	def set_debugging_port(self, debugging_port: Optional[int]):
		"""
		Sets the debugging port.

		Configures the browser to start with a specific debugging port. This port is used for external tools,
		like debuggers or browser automation frameworks, to connect to and control the browser instance.
		Setting a fixed debugging port can be useful for consistent remote debugging or automation setups.

		Args:
			debugging_port (Optional[int]): Debugging port number. If None, the browser chooses a port automatically.
		"""
		
		self._webdriver_start_args.debugging_port = debugging_port
		self._webdriver_options_manager.set_debugger_address(debugging_port)
	
	def hide_automation(self, hide: bool):
		"""
		Sets whether to hide browser automation indicators.

		This method configures the browser options to hide or show automation
		indicators, which are typically present when a browser is controlled by WebDriver.

		Args:
			hide (bool): If True, hides automation indicators; otherwise, shows them.
		"""
		
		self._webdriver_options_manager.hide_automation(hide)
	
	def set_enable_devtools(self, enable_devtools: bool):
		"""
		Enables or disables the BiDi protocol for DevTools.

		Controls whether the BiDi (Bidirectional) protocol is enabled for communication with browser developer tools.
		Enabling DevTools allows for advanced browser interaction, network interception, and performance analysis.

		Args:
			enable_devtools (bool): True to enable DevTools, False to disable.
		"""
		
		self._webdriver_options_manager.set_enable_bidi(enable_devtools)
	
	def reset_settings(
			self,
			enable_devtools: bool,
			hide_automation: bool = False,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: bool = False,
			mute_audio: bool = False,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
			start_page_url: str = "",
	):
		"""
		Resets all configurable browser settings to their default or specified values.

		This method resets various browser settings to the provided values. If no value
		is provided for certain settings, they are reset to their default states.
		This includes DevTools, automation hiding, debugging port, profile directory,
		proxy, audio muting, headless mode, user agent, and window rectangle.

		Args:
			enable_devtools (bool): Enables or disables DevTools integration.
			hide_automation (bool): Sets whether to hide browser automation indicators. Defaults to False.
			debugging_port (Optional[int]): Specifies the debugging port for the browser. Defaults to None.
			profile_dir (Optional[str]): Sets the browser profile directory. Defaults to None.
			headless_mode (bool): Enables or disables headless mode. Defaults to False.
			mute_audio (bool): Mutes or unmutes audio output in the browser. Defaults to False.
			proxy (Optional[Union[str, list[str]]]): Configures proxy settings for the browser. Defaults to None.
			user_agent (Optional[str]): Sets a custom user agent string for the browser. Defaults to None.
			window_rect (Optional[WindowRect]): Updates the window rectangle settings. Defaults to None.
			start_page_url (str): The URL to navigate to when the browser starts. Defaults to an empty string.
		"""
		
		if window_rect is None:
			window_rect = WindowRect()
		
		self.set_enable_devtools(enable_devtools)
		self.hide_automation(hide_automation)
		self.set_debugging_port(debugging_port)
		self.set_profile_dir(profile_dir)
		self.set_proxy(proxy)
		self.set_mute_audio(mute_audio)
		self.set_headless_mode(headless_mode)
		self.set_user_agent(user_agent)
		self.set_start_page_url(start_page_url)
		self._window_rect = window_rect
	
	@property
	def debugging_port(self) -> Optional[int]:
		"""
		Gets the currently set debugging port.

		Retrieves the debugging port number that the browser instance is configured to use.

		Returns:
			Optional[int]: The debugging port number, or None if not set.
		"""
		
		return self._webdriver_start_args.debugging_port
	
	def create_driver(self):
		"""
		Abstract method to create a WebDriver instance. Must be implemented in child classes.

		This method is intended to be overridden in subclasses to provide browser-specific
		WebDriver instantiation logic (e.g., creating ChromeDriver, FirefoxDriver, etc.).

		Raises:
			NotImplementedError: If the method is not implemented in a subclass.
		"""
		
		raise NotImplementedError("This function must be implemented in child classes.")
	
	def check_webdriver_active(self) -> bool:
		"""
		Checks if the WebDriver is active by verifying if the debugging port is in use.

		Determines if a WebDriver instance is currently running and active by checking if the configured
		debugging port is in use by any process. This is a way to verify if a browser session is active
		without directly querying the WebDriver itself.

		Returns:
			bool: True if the WebDriver is active (debugging port is in use), False otherwise.
		"""
		
		if any(
				ports == [self.debugging_port]
				for pid, ports in get_localhost_processes_with_pids().items()
		):
			return True
		else:
			return False
	
	def find_debugging_port(self, debugging_port: Optional[int], profile_dir: Optional[str]) -> int:
		"""
		Finds an appropriate debugging port, either reusing a previous session's port or finding a free port.

		Attempts to locate a suitable debugging port for the browser. It first tries to reuse a debugging port
		from a previous browser session if a profile directory is specified and a previous session is found.
		If no previous session is found or if no profile directory is specified, it attempts to use the provided
		`debugging_port` if available, or finds a minimum free port if no port is provided or the provided port is in use.

		Args:
			debugging_port (Optional[int]): Requested debugging port number. If provided, the method attempts to use this port. Defaults to None.
			profile_dir (Optional[str]): Profile directory path. If provided, the method checks for previous sessions using this profile. Defaults to None.

		Returns:
			int: The debugging port number to use. This is either a reused port from a previous session, the provided port if available, or a newly found free port.
		"""
		
		previous_session = find_browser_previous_session(
				self._browser_exe,
				self._webdriver_start_args.profile_dir_command_line,
				profile_dir
		)
		
		if previous_session is not None:
			return previous_session
		
		if debugging_port is not None:
			return get_localhost_minimum_free_port(debugging_port)
		
		if self.debugging_port is None:
			return get_localhost_minimum_free_port()
		
		return self.debugging_port
	
	def update_settings(
			self,
			enable_devtools: Optional[bool] = None,
			hide_automation: Optional[bool] = None,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
			start_page_url: Optional[str] = None,
	):
		"""
		Updates various browser settings after initialization.

		This method allows for dynamic updating of browser settings such as
		DevTools enablement, automation hiding, debugging port, profile directory,
		headless mode, audio muting, proxy configuration, user agent string, and window rectangle.

		Args:
			enable_devtools (Optional[bool]): Enables or disables DevTools integration. Defaults to None.
			hide_automation (Optional[bool]): Sets whether to hide browser automation indicators. Defaults to None.
			debugging_port (Optional[int]): Specifies a debugging port for the browser. Defaults to None.
			profile_dir (Optional[str]): Sets the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Enables or disables headless mode. Defaults to None.
			mute_audio (Optional[bool]): Mutes or unmutes audio output in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Configures proxy settings for the browser. Defaults to None.
			user_agent (Optional[str]): Sets a custom user agent string for the browser. Defaults to None.
			window_rect (Optional[WindowRect]): Updates the window rectangle settings. Defaults to None.
			start_page_url (Optional[str]): Sets the start page URL for the browser. Defaults to None.
		"""
		
		if enable_devtools is not None:
			self.set_enable_devtools(enable_devtools)
		
		if hide_automation is not None:
			self.hide_automation(hide_automation)
		
		if profile_dir is not None:
			self.set_profile_dir(profile_dir)
		
		if proxy is not None:
			self.set_proxy(proxy)
		
		if mute_audio is not None:
			self.set_mute_audio(mute_audio)
		
		if headless_mode is not None:
			self.set_headless_mode(headless_mode)
		
		if user_agent is not None:
			self.set_user_agent(user_agent)
		
		if window_rect is not None:
			self._window_rect = window_rect
		
		if start_page_url is not None:
			self.set_start_page_url(start_page_url)
		
		self.set_debugging_port(self.find_debugging_port(debugging_port, profile_dir))
	
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
			start_page_url: Optional[str] = None,
	):
		"""
		Starts the WebDriver and browser session.

		Initializes and starts the WebDriver instance and the associated browser process.
		It first updates settings based on provided parameters, checks if a WebDriver instance is already active,
		and if not, starts the WebDriver service and then creates a new browser session.

		Args:
			enable_devtools (Optional[bool]): Whether to enable DevTools integration. Defaults to None.
			debugging_port (Optional[int]): Debugging port number for the browser. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the browser in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.
			user_agent (Optional[str]): User agent string to use. Defaults to None.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to None.
			start_page_url (Optional[str]): Sets the start page URL for the browser. Defaults to None.
		"""
		
		if self.driver is None:
			self.update_settings(
					enable_devtools=enable_devtools,
					debugging_port=debugging_port,
					profile_dir=profile_dir,
					headless_mode=headless_mode,
					mute_audio=mute_audio,
					proxy=proxy,
					user_agent=user_agent,
					window_rect=window_rect,
					start_page_url=start_page_url,
			)
		
			self._is_active = self.check_webdriver_active()
		
			if not self._is_active:
				Popen(self._webdriver_start_args.start_command, shell=True)
		
				while not self._is_active:
					self._is_active = self.check_webdriver_active()
		
			self.create_driver()
	
	def close_webdriver(self):
		"""
		Closes the WebDriver instance and terminates the associated browser subprocess.

		Quits the current WebDriver session, closes all browser windows, and then forcefully terminates
		the browser process. This ensures a clean shutdown of the browser and WebDriver environment.
		"""
		
		for pid, ports in get_localhost_processes_with_pids().items():
			if ports == [self.debugging_port]:
				taskkill_windows(
						taskkill_type=TaskKillTypes.forcefully_terminate,
						selectors=ProcessID(pid)
				)
		
				self._is_active = self.check_webdriver_active()
		
				while self._is_active:
					self._is_active = self.check_webdriver_active()
		
		self.driver.quit()
		self.driver = None
	
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
			start_page_url: Optional[str] = None,
	):
		"""
		Restarts the WebDriver and browser session.

		Performs a complete restart of the WebDriver and browser. It first closes the existing WebDriver
		and browser session using `close_webdriver`, and then starts a new session using `start_webdriver`
		with the provided or current settings. This is useful for resetting the browser state between tests or operations.

		Args:
			enable_devtools (Optional[bool]): Whether to enable DevTools integration for the new session. Defaults to None.
			debugging_port (Optional[int]): Debugging port number for the new browser session. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory for the new session. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the new browser session in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the new browser session. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses for the new session. Defaults to None.
			user_agent (Optional[str]): User agent string to use for the new session. Defaults to None.
			window_rect (Optional[WindowRect]): Initial window rectangle settings for the new session. Defaults to None.
			start_page_url (Optional[str]): Sets the start page URL for the browser. Defaults to None.
		"""
		
		self.close_webdriver()
		self.start_webdriver(
				enable_devtools=enable_devtools,
				debugging_port=debugging_port
				if debugging_port is not None
				else self.debugging_port,
				profile_dir=profile_dir,
				headless_mode=headless_mode,
				mute_audio=mute_audio,
				proxy=proxy,
				user_agent=user_agent,
				window_rect=window_rect,
				start_page_url=start_page_url,
		)
	
	def scroll_by_amount(self, x: int = 0, y: int = 0, duration: int = 250):
		"""
		Scrolls the viewport by a specified amount.

		Performs a scroll action in the browser viewport by a given amount in pixels, both horizontally and vertically.
		This is useful for scrolling the page programmatically to bring different parts of the content into view.

		Args:
			x (int): Horizontal scroll amount in pixels. Positive values scroll right, negative values scroll left. Defaults to 0 (no horizontal scroll).
			y (int): Vertical scroll amount in pixels. Positive values scroll down, negative values scroll up. Defaults to 0 (no vertical scroll).
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		
		ActionChains(driver=self.driver, duration=duration).scroll_by_amount(x, y).perform()
	
	def scroll_down_of_element(self, element: WebElement, duration: int = 250):
		"""
		Scrolls down within a specific web element by half of its height.

		Simulates scrolling down inside a given WebElement. It moves the mouse to the element and then scrolls vertically by an amount equal to half the element's height. This is useful for bringing content within a scrollable element into view.

		Args:
			element (WebElement): The WebElement object representing the element to scroll within. This element should be scrollable.
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		
		ActionChains(driver=self.driver, duration=duration).move_to_element_with_offset(element, xoffset=0, yoffset=element.size["height"] // 2).perform()
	
	def scroll_from_origin(
			self,
			origin: ScrollOrigin,
			x: int = 0,
			y: int = 0,
			duration: int = 250
	):
		"""
		Scrolls from a specific origin by a specified amount.

		Scrolls the viewport relative to a specified origin point. The origin can be the viewport itself
		or a specific web element. This offers more control over the starting point of the scroll action.

		Args:
			origin (ScrollOrigin): The scroll origin, which can be the viewport or a specific element (e.g., `ScrollOrigin.viewport`, `ScrollOrigin.element`).
			x (int): Horizontal scroll amount in pixels from the origin. Defaults to 0.
			y (int): Vertical scroll amount in pixels from the origin. Defaults to 0.
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		
		ActionChains(driver=self.driver, duration=duration).scroll_from_origin(origin, x, y).perform()
	
	def scroll_to_element(self, element: WebElement, duration: int = 250):
		"""
		Scrolls an element into view.

		Programmatically scrolls the webpage to bring a specific web element into the visible viewport.
		This is useful for ensuring that an element is visible before interacting with it, especially if it's initially off-screen.

		Args:
			element (WebElement): The element to scroll into view.
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		
		ActionChains(driver=self.driver, duration=duration).scroll_to_element(element).perform()
	
	def scroll_up_of_element(self, element: WebElement, duration: int = 250):
		"""
		Scrolls up within a specific web element by half of its height.

		This method simulates scrolling up inside a given WebElement. It moves the mouse to the element and then scrolls vertically upwards by an amount equal to half the element's height. This is useful for bringing content within a scrollable element into view.

		Args:
			element (WebElement): The WebElement object representing the element to scroll within. This element should be scrollable.
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		
		ActionChains(driver=self.driver, duration=duration).move_to_element_with_offset(element, xoffset=0, yoffset=-(element.size["height"] // 2)).perform()
	
	def search_url(
			self,
			url: str,
			temp_implicitly_wait: Optional[int] = None,
			temp_page_load_timeout: Optional[int] = None
	):
		"""
		Opens a URL in the current browser session.

		Navigates the browser to a specified URL. This action loads the new webpage in the current browser window or tab.

		Args:
			url (str): The URL to open. Must be a valid web address (e.g., "https://www.example.com").
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for page load. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for page load. Defaults to None.
		"""
		
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		self.driver.get(url)
	
	def set_window_rect(self, rect: WindowRect):
		"""
		Sets the browser window rectangle.

		Adjusts the position and size of the browser window to the specified rectangle. This can be used
		to manage window placement and dimensions for testing or display purposes.

		Args:
			rect (WindowRect): An object containing the desired window rectangle parameters (x, y, width, height).
		"""
		
		self.driver.set_window_rect(x=rect.x, y=rect.y, width=rect.width, height=rect.height)
	
	def stop_window_loading(self):
		"""
		Stops the current page loading.

		Interrupts the loading process of the current webpage. This can be useful when a page is taking too long
		to load or when you want to halt resource loading for performance testing or specific scenarios.
		"""
		
		self.execute_js_script(self._js_scripts["stop_window_loading"])
	
	def switch_to_frame(self, frame: Union[str, int, WebElement]):
		"""
		Switches the driver's focus to a frame.

		Changes the WebDriver's focus to a specific frame within the current page. Frames are often used to embed
		content from other sources within a webpage. After switching to a frame, all WebDriver commands will be
		directed to elements within that frame until focus is switched back.

		Args:
			frame (Union[str, int, WebElement]): Specifies the frame to switch to. Can be a frame name (str), index (int), or a WebElement representing the frame.
		"""
		
		self.driver.switch_to.frame(frame)
	
	def to_wrapper(self):
		"""
		Creates a TrioBrowserWebDriverWrapper instance for asynchronous operations with Trio.

		Wraps the BrowserWebDriver instance in a TrioBrowserWebDriverWrapper, which allows for running WebDriver
		commands in a non-blocking manner within a Trio asynchronous context. This is essential for
		integrating Selenium WebDriver with asynchronous frameworks like Trio.

		Returns:
			TrioBrowserWebDriverWrapper: A TrioBrowserWebDriverWrapper instance wrapping this BrowserWebDriver.
		"""
		
		return TrioBrowserWebDriverWrapper(webdriver_=self)
	
	@property
	def window(self) -> str:
		"""
		Gets the current window handle.

		Retrieves the handle of the currently active browser window or tab. Window handles are unique identifiers
		used by WebDriver to distinguish between different browser windows.

		Returns:
			str: The current window handle.
		"""
		
		return self.driver.current_window_handle
	
	@property
	def windows_names(self) -> list[str]:
		"""
		Gets the handles of all open windows.

		Returns a list of handles for all browser windows or tabs currently open and managed by the WebDriver.
		This is useful for iterating through or managing multiple windows in a browser session.

		Returns:
		   list[str]: A list of window handles. Each handle is a string identifier for an open window.
		"""
		
		return self.driver.window_handles


class TrioBrowserWebDriverWrapper:
	"""
	Wraps BrowserWebDriver for asynchronous execution in Trio.

	This class provides a wrapper around BrowserWebDriver to make its methods compatible with Trio's
	asynchronous execution model. It uses `trio.to_thread.run_sync` to execute WebDriver commands
	in separate threads, preventing them from blocking the Trio event loop.

	Attributes:
		_webdriver (BrowserWebDriver): The BrowserWebDriver instance being wrapped.
	"""
	
	def __init__(self, webdriver_: BrowserWebDriver):
		"""
		Initializes the TrioBrowserWebDriverWrapper.

		Args:
			webdriver_ (BrowserWebDriver): The BrowserWebDriver instance to wrap.
		"""
		
		self._webdriver = webdriver_
	
	def __getattr__(self, name):
		"""
		Overrides attribute access to run BrowserWebDriver methods asynchronously.

		This method is a special Python method that gets called when an attribute is accessed that
		doesn't exist on the `TrioBrowserWebDriverWrapper` instance itself. In this case, it's used to intercept
		calls to methods of the wrapped `BrowserWebDriver` instance and execute them in a non-blocking way
		using `trio.to_thread.run_sync`. This ensures that WebDriver operations, which are inherently synchronous,
		do not block the asynchronous Trio event loop.

		Args:
			name (str): The name of the attribute being accessed.

		Returns:
			Any: If the attribute is a method of `BrowserWebDriver`, returns a wrapped asynchronous version of the method.
				 If the attribute is a property, returns the property directly from `BrowserWebDriver`.
		"""
		
		if name in ["to_wrapper"]:
			raise AttributeError(f"Don't use {name} method in TrioBrowserWebDriverWrapper!")
		else:
			attr = getattr(self._webdriver, name)
		
			if callable(attr):
				def wrapped(*args, **kwargs):
					return trio.to_thread.run_sync(attr, *args, **kwargs)
		
				return wrapped
		
			return attr
