import pathlib
from time import sleep
from random import random
from subprocess import Popen
from selenium import webdriver
from typing import Any, Optional, Union
from osn_bas.utilities import WindowRect
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from osn_windows_cmd.taskkill.parameters import TaskKillTypes
from osn_bas.webdrivers.BaseDriver.start_args import BrowserStartArgs
from osn_windows_cmd.taskkill import (
	ProcessID,
	taskkill_windows
)
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from osn_bas.webdrivers.BaseDriver.options import BrowserOptionsManager
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.functions import (
	find_browser_previous_session,
	read_js_scripts
)
from osn_windows_cmd.netstat import (
	get_localhost_busy_ports,
	get_localhost_minimum_free_port,
	get_localhost_processes_with_pids
)


class BrowserWebDriver:
	"""
	A base class for managing browser and WebDriver instances.

	This class provides a foundation for interacting with web browsers through WebDriver.
	It handles the setup of browser executables, WebDriver paths, browser options, and start arguments.
	It also manages the WebDriver lifecycle, including starting and stopping the browser.

	Attributes:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
		webdriver_path (str): Path to the WebDriver executable.
		window_rect (WindowRect): Object to store window rectangle settings, controlling window position and size.
		webdriver_start_args (BrowserStartArgs): Manages browser-specific start arguments passed to the WebDriver.
		webdriver_options_manager (BrowserOptionsManager): Manages browser options, such as headless mode, extensions, etc.
		webdriver_is_active (bool): Flag indicating whether the WebDriver instance is currently active and controlling a browser.
		base_implicitly_wait (int): Base implicit wait time in seconds for WebDriver operations, inherited from EmptyWebDriver.
		base_page_load_timeout (int): Base page load timeout in seconds for page loading operations, inherited from EmptyWebDriver.
		driver (Optional[Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox]]): The underlying WebDriver instance (e.g., Chrome, Edge, Firefox WebDriver).
	"""
	
	def __init__(
			self,
			browser_exe: Union[str, pathlib.Path],
			webdriver_path: str,
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
		"""
		Initializes BrowserWebDriver with browser and WebDriver paths, and settings.

		Args:
			browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
			webdriver_path (str): Path to the WebDriver executable.
			webdriver_start_args (type): Class type for managing browser start arguments.
			webdriver_options_manager (type): Class type for managing browser options.
			debugging_port (Optional[int]): Debugging port number. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the browser in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.
			user_agent (Optional[str]): User agent string to use. Defaults to None.
			implicitly_wait (int): Base implicit wait time for WebDriver operations. Defaults to 5.
			page_load_timeout (int): Base page load timeout for WebDriver operations. Defaults to 5.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to None.
		"""
		if window_rect is None:
			window_rect = WindowRect()
		
		self.browser_exe = browser_exe
		self.webdriver_path = webdriver_path
		self.window_rect = window_rect
		self.base_implicitly_wait = implicitly_wait
		self.base_page_load_timeout = page_load_timeout
		self.js_scripts = read_js_scripts()
		self.driver: Optional[Union[webdriver.Chrome, webdriver.Edge, webdriver.Firefox]] = None
		
		self.webdriver_start_args: BrowserStartArgs = webdriver_start_args(browser_exe=browser_exe)
		
		self.webdriver_options_manager: BrowserOptionsManager = webdriver_options_manager()
		self.webdriver_is_active = False
		
		self.update_settings(
				debugging_port=debugging_port,
				profile_dir=profile_dir,
				headless_mode=headless_mode,
				mute_audio=mute_audio,
				proxy=proxy,
				user_agent=user_agent
		)
	
	def switch_to_window(self, window: Optional[Union[str, int]] = None):
		"""
		Switches focus to the specified window.

		Args:
			window (Optional[Union[str, int]]): The name, index, or handle of the window to switch to. If None, switches to the current window. Defaults to None.
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

		Args:
			window (Optional[Union[str, int]]): The name, index, or handle of the window to close. If None, closes the current window. Defaults to None.
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
		"""
		for window in self.driver.window_handles:
			self.close_window(window)
	
	@property
	def current_url(self) -> str:
		"""
		Gets the current URL.

		Returns:
			str: The current URL.
		"""
		return self.driver.current_url
	
	def set_implicitly_wait_timeout(self, timeout: float):
		"""
		Sets the implicit wait timeout for WebDriver element searches.

		This method sets the amount of time WebDriver will implicitly wait when searching for elements
		before throwing a `NoSuchElementException`. It uses the WebDriver's `implicitly_wait` method.

		Args:
			timeout (float): The implicit wait timeout value in seconds.
		"""
		self.driver.implicitly_wait(timeout)
	
	def set_page_load_timeout(self, timeout: float):
		"""
		Sets the page load timeout for WebDriver operations.

		This method configures the maximum time WebDriver will wait for a page to load before timing out.
		It utilizes the WebDriver's `set_page_load_timeout` method to set this timeout.

		Args:
			timeout (float): The page load timeout value in seconds.
		"""
		self.driver.set_page_load_timeout(timeout)
	
	def set_driver_timeouts(self, page_load_timeout: float, implicit_wait_timeout: float):
		"""
		Sets both page load timeout and implicit wait timeout for WebDriver.

		This method is a convenience function to set both the page load timeout and the implicit wait timeout
		in a single call. It internally calls `set_page_load_timeout` and `set_implicitly_wait_timeout`.

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

		Args:
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds. Defaults to None.
		"""
		if temp_implicitly_wait:
			implicitly_wait = temp_implicitly_wait + random()
		else:
			implicitly_wait = self.base_implicitly_wait + random()
		
		if temp_page_load_timeout:
			page_load_timeout = temp_page_load_timeout + random()
		else:
			page_load_timeout = self.base_page_load_timeout + random()
		
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

		Args:
			parent_element (WebElement): The parent web element to search within.
			by (By): Locator strategy (e.g., By.ID, By.XPATH).
			value (str): Locator value (e.g., "elementId", "//xpath/to/element").
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			WebElement: The found web element.
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

		Args:
			parent_element (WebElement): The parent web element to search within.
			by (By): Locator strategy (e.g., By.CLASS_NAME, By.CSS_SELECTOR).
			value (str): Locator value (e.g., "className", "css.selector").
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			list[WebElement]: A list of found web elements.
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

		Args:
			by (By): Locator strategy (e.g., By.ID, By.NAME).
			value (str): Locator value (e.g., "loginForm", "username").
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			WebElement: The found web element.
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

		Args:
			by (By): Locator strategy (e.g., By.TAG_NAME, By.LINK_TEXT).
			value (str): Locator value (e.g., "div", "Click Here").
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for this operation. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for this operation. Defaults to None.

		Returns:
			list[WebElement]: A list of found web elements.
		"""
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		return self.driver.find_elements(by, value)
	
	def execute_js_script(self, script: str, *args) -> Any:
		"""
		Executes a JavaScript script in the current browser context.

		This method uses the Selenium WebDriver's `execute_script` function to run arbitrary JavaScript code
		within the context of the currently active web page. It allows for dynamic interaction with the webpage
		beyond the standard WebDriver commands.

		Args:
			script (str): The JavaScript code to be executed as a string. This script can access and manipulate
						  the DOM of the webpage, call browser APIs, and perform any action that is possible in JavaScript.
			*args: Variable length argument list. These arguments are passed to the JavaScript script and can be accessed
				   within the script using the `arguments` array (e.g., `arguments[0]`, `arguments[1]`, etc.).
				   These arguments can be of any type that can be serialized to JSON.

		Returns:
			Any: The result of the JavaScript execution. The return value from JavaScript is automatically
						converted to the corresponding Python type. If the JavaScript code returns a primitive type
						(number, string, boolean), it will be returned as is. If it returns a JavaScript object or array,
						it will be converted to a Python dictionary or list, respectively. If the script does not return
						any value or returns `undefined`, Python `None` is returned.
		"""
		return self.driver.execute_script(script, *args)
	
	def get_element_css_style(self, element: WebElement) -> dict[str, str]:
		"""
		Retrieves the computed CSS style of a WebElement.

		This method uses JavaScript to get the computed style of a given WebElement.
		It extracts all CSS properties and their values as a dictionary.

		Args:
			element (WebElement): The WebElement for which to retrieve the CSS style.

		Returns:
			dict[str, str]: A dictionary where keys are CSS property names and values are their computed values.
		"""
		return self.execute_js_script(self.js_scripts["get_element_css"], element)
	
	def get_vars_for_remote(self) -> tuple[RemoteConnection, str]:
		"""
		Gets variables necessary to create a remote WebDriver instance.

		Returns:
			tuple[RemoteConnection, str]: A tuple containing the command executor and session ID of the WebDriver.
		"""
		return self.driver.command_executor, self.driver.session_id
	
	def hover_element(self, element: WebElement, duration: int = 250):
		"""
		Hovers the mouse over an element.

		Args:
			element (WebElement): The element to hover over.
			duration (int): Duration of the hover action in milliseconds. Defaults to 250ms.
		"""
		ActionChains(driver=self.driver, duration=duration).move_to_element(element).perform()
	
	@property
	def html(self) -> str:
		"""
		Gets the current page source.

		Returns:
			str: The page source.
		"""
		return self.driver.page_source
	
	def open_new_tab(self, link: str = ""):
		"""
		Opens a new tab with the given URL.

		Args:
			link (str): URL to open in the new tab. Defaults to "".
		"""
		self.execute_js_script(self.js_scripts["open_new_tab"], link)
	
	@property
	def rect(self) -> WindowRect:
		"""
		Gets the window rectangle.

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
		"""
		raise NotImplementedError("This function must be implemented in child classes.")
	
	@property
	def window(self) -> str:
		"""
		Gets the current window handle.

		Returns:
			str: The current window handle.
		"""
		return self.driver.current_window_handle
	
	def set_user_agent(self, user_agent: Optional[str]):
		"""
		Sets the user agent.

		Args:
			user_agent (Optional[str]): User agent string to use.
		"""
		self.webdriver_start_args.set_user_agent(user_agent)
		self.webdriver_options_manager.set_user_agent(user_agent)
	
	def set_headless_mode(self, headless_mode: bool):
		"""
		Sets headless mode.

		Args:
			headless_mode (bool): Whether to start the browser in headless mode.
		"""
		self.webdriver_start_args.set_headless_mode(headless_mode)
	
	def set_mute_audio(self, mute_audio: bool):
		"""
		Sets mute audio mode.

		Args:
			mute_audio (bool): Whether to mute audio in the browser.
		"""
		self.webdriver_start_args.set_mute_audio(mute_audio)
	
	def set_proxy(self, proxy: Optional[Union[str, list[str]]]):
		"""
		Sets the proxy.

		Args:
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses.
		"""
		self.webdriver_start_args.set_proxy_server(proxy)
		self.webdriver_options_manager.set_proxy(proxy)
	
	def set_profile_dir(self, profile_dir: Optional[str]):
		"""
		Sets the profile directory.

		Args:
			profile_dir (Optional[str]): Path to the browser profile directory.
		"""
		self.webdriver_start_args.set_profile_dir(profile_dir)
	
	def set_debugging_port(self, debugging_port: Optional[int]):
		"""
		Sets the debugging port.

		Args:
			debugging_port (Optional[int]): Debugging port number.
		"""
		self.webdriver_start_args.set_debugging_port(debugging_port)
		self.webdriver_options_manager.set_debugger_address(debugging_port)
	
	def reset_settings(
			self,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	):
		"""
		Resets browser settings to provided values.

		Args:
			debugging_port (Optional[int]): Debugging port number. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the browser in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.
			user_agent (Optional[str]): User agent string to use. Defaults to None.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to None.
		"""
		if window_rect is None:
			window_rect = WindowRect()
		
		self.set_debugging_port(debugging_port)
		self.set_profile_dir(profile_dir)
		self.set_proxy(proxy)
		self.set_mute_audio(mute_audio)
		self.set_headless_mode(headless_mode)
		self.set_user_agent(user_agent)
		self.window_rect = window_rect
	
	def create_driver(self):
		"""
		Abstract method to create a WebDriver instance. Must be implemented in child classes.
		"""
		raise NotImplementedError("This function must be implemented in child classes.")
	
	@property
	def debugging_port(self) -> Optional[int]:
		"""
		Gets the currently set debugging port.

		Returns:
			Optional[int]: The debugging port number, or None if not set.
		"""
		return self.webdriver_start_args.debugging_port
	
	def check_webdriver_active(self) -> bool:
		"""
		Checks if the WebDriver is active by verifying if the debugging port is in use.

		Returns:
			bool: True if the WebDriver is active, False otherwise.
		"""
		if self.debugging_port in get_localhost_busy_ports():
			return True
		else:
			return False
	
	def find_debugging_port(self, debugging_port: Optional[int], profile_dir: Optional[str]) -> int:
		"""
		Finds an appropriate debugging port, either reusing a previous session's port or finding a free port.

		Args:
			debugging_port (Optional[int]): Requested debugging port number. Defaults to None.
			profile_dir (Optional[str]): Profile directory path. Defaults to None.

		Returns:
			int: The debugging port number to use.
		"""
		previous_session = find_browser_previous_session(
				self.browser_exe,
				self.webdriver_start_args.profile_dir_command_line,
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
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	):
		"""
		Updates browser settings with provided values, keeping existing settings if new values are None.

		Args:
			debugging_port (Optional[int]): Debugging port number. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the browser in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.
			user_agent (Optional[str]): User agent string to use. Defaults to None.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to None.
		"""
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
			self.window_rect = window_rect
		
		self.set_debugging_port(self.find_debugging_port(debugging_port, profile_dir))
	
	def start_webdriver(
			self,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	):
		"""
		Starts the WebDriver instance, launching the browser subprocess if necessary.

		Args:
			debugging_port (Optional[int]): Debugging port number. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the browser in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.
			user_agent (Optional[str]): User agent string to use. Defaults to None.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to None.
		"""
		if self.driver is None:
			self.update_settings(
					debugging_port=debugging_port,
					profile_dir=profile_dir,
					headless_mode=headless_mode,
					mute_audio=mute_audio,
					proxy=proxy,
					user_agent=user_agent,
					window_rect=window_rect
			)
		
			self.webdriver_is_active = self.check_webdriver_active()
		
			if not self.webdriver_is_active:
				print(self.webdriver_start_args.start_command)
				Popen(self.webdriver_start_args.start_command, shell=True)
		
				while not self.webdriver_is_active:
					self.webdriver_is_active = self.check_webdriver_active()
		
			self.create_driver()
	
	def close_webdriver(self):
		"""
		Closes the WebDriver instance and terminates the associated browser subprocess.
		"""
		for pid, ports in get_localhost_processes_with_pids().items():
			if self.debugging_port in ports:
				taskkill_windows(
						taskkill_type=TaskKillTypes.forcefully_terminate,
						selectors=ProcessID(pid)
				)
		
				while self.webdriver_is_active:
					self.webdriver_is_active = self.check_webdriver_active()
		
				sleep(1)
				break
		
		self.driver = None
	
	def restart_webdriver(
			self,
			debugging_port: Optional[int] = None,
			profile_dir: Optional[str] = None,
			headless_mode: Optional[bool] = None,
			mute_audio: Optional[bool] = None,
			proxy: Optional[Union[str, list[str]]] = None,
			user_agent: Optional[str] = None,
			window_rect: Optional[WindowRect] = None,
	):
		"""
		Restarts the WebDriver instance, closing and then restarting the browser with current or provided settings.

		Args:
			debugging_port (Optional[int]): Debugging port number. Defaults to None.
			profile_dir (Optional[str]): Path to the browser profile directory. Defaults to None.
			headless_mode (Optional[bool]): Whether to start the browser in headless mode. Defaults to None.
			mute_audio (Optional[bool]): Whether to mute audio in the browser. Defaults to None.
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. Defaults to None.
			user_agent (Optional[str]): User agent string to use. Defaults to None.
			window_rect (Optional[WindowRect]): Initial window rectangle settings. Defaults to None.
		"""
		self.close_webdriver()
		self.start_webdriver(
				debugging_port,
				profile_dir,
				headless_mode,
				mute_audio,
				proxy,
				user_agent,
				window_rect
		)
	
	def scroll_by_amount(self, x: int = 0, y: int = 0, duration: int = 250):
		"""
		Scrolls the viewport by a specified amount.

		Args:
			x (int): Horizontal scroll amount in pixels. Defaults to 0.
			y (int): Vertical scroll amount in pixels. Defaults to 0.
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		ActionChains(driver=self.driver, duration=duration).scroll_by_amount(x, y).perform()
	
	def scroll_down_of_element(self, element: WebElement, duration: int = 250):
		"""
		Scrolls down within a specific web element by half of its height.

		This method simulates scrolling down inside a given WebElement. It moves the mouse to the element and then scrolls vertically by an amount equal to half the element's height. This is useful for bringing content within a scrollable element into view.

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

		Args:
			origin (ScrollOrigin): The scroll origin (e.g., ScrollOrigin.viewport, ScrollOrigin.element).
			x (int): Horizontal scroll amount in pixels. Defaults to 0.
			y (int): Vertical scroll amount in pixels. Defaults to 0.
			duration (int): Duration of the scroll animation in milliseconds. Defaults to 250ms.
		"""
		ActionChains(driver=self.driver, duration=duration).scroll_from_origin(origin, x, y).perform()
	
	def scroll_to_element(self, element: WebElement, duration: int = 250):
		"""
		Scrolls an element into view.

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

		Args:
			url (str): The URL to open.
			temp_implicitly_wait (Optional[int]): Temporary implicit wait time in seconds for page load. Defaults to None.
			temp_page_load_timeout (Optional[int]): Temporary page load timeout in seconds for page load. Defaults to None.
		"""
		self.update_times(temp_implicitly_wait, temp_page_load_timeout)
		self.driver.get(url)
	
	def set_window_rect(self, rect: WindowRect):
		"""
		Sets the browser window rectangle.

		This method sets the position and size of the browser window using the provided `WindowRect` object.
		It uses the WebDriver's `set_window_rect` method to apply the window settings.

		Args:
			rect (WindowRect): An object containing the desired window rectangle parameters (x, y, width, height).
		"""
		self.driver.set_window_rect(x=rect.x, y=rect.y, width=rect.width, height=rect.height)
	
	def stop_window_loading(self):
		"""
		Stops the current page loading.
		"""
		self.execute_js_script(self.js_scripts["stop_window_loading"])
	
	def switch_to_frame(self, frame: Union[str, int, WebElement]):
		"""
		Switches the driver's focus to a frame.

		Args:
			frame (Union[str, int, WebElement]): The frame to switch to. Can be a frame name, index, or WebElement.
		"""
		self.driver.switch_to.frame(frame)
	
	@property
	def windows_names(self) -> list[str]:
		"""
		Gets the handles of all open windows.

		Returns:
		   list[str]: A list of window handles.
		"""
		return self.driver.window_handles
