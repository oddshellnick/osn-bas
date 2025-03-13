import pathlib
from time import sleep
from subprocess import Popen
from random import choice, random
from typing import Any, Optional, Union
from osn_bas.utilities import WindowRect
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
from osn_bas.webdrivers.types import WebdriverOption
from selenium.webdriver.remote.webelement import WebElement
from osn_windows_cmd.taskkill.parameters import TaskKillTypes
from osn_windows_cmd.taskkill import (
	ProcessID,
	taskkill_windows
)
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.functions import (
	build_first_start_argument,
	find_browser_previous_session,
	read_js_scripts
)
from osn_windows_cmd.netstat import (
	get_localhost_busy_ports,
	get_localhost_minimum_free_port,
	get_localhost_processes_with_pids
)


class BrowserOptionsManager:
	"""
	Manages browser options for WebDriver.

	This class is responsible for handling and setting browser options for Selenium WebDriver instances.
	It provides methods to add, remove, and modify browser arguments and experimental options.

	Attributes:
	   options (Any): The WebDriver options object, specific to the browser type (e.g., ChromeOptions, FirefoxOptions). Initialized by `renew_webdriver_options`.
	   debugging_port_command (str): Command line argument format string for setting the debugging port.
	   user_agent_command (str): Command line argument format string for setting the user agent.
	   proxy_command (str): Command line argument format string for setting the proxy.
	"""
	
	def __init__(
			self,
			debugging_port_command: WebdriverOption,
			user_agent_command: WebdriverOption,
			proxy_command: WebdriverOption,
	):
		"""
		Initializes BrowserOptionsManager with command templates.

		Args:
			debugging_port_command (str): Command line argument format for debugging port.
			user_agent_command (str): Command line argument format for user agent.
			proxy_command (str): Command line argument format for proxy.
		"""
		self.options = self.renew_webdriver_options()
		self.debugging_port_command = debugging_port_command
		self.user_agent_command = user_agent_command
		self.proxy_command = proxy_command
	
	def renew_webdriver_options(self) -> Any:
		"""
		Abstract method to renew WebDriver options. Must be implemented in child classes.

		Returns:
			Any: A new instance of WebDriver options (e.g., ChromeOptions, FirefoxOptions).
		"""
		raise NotImplementedError("This function must be implemented in child classes.")
	
	def hide_automation(self, hide: bool):
		"""
		Abstract method to hide browser automation. Must be implemented in child classes.

		Args:
			hide (bool): Whether to enable or disable hiding automation features.
		"""
		raise NotImplementedError("This function must be implemented in child classes.")
	
	def remove_experimental_option(self, experimental_option_name: str):
		"""
		Removes an experimental browser option by its attribute name.

		Args:
			experimental_option_name (str): Attribute name of the experimental option to remove.
		"""
		if hasattr(self, experimental_option_name):
			experimental_option = getattr(self, experimental_option_name)
		
			if experimental_option[0] in self.options.experimental_options:
				self.options.experimental_options.pop(experimental_option[0])
				delattr(self, experimental_option_name)
	
	def remove_argument(self, argument_name: str):
		"""
		Removes a browser argument by its attribute name.

		Args:
			argument_name (str): Attribute name of the argument to remove.
		"""
		if hasattr(self, argument_name):
			argument = getattr(self, argument_name)
		
			if argument in self.options.arguments:
				self.options.arguments.remove(argument)
				delattr(self, argument_name)
	
	def remove_option(self, option: WebdriverOption):
		"""
		Removes a browser option by its configuration object.

		This method removes a browser option, whether it's a normal argument or an experimental option, based on the provided `WebdriverOption` configuration.

		Args:
			option (WebdriverOption): The configuration object defining the option to be removed.

		Raises:
			ValueError: If the option type is not recognized.
		"""
		if option["type"] == "normal":
			self.remove_argument(option["name"])
		elif option["type"] == "experimental":
			self.remove_experimental_option(option["name"])
		elif option["type"] is None:
			pass
		else:
			raise ValueError(f"Unknown option type ({option}).")
	
	def set_experimental_option(
			self,
			experimental_option_name: str,
			experimental_option: str,
			value: Any
	):
		"""
		Sets an experimental browser option.

		Args:
			experimental_option_name (str): Name to store the experimental option under (attribute name in the class).
			experimental_option (str): Experimental option name.
			value (Any): Value for the experimental option.
		"""
		self.remove_experimental_option(experimental_option_name)
		
		self.options.add_experimental_option(experimental_option, value)
		setattr(self, experimental_option_name, (experimental_option, value))
	
	def set_argument(self, argument_name: str, argument: str, value: Optional[str] = None):
		"""
		Sets a browser argument.

		Args:
			argument_name (str): Name to store the argument under (attribute name in the class).
			argument (str): Argument format string, may contain '{value}' placeholder.
			value (Optional[str]): Value to insert into the argument format string. Defaults to None.
		"""
		self.remove_argument(argument_name)
		
		if value is not None:
			argument_line = argument.format(value=value)
		else:
			argument_line = argument
		
		self.options.add_argument(argument_line)
		setattr(self, argument_name, argument_line)
	
	def set_option(self, option: WebdriverOption, value: Any):
		"""
		Sets a browser option based on its configuration object.

		This method configures a browser option, handling both normal arguments and experimental options as defined in the provided `WebdriverOption`.
		It uses the option's type to determine the appropriate method for setting the option with the given value.

		Args:
			option (WebdriverOption): A dictionary-like object containing the configuration for the option to be set.
			value (Any): The value to be set for the option. The type and acceptable values depend on the specific browser option being configured.

		Raises:
			ValueError: If the option type is not recognized.
		"""
		if option["type"] == "normal":
			self.set_argument(option["name"], option["command"], value)
		elif option["type"] == "experimental":
			self.set_experimental_option(option["name"], option["command"], value)
		elif option["type"] is None:
			pass
		else:
			raise ValueError(f"Unknown option type ({option}).")
	
	def set_debugger_address(self, debugging_port: Optional[int]):
		"""
		Sets the debugger address experimental option.

		Args:
			debugging_port (Optional[int]): Debugging port number. If None, removes the debugger-address option. Defaults to None.
		"""
		if debugging_port is not None:
		
			self.set_option(self.debugging_port_command, f"127.0.0.1:{debugging_port}")
		else:
			self.remove_option(self.debugging_port_command)
	
	def set_proxy(self, proxy: Optional[Union[str, list[str]]] = None):
		"""
		Sets the proxy browser option.

		Args:
			proxy (Optional[Union[str, list[str]]]): Proxy string or list of proxy strings. If a list, a random proxy is chosen. If None, removes the proxy argument. Defaults to None.
		"""
		if proxy is not None:
			if isinstance(proxy, list):
				proxy = choice(proxy)
		
			self.set_option(self.proxy_command, proxy)
		else:
			self.remove_option(self.proxy_command)
	
	def set_user_agent(self, user_agent: Optional[str] = None):
		"""
		Sets the user agent browser option.

		Args:
			user_agent (Optional[str]): User agent string to set. If None, removes the user-agent argument. Defaults to None.
		"""
		if user_agent is not None:
			self.set_option(self.user_agent_command, user_agent)
		else:
			self.remove_option(self.user_agent_command)


class BrowserStartArgs:
	"""
	Manages browser start arguments for subprocess execution.

	This class constructs and manages the command line arguments used to start a browser subprocess.
	It allows setting and updating various arguments like debugging port, profile directory, user agent, headless mode, mute audio, and proxy server.

	Attributes:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
		debugging_port_command_line (str): Command line argument format string for debugging port.
		profile_dir_command_line (str): Command line argument format string for profile directory.
		headless_mode_command_line (str): Command line argument for headless mode.
		mute_audio_command_line (str): Command line argument for muting audio.
		user_agent_command_line (str): Command line argument format string for user agent.
		proxy_server_command_line (str): Command line argument format string for proxy server.
		debugging_port (Optional[int]): Current debugging port, defaults to None.
		profile_dir (Optional[str]): Current profile directory path, defaults to None.
		headless_mode (Optional[bool]): Current headless mode status, defaults to None.
		mute_audio (Optional[bool]): Current mute audio status, defaults to None.
		user_agent (Optional[str]): Current user agent string, defaults to None.
		proxy_server (Optional[str]): Current proxy server string, defaults to None.
		start_command (str): The full constructed start command string.
	"""
	
	def __init__(
			self,
			browser_exe: Union[str, pathlib.Path],
			debugging_port_command_line: str,
			profile_dir_command_line: str,
			headless_mode_command_line: str,
			mute_audio_command_line: str,
			user_agent_command_line: str,
			proxy_server_command_line: str,
	):
		"""
		Initializes BrowserStartArgs with browser executable and command line templates.

		Args:
			browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
			debugging_port_command_line (str): Command line argument format for debugging port.
			profile_dir_command_line (str): Command line argument format for profile directory.
			headless_mode_command_line (str): Command line argument for headless mode.
			mute_audio_command_line (str): Command line argument for mute audio.
			user_agent_command_line (str): Command line argument format for user agent.
			proxy_server_command_line (str): Command line argument format for proxy server.
		"""
		self.browser_exe = browser_exe
		self.debugging_port_command_line = debugging_port_command_line
		self.profile_dir_command_line = profile_dir_command_line
		self.headless_mode_command_line = headless_mode_command_line
		self.mute_audio_command_line = mute_audio_command_line
		self.user_agent_command_line = user_agent_command_line
		self.proxy_server_command_line = proxy_server_command_line
		self.debugging_port = None
		self.profile_dir = None
		self.headless_mode = None
		self.mute_audio = None
		self.user_agent = None
		self.proxy_server = None
		self.start_command = build_first_start_argument(self.browser_exe)
		
		self.update_command()
	
	def update_command(self):
		"""
		Updates the start command string based on current settings.
		"""
		start_args = [build_first_start_argument(self.browser_exe)]
		
		if self.debugging_port is not None:
			start_args.append(self.debugging_port_command_line.format(value=self.debugging_port))
		
		if self.profile_dir is not None:
			start_args.append(self.profile_dir_command_line.format(value=self.profile_dir))
		
		if self.headless_mode:
			start_args.append(self.headless_mode_command_line)
		
		if self.mute_audio is not None:
			start_args.append(self.mute_audio_command_line)
		
		if self.user_agent is not None:
			start_args.append(self.user_agent_command_line.format(value=self.user_agent))
		
		if self.proxy_server is not None:
			start_args.append(self.proxy_server_command_line.format(value=self.proxy_server))
		
		self.start_command = " ".join(start_args)
	
	def clear_command(self):
		"""
		Clears all optional arguments from the start command, resetting to the base executable.
		"""
		self.debugging_port = None
		self.profile_dir = None
		self.headless_mode = False
		self.mute_audio = False
		self.user_agent = None
		self.proxy_server = False
		
		self.update_command()
	
	def set_debugging_port(self, debugging_port: Optional[int] = None):
		"""
		Sets the debugging port argument and updates the start command.

		Args:
			debugging_port (Optional[int]): Debugging port number to set. If None, removes debugging port argument. Defaults to None.
		"""
		self.debugging_port = debugging_port
		
		self.update_command()
	
	def set_headless_mode(self, headless_mode: bool = False):
		"""
		Sets the headless mode argument and updates the start command.

		Args:
			headless_mode (bool): Boolean value to enable or disable headless mode. Defaults to False.
		"""
		self.headless_mode = headless_mode
		
		self.update_command()
	
	def set_mute_audio(self, mute_audio: bool = False):
		"""
		Sets the mute audio argument and updates the start command.

		Args:
			mute_audio (bool): Boolean value to enable or disable mute audio. Defaults to False.
		"""
		self.mute_audio = mute_audio
		
		self.update_command()
	
	def set_profile_dir(self, profile_dir: Optional[str] = None):
		"""
		Sets the profile directory argument and updates the start command.

		Args:
			profile_dir (Optional[str]): Profile directory path to set. If None, removes profile directory argument. Defaults to None.
		"""
		self.profile_dir = profile_dir
		
		self.update_command()
	
	def set_proxy_server(self, proxy_server: Optional[Union[str, list[str]]] = None):
		"""
		Sets the proxy server argument and updates the start command.

		Args:
			proxy_server (Optional[Union[str, list[str]]]): Proxy server string to set. If None, removes proxy server argument. Defaults to None. Can be a single proxy string or list of proxy strings, in which case a random proxy will be chosen.
		"""
		if isinstance(proxy_server, list):
			proxy_server = choice(proxy_server)
		
		self.proxy_server = proxy_server
		
		self.update_command()
	
	def set_user_agent(self, user_agent: Optional[str] = None):
		"""
		Sets the user agent argument and updates the start command.

		Args:
			user_agent (Optional[str]): User agent string to set. If None, removes user agent argument. Defaults to None.
		"""
		self.user_agent = user_agent
		
		self.update_command()


class EmptyWebDriver:
	"""
	Provides a simplified interface for interacting with a web driver.

	This class serves as a base for creating WebDriver wrappers, offering a set of commonly used WebDriver actions.
	It is designed to be extended, providing basic functionalities without browser-specific implementations.

	Attributes:
		base_implicitly_wait (int): The base implicit wait time in seconds for element searching.
		base_page_load_timeout (int): The base page load timeout in seconds for page loading.
		driver (webdriver): The underlying WebDriver instance, initialized to None and set upon driver creation in subclasses.
	"""
	
	def __init__(self, implicitly_wait: int = 5, page_load_timeout: int = 5):
		"""
		Initializes an instance of the EmptyWebDriver class.

		Args:
			implicitly_wait (int): The base implicit wait time in seconds. Defaults to 5.
			page_load_timeout (int): The base page load timeout in seconds. Defaults to 5.
		"""
		self.base_implicitly_wait = implicitly_wait
		self.base_page_load_timeout = page_load_timeout
		self.js_scripts = read_js_scripts()
		self.driver = None
	
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
		
		self.driver.implicitly_wait(implicitly_wait)
		self.driver.set_page_load_timeout(page_load_timeout)
	
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
	
	def hover_element(self, element: WebElement):
		"""
		Hovers the mouse over an element.

		Args:
			element (WebElement): The element to hover over.
		"""
		ActionChains(self.driver).move_to_element(element).perform()
	
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
	
	def scroll_by_amount(self, x: int = 0, y: int = 0):
		"""
		Scrolls the viewport by a specified amount.

		Args:
			x (int): Horizontal scroll amount in pixels. Defaults to 0.
			y (int): Vertical scroll amount in pixels. Defaults to 0.
		"""
		ActionChains(self.driver).scroll_by_amount(x, y).perform()
	
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
	
	def scroll_down_of_element(self, by: By, value: str):
		"""
		Scrolls down within a specific element using PAGE_DOWN key.

		Args:
			by (By): Locator Strategy (e.g., By.ID, By.CLASS_NAME).
			value (str): Locator Value (e.g., "scrollableDiv", "content-area").
		"""
		self.find_web_element(by, value).send_keys(Keys.PAGE_DOWN)
	
	def scroll_from_origin(self, origin: ScrollOrigin, x: int = 0, y: int = 0):
		"""
		Scrolls from a specific origin by a specified amount.

		Args:
			origin (ScrollOrigin): The scroll origin (e.g., ScrollOrigin.viewport, ScrollOrigin.element).
			x (int): Horizontal scroll amount in pixels. Defaults to 0.
			y (int): Vertical scroll amount in pixels. Defaults to 0.

		Raises:
			MoveTargetOutOfBoundsException: If the origin with offset is outside the viewport.
		"""
		ActionChains(self.driver).scroll_from_origin(origin, x, y).perform()
	
	def scroll_to_element(self, element: WebElement):
		"""
		Scrolls an element into view.

		Args:
			element (WebElement): The element to scroll into view.
		"""
		ActionChains(self.driver).scroll_to_element(element).perform()
	
	def scroll_up_of_element(self, by: By, value: str):
		"""
		Scrolls up within a specific element using PAGE_UP key.

		Args:
			by (By): Locator strategy (e.g., By.CSS_SELECTOR, By.XPATH).
			value (str): Locator value (e.g., ".scroll-container", "//div[@class='scroll-area']").
		"""
		self.find_web_element(by, value).send_keys(Keys.PAGE_UP)
	
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
	def window(self) -> str:
		"""
		Gets the current window handle.

		Returns:
			str: The current window handle.
		"""
		return self.driver.current_window_handle
	
	@property
	def windows_names(self) -> list[str]:
		"""
		Gets the handles of all open windows.

		Returns:
		   list[str]: A list of window handles.
		"""
		return self.driver.window_handles


class BrowserWebDriver(EmptyWebDriver):
	"""
	Extends EmptyWebDriver to manage a browser instance lifecycle.

	This class inherits from `EmptyWebDriver` and adds functionality to manage the lifecycle of a browser instance,
	including starting, stopping, and restarting the browser with various configurations.

	Attributes:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
		webdriver_path (str): Path to the WebDriver executable.
		window_rect (WindowRect): Object to store window rectangle settings.
		webdriver_start_args (BrowserStartArgs): Manages browser start arguments.
		webdriver_options_manager (BrowserOptionsManager): Manages browser options.
		webdriver_is_active (bool): Flag indicating if the WebDriver is currently active.
		base_implicitly_wait (int): Inherited from EmptyWebDriver, base implicit wait time.
		base_page_load_timeout (int): Inherited from EmptyWebDriver, base page load timeout.
		driver (webdriver): Inherited from EmptyWebDriver, the WebDriver instance.
	"""
	
	def __init__(
			self,
			browser_exe: Union[str, pathlib.Path],
			webdriver_path: str,
			webdriver_start_args: type = BrowserStartArgs,
			webdriver_options_manager: type = BrowserOptionsManager,
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
			webdriver_start_args (type): Class type for managing browser start arguments. Defaults to BrowserStartArgs.
			webdriver_options_manager (type): Class type for managing browser options. Defaults to BrowserOptionsManager.
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
		super().__init__(implicitly_wait, page_load_timeout)
		
		if window_rect is None:
			window_rect = WindowRect()
		
		self.browser_exe = browser_exe
		self.webdriver_path = webdriver_path
		self.window_rect = window_rect
		
		self.webdriver_start_args = webdriver_start_args(browser_exe=browser_exe)
		
		self.webdriver_options_manager = webdriver_options_manager()
		self.webdriver_is_active = False
		
		self.update_settings(
				debugging_port=debugging_port,
				profile_dir=profile_dir,
				headless_mode=headless_mode,
				mute_audio=mute_audio,
				proxy=proxy,
				user_agent=user_agent
		)
	
	def get_vars_for_remote(self):
		"""
		Gets variables necessary to create a remote WebDriver instance.

		Returns:
			tuple: A tuple containing the command executor URL and session ID of the WebDriver.
		"""
		return self.driver.command_executor, self.driver.session_id
	
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
	
	def check_webdriver_active(self):
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
