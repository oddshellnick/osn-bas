import trio
import pathlib
from selenium import webdriver
from types import TracebackType
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.bidi.cdp import CdpSession
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.actions.key_input import KeyInput
from selenium.webdriver.remote.bidi_connection import BidiConnection
from osn_bas.webdrivers.BaseDriver.start_args import BrowserStartArgs
from osn_bas.types import (
	Position,
	Rectangle,
	Size,
	WindowRect
)
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.remote.remote_connection import RemoteConnection
from osn_bas.webdrivers.BaseDriver.options import (
	BrowserOptionsManager
)
from contextlib import (
	AbstractAsyncContextManager,
	asynccontextmanager
)
from selenium.webdriver.common.actions.wheel_input import (
	ScrollOrigin,
	WheelInput
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
	
	async def build_action_chains(
			self,
			duration: int = 250,
			devices: Optional[list[Union[PointerInput, KeyInput, WheelInput]]] = None
	) -> ActionChains:
		"""
		Builds and returns a new Selenium ActionChains instance.

		Initializes an ActionChains object associated with the current WebDriver instance (`self.driver`).
		Allows specifying the default pause duration between actions and custom input device sources.

		Args:
			duration (int): The default duration in milliseconds to pause between actions
				within the chain. Defaults to 250.
			devices (Optional[List[Union[PointerInput, KeyInput, WheelInput]]]): A list of
				specific input device sources (Pointer, Key, Wheel) to use for the actions.
				If None, default devices are used. Defaults to None.

		Returns:
			ActionChains: A new ActionChains instance configured with the specified driver,
				duration, and devices.
		"""
		
		...
	
	async def check_element_in_viewport(self, element: WebElement) -> bool:
		"""
		Checks if the specified web element is currently within the browser's viewport.

		Executes a predefined JavaScript snippet to determine the visibility status.

		Args:
			element (WebElement): The Selenium WebElement to check.

		Returns:
			bool: True if the element is at least partially within the viewport, False otherwise.
		"""
		
		...
	
	async def check_webdriver_active(self) -> bool:
		"""
		Checks if the WebDriver is active by verifying if the debugging port is in use.

		Determines if a WebDriver instance is currently running and active by checking if the configured
		debugging port is in use by any process. This is a way to verify if a browser session is active
		without directly querying the WebDriver itself.

		Returns:
			bool: True if the WebDriver is active (debugging port is in use), False otherwise.
		"""
		
		...
	
	async def click_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a click action. Clicks on the specified element or the current mouse position if no element is provided.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to click. If None, clicks at the
				current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the click action added, allowing for method chaining.
		"""
		
		...
	
	async def click_and_hold_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a click-and-hold action. Holds down the left mouse button on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to click and hold. If None, clicks
				and holds at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the click-and-hold action added, allowing for method chaining.
		"""
		
		...
	
	async def close_all_windows(self):
		"""
		Closes all open windows.

		Iterates through all window handles and closes each window associated with the WebDriver instance.
		This effectively closes the entire browser session managed by the driver.
		"""
		
		...
	
	async def close_webdriver(self):
		"""
		Closes the WebDriver instance and terminates the associated browser subprocess.

		Quits the current WebDriver session, closes all browser windows, and then forcefully terminates
		the browser process. This ensures a clean shutdown of the browser and WebDriver environment.
		"""
		
		...
	
	async def close_window(self, window: Optional[Union[str, int]] = None):
		"""
		Closes the specified browser window and manages focus switching.

		Identifies the target window to close using get_window_handle. Switches to that window,
		closes it, and then switches focus back. If the closed window was the currently focused
		window, it switches focus to the last window in the remaining list. Otherwise, it switches
		back to the window that had focus before the close operation began.

		Args:
			window (Optional[Union[str, int]]): The identifier of the window to close.
				Can be a window handle (string), an index (int), or None to close the
				currently focused window.
		"""
		
		...
	
	async def context_click_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a context-click (right-click) action. Performs the action on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to context-click. If None, performs
				the context-click at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the context-click action added, allowing for method chaining.
		"""
		
		...
	
	async def create_driver(self):
		"""
		Abstract method to create a WebDriver instance. Must be implemented in child classes.

		This method is intended to be overridden in subclasses to provide browser-specific
		WebDriver instantiation logic (e.g., creating ChromeDriver, FirefoxDriver, etc.).

		Raises:
			NotImplementedError: If the method is not implemented in a subclass.
		"""
		
		...
	
	@property
	def current_url(self) -> str:
		"""
		Gets the current URL.

		Retrieves the URL of the current page loaded in the browser window under WebDriver control.

		Returns:
			str: The current URL of the webpage.
		"""
		
		...
	
	@property
	def current_window_handle(self) -> str:
		"""
		Gets the current window handle.

		Retrieves the handle of the currently active browser window or tab. Window handles are unique identifiers
		used by WebDriver to distinguish between different browser windows.

		Returns:
			str: The current window handle.
		"""
		
		...
	
	@property
	def debugging_port(self) -> Optional[int]:
		"""
		Gets the currently set debugging port.

		Retrieves the debugging port number that the browser instance is configured to use.

		Returns:
			Optional[int]: The debugging port number, or None if not set.
		"""
		
		...
	
	async def double_click_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a double-click action. Performs the action on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to double-click. If None, double-clicks
				at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the double-click action added, allowing for method chaining.
		"""
		
		...
	
	async def drag_and_drop_action(
			self,
			source_element: WebElement,
			target_element: WebElement,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a drag-and-drop action from a source element to a target element.

		Combines click-and-hold on the source, move to the target, and release.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			source_element (WebElement): The element to click and hold (the start of the drag).
			target_element (WebElement): The element to move to and release over (the end of the drop).
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the drag-and-drop action added, allowing for method chaining.
		"""
		
		...
	
	async def drag_and_drop_by_offset_action(
			self,
			source_element: WebElement,
			xoffset: int,
			yoffset: int,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a drag-and-drop action from a source element by a given offset.

		Combines click-and-hold on the source, move by the offset, and release.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			source_element (WebElement): The element to click and hold (the start of the drag).
			xoffset (int): The horizontal distance to move the mouse.
			yoffset (int): The vertical distance to move the mouse.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the drag-and-drop by offset action added, allowing for method chaining.
		"""
		
		...
	
	async def execute_js_script(self, script: str, *args) -> Any:
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
		
		...
	
	async def find_debugging_port(self, debugging_port: Optional[int], profile_dir: Optional[str]) -> int:
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
		
		...
	
	async def find_inner_web_element(
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
		
		...
	
	async def find_inner_web_elements(
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
		
		...
	
	async def find_web_element(
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
		
		...
	
	async def find_web_elements(
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
		
		...
	
	async def get_document_scroll_size(self) -> Size:
		"""
		Gets the total scrollable dimensions of the HTML document.

		Executes a predefined JavaScript snippet to retrieve the document's scrollWidth
		and scrollHeight.

		Returns:
			Size: A TypedDict where 'width' represents the document's scrollWidth,
					   'height' represents the scrollHeight.
		"""
		
		...
	
	async def get_element_css_style(self, element: WebElement) -> dict[str, str]:
		"""
		Retrieves the computed CSS style of a WebElement.

		Uses JavaScript to get all computed CSS properties and their values for a given web element.
		Returns a dictionary where keys are CSS property names and values are their computed values.

		Args:
			element (WebElement): The WebElement for which to retrieve the CSS style.

		Returns:
			dict[str, str]: A dictionary of CSS property names and their computed values as strings.
		"""
		
		...
	
	async def get_element_rect_in_viewport(self, element: WebElement) -> Rectangle:
		"""
		Gets the position and dimensions of an element relative to the viewport.

		Executes a predefined JavaScript snippet that calculates the element's bounding rectangle
		as seen in the current viewport.

		Args:
			element (WebElement): The Selenium WebElement whose rectangle is needed.

		Returns:
			Rectangle: A TypedDict containing the 'x', 'y', 'width', and 'height' of the element
					   relative to the viewport's top-left corner. 'x' and 'y' can be negative
					   if the element is partially scrolled out of view to the top or left.
		"""
		
		...
	
	async def get_random_element_point_in_viewport(self, element: WebElement, step: int = 1) -> Optional[Position]:
		"""
		Calculates a random point within the visible portion of a given element in the viewport.

		Executes a predefined JavaScript snippet that determines the element's bounding box
		relative to the viewport, calculates the intersection of this box with the viewport,
		and then selects a random point within that intersection, potentially aligned to a grid defined by `step`.

		Args:
			element (WebElement): The Selenium WebElement to find a random point within.
			step (int): Defines the grid step for selecting the random point. The coordinates
				will be multiples of this step within the valid range. Defaults to 1 (any pixel).

		Returns:
			Position: A TypedDict containing the integer 'x' and 'y' coordinates of a random point
					  within the element's visible area in the viewport. Coordinates are relative
					  to the element's top-left corner (0,0).
		"""
		
		...
	
	async def get_vars_for_remote(self) -> tuple[RemoteConnection, str]:
		"""
		Gets variables necessary to create a remote WebDriver instance.

		Provides the command executor and session ID of the current WebDriver instance.
		These are needed to re-establish a connection to the same browser session from a different WebDriver client,
		for example, in a distributed testing environment.

		Returns:
			tuple[RemoteConnection, str]: A tuple containing the command executor (for establishing connection) and session ID (for session identification).
		"""
		
		...
	
	async def get_viewport_position(self) -> Position:
		"""
		Gets the current scroll position of the viewport relative to the document origin (0,0).

		Executes a predefined JavaScript snippet to retrieve window.scrollX and window.scrollY.

		Returns:
			Position: A TypedDict containing the 'x' (horizontal scroll offset) and
					  'y' (vertical scroll offset) of the viewport.
		"""
		
		...
	
	async def get_viewport_rect(self) -> Rectangle:
		"""
		Gets the position and dimensions of the viewport relative to the document origin.

		Combines the scroll position (top-left corner) and the viewport dimensions.
		Executes a predefined JavaScript snippet.

		Returns:
			Rectangle: A TypedDict where 'x' and 'y' represent the current scroll offsets
					   (window.pageXOffset, window.pageYOffset) and 'width' and 'height' represent
					   the viewport dimensions (window.innerWidth, window.innerHeight).
		"""
		
		...
	
	async def get_viewport_size(self) -> Size:
		"""
		Gets the current dimensions (width and height) of the browser's viewport.

		Executes a predefined JavaScript snippet to retrieve the inner width and height
		of the window.

		Returns:
			Size: A TypedDict containing the 'width' and 'height' of the viewport in pixels.
		"""
		
		...
	
	async def get_window_handle(self, window: Optional[Union[str, int]] = None) -> str:
		"""
		Retrieves a window handle string based on the provided identifier.

		If the identifier is already a string, it's assumed to be a valid handle and returned directly.
		If it's an integer, it's treated as an index into the list of currently open window handles.
		If it's None or not provided, the handle of the currently active window is returned.

		Args:
			window (Optional[Union[str, int]]): The identifier for the desired window handle.
				- str: Assumed to be the window handle itself.
				- int: Index into the list of window handles (self.driver.window_handles).
				- None: Get the handle of the currently focused window.

		Returns:
			str: The window handle string corresponding to the input identifier.
		"""
		
		...
	
	async def hide_automation(self, hide: bool):
		"""
		Sets whether to hide browser automation indicators.

		This method configures the browser options to hide or show automation
		indicators, which are typically present when a browser is controlled by WebDriver.

		Args:
			hide (bool): If True, hides automation indicators; otherwise, shows them.
		"""
		
		...
	
	@property
	def html(self) -> str:
		"""
		Gets the current page source.

		Retrieves the HTML source code of the currently loaded webpage. This is useful for
		inspecting the page structure and content, especially for debugging or data extraction purposes.

		Returns:
			str: The HTML source code of the current page.
		"""
		
		...
	
	@property
	def is_active(self) -> bool:
		"""
		Checks if the WebDriver instance is currently active and connected.

		This property provides a way to determine the current status of the WebDriver.
		It reflects whether the WebDriver is initialized and considered operational.

		Returns:
			bool: True if the WebDriver is active, False otherwise.
		"""
		
		...
	
	async def key_down_action(
			self,
			value: str,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a key down (press and hold) action for a specific modifier key.

		Sends the key press to the specified element or the currently focused element.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			value (str): The modifier key to press (e.g., Keys.CONTROL, Keys.SHIFT).
			element (Optional[WebElement]): The element to send the key press to. If None,
				sends to the currently focused element. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the key down action added, allowing for method chaining.
		"""
		
		...
	
	async def key_up_action(
			self,
			value: str,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a key up (release) action for a specific modifier key.

		Sends the key release to the specified element or the currently focused element.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action. Typically used after `key_down_action`.

		Args:
			value (str): The modifier key to release (e.g., Keys.CONTROL, Keys.SHIFT).
			element (Optional[WebElement]): The element to send the key release to. If None,
				sends to the currently focused element. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the key up action added, allowing for method chaining.
		"""
		
		...
	
	async def move_to_element_action(
			self,
			element: WebElement,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a move mouse cursor action to the specified web element.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (WebElement): The target web element to move the mouse to.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the move action added, allowing for method chaining.
		"""
		
		...
	
	async def move_to_element_with_offset_action(
			self,
			element: WebElement,
			xoffset: int,
			yoffset: int,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds an action to move the mouse cursor to an offset from the center of a specified element.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (WebElement): The target web element to base the offset from.
			xoffset (int): The horizontal offset from the element's center. Positive is right, negative is left.
			yoffset (int): The vertical offset from the element's center. Positive is down, negative is up.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the move-with-offset action added, allowing for method chaining.
		"""
		
		...
	
	async def open_new_tab(self, link: str = ""):
		"""
		Opens a new tab with the given URL.

		Opens a new browser tab and optionally navigates it to a specified URL. If no URL is provided, a blank tab is opened.

		Args:
			link (str): URL to open in the new tab. If empty, opens a blank tab. Defaults to "".
		"""
		
		...
	
	@property
	def rect(self) -> WindowRect:
		"""
		Gets the window rectangle.

		Retrieves the current position and size of the browser window as a `WindowRect` object.
		This object contains the x and y coordinates of the window's top-left corner, as well as its width and height.

		Returns:
			WindowRect: The window rectangle object containing x, y, width, and height.
		"""
		
		...
	
	async def refresh_webdriver(self):
		"""
		Refreshes the current page.

		Reloads the currently loaded webpage in the browser. This action fetches the latest version of the page from the server.
		"""
		
		...
	
	async def release_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a release mouse button action. Releases the depressed left mouse button on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action. Typically used after a `click_and_hold_action`.

		Args:
			element (Optional[WebElement]): The web element on which to release the mouse button.
				If None, releases at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the release action added, allowing for method chaining.
		"""
		
		...
	
	async def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str):
		"""
		Connects to an existing remote WebDriver session.

		This method establishes a connection to a remote Selenium WebDriver server and reuses an existing browser session, instead of creating a new one.
		It's useful when you want to attach to an already running browser instance, managed by a remote WebDriver service like Selenium Grid or cloud-based Selenium providers.

		Args:
			command_executor (Union[str, RemoteConnection]): The URL of the remote WebDriver server or a `RemoteConnection` object.
			session_id (str): The ID of the existing WebDriver session to connect to.
		"""
		
		...
	
	async def reset_settings(
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
		
		...
	
	async def scroll_by_amount_action(
			self,
			delta_x: int,
			delta_y: int,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a scroll action to the current mouse position by the specified amounts.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			delta_x (int): The amount to scroll horizontally. Positive scrolls right, negative scrolls left.
			delta_y (int): The amount to scroll vertically. Positive scrolls down, negative scrolls up.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the scroll action added, allowing for method chaining.
		"""
		
		...
	
	async def scroll_from_origin_action(
			self,
			origin: ScrollOrigin,
			delta_x: int,
			delta_y: int,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a scroll action relative to a specified origin (viewport or element center).

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			origin (ScrollOrigin): The origin point for the scroll. This object defines
				whether the scroll is relative to the viewport or an element's center.
				Use `ScrollOrigin.from_viewport()` or `ScrollOrigin.from_element()`.
			delta_x (int): The horizontal scroll amount. Positive scrolls right, negative left.
			delta_y (int): The vertical scroll amount. Positive scrolls down, negative up.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the scroll action added, allowing for method chaining.
		"""
		
		...
	
	async def scroll_to_element_action(
			self,
			element: WebElement,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds an action to scroll the viewport until the specified element is in view.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (WebElement): The target web element to scroll into view.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the scroll-to-element action added, allowing for method chaining.
		"""
		
		...
	
	async def search_url(
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
		
		...
	
	async def send_keys_action(
			self,
			keys_to_send: str,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a send keys action to the currently focused element.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			keys_to_send (str): The sequence of keys to send.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the send keys action added, allowing for method chaining.
		"""
		
		...
	
	async def send_keys_to_element_action(
			self,
			element: WebElement,
			keys_to_send: str,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a send keys action specifically to the provided web element.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (WebElement): The target web element to send keys to.
			keys_to_send (str): The sequence of keys to send.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the send keys to element action added, allowing for method chaining.
		"""
		
		...
	
	async def set_debugging_port(self, debugging_port: Optional[int]):
		"""
		Sets the debugging port.

		Configures the browser to start with a specific debugging port. This port is used for external tools,
		like debuggers or browser automation frameworks, to connect to and control the browser instance.
		Setting a fixed debugging port can be useful for consistent remote debugging or automation setups.

		Args:
			debugging_port (Optional[int]): Debugging port number. If None, the browser chooses a port automatically.
		"""
		
		...
	
	async def set_driver_timeouts(self, page_load_timeout: float, implicit_wait_timeout: float):
		"""
		Sets both page load timeout and implicit wait timeout for WebDriver.

		A convenience method to set both the page load timeout and the implicit wait timeout
		in a single operation. This can simplify timeout configuration at the start of tests or
		when adjusting timeouts dynamically.

		Args:
			page_load_timeout (float): The page load timeout value in seconds.
			implicit_wait_timeout (float): The implicit wait timeout value in seconds.
		"""
		
		...
	
	async def set_enable_devtools(self, enable_devtools: bool):
		"""
		Enables or disables the BiDi protocol for DevTools.

		Controls whether the BiDi (Bidirectional) protocol is enabled for communication with browser developer tools.
		Enabling DevTools allows for advanced browser interaction, network interception, and performance analysis.

		Args:
			enable_devtools (bool): True to enable DevTools, False to disable.
		"""
		
		...
	
	async def set_headless_mode(self, headless_mode: bool):
		"""
		Sets headless mode.

		Enables or disables headless browsing. In headless mode, the browser runs in the background without a visible UI.
		This is often used for automated testing and scraping to save resources and improve performance.

		Args:
			headless_mode (bool): Whether to start the browser in headless mode. True for headless, False for visible browser UI.
		"""
		
		...
	
	async def set_implicitly_wait_timeout(self, timeout: float):
		"""
		Sets the implicit wait timeout for WebDriver element searches.

		Configures the implicit wait time, which is the maximum time WebDriver will wait
		when searching for elements before throwing a `NoSuchElementException`. This setting
		applies globally to all element searches for the duration of the WebDriver session.

		Args:
			timeout (float): The implicit wait timeout value in seconds.
		"""
		
		...
	
	async def set_mute_audio(self, mute_audio: bool):
		"""
		Sets mute audio mode.

		Configures the browser to mute or unmute audio output. Muting audio can be useful in automated testing
		environments to prevent sound from interfering with tests or to conserve system resources.

		Args:
			mute_audio (bool): Whether to mute audio in the browser. True to mute, False to unmute.
		"""
		
		...
	
	async def set_page_load_timeout(self, timeout: float):
		"""
		Sets the page load timeout for WebDriver operations.

		Defines the maximum time WebDriver will wait for a page to fully load before timing out
		and throwing a `TimeoutException`. This is useful to prevent tests from hanging indefinitely
		on slow-loading pages.

		Args:
			timeout (float): The page load timeout value in seconds.
		"""
		
		...
	
	async def set_profile_dir(self, profile_dir: Optional[str]):
		"""
		Sets the profile directory.

		Specifies a custom browser profile directory to be used by the browser instance. Browser profiles store user-specific
		data such as bookmarks, history, cookies, and extensions. Using profiles allows for persistent browser settings
		across sessions and can be useful for testing with specific browser states.

		Args:
			profile_dir (Optional[str]): Path to the browser profile directory. If None, a default or temporary profile is used.
		"""
		
		...
	
	async def set_proxy(self, proxy: Optional[Union[str, list[str]]]):
		"""
		Sets the proxy.

		Configures the browser to use a proxy server for network requests. This can be a single proxy server or a list
		of proxy servers, from which one will be randomly selected for use. Proxies are used to route browser traffic
		through an intermediary server, often for anonymity, security, or accessing geo-restricted content.

		Args:
			proxy (Optional[Union[str, list[str]]]): Proxy server address or list of addresses. If a list is provided, a proxy will be randomly chosen from the list.
				If None, proxy settings are removed.
		"""
		
		...
	
	async def set_start_page_url(self, start_page_url: str):
		"""
		Sets the URL that the WebDriver will navigate to upon starting.

		Updates an internal configuration attribute (`_webdriver_start_args.start_page_url`)
		which is presumably used during WebDriver initialization.

		Args:
			start_page_url (str): The absolute URL for the browser to load initially.
		"""
		
		...
	
	async def set_user_agent(self, user_agent: Optional[str]):
		"""
		Sets the user agent.

		Configures the browser to use a specific user agent string. Overriding the default user agent
		can be useful for testing website behavior under different browser or device conditions, or for privacy purposes.

		Args:
			user_agent (Optional[str]): User agent string to use. If None, the user agent setting is removed, reverting to the browser's default.
		"""
		
		...
	
	async def set_window_rect(self, rect: WindowRect):
		"""
		Sets the browser window rectangle.

		Adjusts the position and size of the browser window to the specified rectangle. This can be used
		to manage window placement and dimensions for testing or display purposes.

		Args:
			rect (WindowRect): An object containing the desired window rectangle parameters (x, y, width, height).
		"""
		
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
		
		...
	
	async def stop_window_loading(self):
		"""
		Stops the current page loading.

		Interrupts the loading process of the current webpage. This can be useful when a page is taking too long
		to load or when you want to halt resource loading for performance testing or specific scenarios.
		"""
		
		...
	
	async def switch_to_frame(self, frame: Union[str, int, WebElement]):
		"""
		Switches the driver's focus to a frame.

		Changes the WebDriver's focus to a specific frame within the current page. Frames are often used to embed
		content from other sources within a webpage. After switching to a frame, all WebDriver commands will be
		directed to elements within that frame until focus is switched back.

		Args:
			frame (Union[str, int, WebElement]): Specifies the frame to switch to. Can be a frame name (str), index (int), or a WebElement representing the frame.
		"""
		
		...
	
	async def switch_to_window(self, window: Optional[Union[str, int]] = None):
		"""
		Switches the driver's focus to the specified browser window.

		Uses get_window_handle to resolve the target window identifier (handle string or index)
		before instructing the driver to switch. If no window identifier is provided,
		it effectively switches to the current window.

		Args:
			window (Optional[Union[str, int]]): The identifier of the window to switch to.
				Can be a window handle (string) or an index (int) in the list of window handles.
				If None, targets the current window handle.
		"""
		
		...
	
	async def update_settings(
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
		
		...
	
	async def update_times(
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
		
		...
	
	@property
	def windows_handles(self) -> list[str]:
		"""
		Gets the handles of all open windows.

		Returns a list of handles for all browser windows or tabs currently open and managed by the WebDriver.
		This is useful for iterating through or managing multiple windows in a browser session.

		Returns:
		   list[str]: A list of window handles. Each handle is a string identifier for an open window.
		"""
		
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
	
	def build_action_chains(
			self,
			duration: int = 250,
			devices: Optional[list[Union[PointerInput, KeyInput, WheelInput]]] = None
	) -> ActionChains:
		"""
		Builds and returns a new Selenium ActionChains instance.

		Initializes an ActionChains object associated with the current WebDriver instance (`self.driver`).
		Allows specifying the default pause duration between actions and custom input device sources.

		Args:
			duration (int): The default duration in milliseconds to pause between actions
				within the chain. Defaults to 250.
			devices (Optional[List[Union[PointerInput, KeyInput, WheelInput]]]): A list of
				specific input device sources (Pointer, Key, Wheel) to use for the actions.
				If None, default devices are used. Defaults to None.

		Returns:
			ActionChains: A new ActionChains instance configured with the specified driver,
				duration, and devices.
		"""
		
		...
	
	def check_element_in_viewport(self, element: WebElement) -> bool:
		"""
		Checks if the specified web element is currently within the browser's viewport.

		Executes a predefined JavaScript snippet to determine the visibility status.

		Args:
			element (WebElement): The Selenium WebElement to check.

		Returns:
			bool: True if the element is at least partially within the viewport, False otherwise.
		"""
		
		...
	
	def click_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a click action. Clicks on the specified element or the current mouse position if no element is provided.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to click. If None, clicks at the
				current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the click action added, allowing for method chaining.
		"""
		
		...
	
	def click_and_hold_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a click-and-hold action. Holds down the left mouse button on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to click and hold. If None, clicks
				and holds at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the click-and-hold action added, allowing for method chaining.
		"""
		
		...
	
	def close_all_windows(self):
		"""
		Closes all open windows.

		Iterates through all window handles and closes each window associated with the WebDriver instance.
		This effectively closes the entire browser session managed by the driver.
		"""
		
		...
	
	def close_window(self, window: Optional[Union[str, int]] = None):
		"""
		Closes the specified browser window and manages focus switching.

		Identifies the target window to close using get_window_handle. Switches to that window,
		closes it, and then switches focus back. If the closed window was the currently focused
		window, it switches focus to the last window in the remaining list. Otherwise, it switches
		back to the window that had focus before the close operation began.

		Args:
			window (Optional[Union[str, int]]): The identifier of the window to close.
				Can be a window handle (string), an index (int), or None to close the
				currently focused window.
		"""
		
		...
	
	def context_click_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a context-click (right-click) action. Performs the action on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to context-click. If None, performs
				the context-click at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the context-click action added, allowing for method chaining.
		"""
		
		...
	
	@property
	def current_url(self) -> str:
		"""
		Gets the current URL.

		Retrieves the URL of the current page loaded in the browser window under WebDriver control.

		Returns:
			str: The current URL of the webpage.
		"""
		
		...
	
	@property
	def current_window_handle(self) -> str:
		"""
		Gets the current window handle.

		Retrieves the handle of the currently active browser window or tab. Window handles are unique identifiers
		used by WebDriver to distinguish between different browser windows.

		Returns:
			str: The current window handle.
		"""
		
		...
	
	def double_click_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a double-click action. Performs the action on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (Optional[WebElement]): The web element to double-click. If None, double-clicks
				at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the double-click action added, allowing for method chaining.
		"""
		
		...
	
	def drag_and_drop_action(
			self,
			source_element: WebElement,
			target_element: WebElement,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a drag-and-drop action from a source element to a target element.

		Combines click-and-hold on the source, move to the target, and release.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			source_element (WebElement): The element to click and hold (the start of the drag).
			target_element (WebElement): The element to move to and release over (the end of the drop).
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the drag-and-drop action added, allowing for method chaining.
		"""
		
		...
	
	def drag_and_drop_by_offset_action(
			self,
			source_element: WebElement,
			xoffset: int,
			yoffset: int,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a drag-and-drop action from a source element by a given offset.

		Combines click-and-hold on the source, move by the offset, and release.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			source_element (WebElement): The element to click and hold (the start of the drag).
			xoffset (int): The horizontal distance to move the mouse.
			yoffset (int): The vertical distance to move the mouse.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the drag-and-drop by offset action added, allowing for method chaining.
		"""
		
		...
	
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
		
		...
	
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
		
		...
	
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
		
		...
	
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
		
		...
	
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
		
		...
	
	def get_document_scroll_size(self) -> Size:
		"""
		Gets the total scrollable dimensions of the HTML document.

		Executes a predefined JavaScript snippet to retrieve the document's scrollWidth
		and scrollHeight.

		Returns:
			Size: A TypedDict where 'width' represents the document's scrollWidth,
					   'height' represents the scrollHeight.
		"""
		
		...
	
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
		
		...
	
	def get_element_rect_in_viewport(self, element: WebElement) -> Rectangle:
		"""
		Gets the position and dimensions of an element relative to the viewport.

		Executes a predefined JavaScript snippet that calculates the element's bounding rectangle
		as seen in the current viewport.

		Args:
			element (WebElement): The Selenium WebElement whose rectangle is needed.

		Returns:
			Rectangle: A TypedDict containing the 'x', 'y', 'width', and 'height' of the element
					   relative to the viewport's top-left corner. 'x' and 'y' can be negative
					   if the element is partially scrolled out of view to the top or left.
		"""
		
		...
	
	def get_random_element_point_in_viewport(self, element: WebElement, step: int = 1) -> Optional[Position]:
		"""
		Calculates a random point within the visible portion of a given element in the viewport.

		Executes a predefined JavaScript snippet that determines the element's bounding box
		relative to the viewport, calculates the intersection of this box with the viewport,
		and then selects a random point within that intersection, potentially aligned to a grid defined by `step`.

		Args:
			element (WebElement): The Selenium WebElement to find a random point within.
			step (int): Defines the grid step for selecting the random point. The coordinates
				will be multiples of this step within the valid range. Defaults to 1 (any pixel).

		Returns:
			Position: A TypedDict containing the integer 'x' and 'y' coordinates of a random point
					  within the element's visible area in the viewport. Coordinates are relative
					  to the element's top-left corner (0,0).
		"""
		
		...
	
	def get_vars_for_remote(self) -> tuple[RemoteConnection, str]:
		"""
		Gets variables necessary to create a remote WebDriver instance.

		Provides the command executor and session ID of the current WebDriver instance.
		These are needed to re-establish a connection to the same browser session from a different WebDriver client,
		for example, in a distributed testing environment.

		Returns:
			tuple[RemoteConnection, str]: A tuple containing the command executor (for establishing connection) and session ID (for session identification).
		"""
		
		...
	
	def get_viewport_position(self) -> Position:
		"""
		Gets the current scroll position of the viewport relative to the document origin (0,0).

		Executes a predefined JavaScript snippet to retrieve window.scrollX and window.scrollY.

		Returns:
			Position: A TypedDict containing the 'x' (horizontal scroll offset) and
					  'y' (vertical scroll offset) of the viewport.
		"""
		
		...
	
	def get_viewport_rect(self) -> Rectangle:
		"""
		Gets the position and dimensions of the viewport relative to the document origin.

		Combines the scroll position (top-left corner) and the viewport dimensions.
		Executes a predefined JavaScript snippet.

		Returns:
			Rectangle: A TypedDict where 'x' and 'y' represent the current scroll offsets
					   (window.pageXOffset, window.pageYOffset) and 'width' and 'height' represent
					   the viewport dimensions (window.innerWidth, window.innerHeight).
		"""
		
		...
	
	def get_viewport_size(self) -> Size:
		"""
		Gets the current dimensions (width and height) of the browser's viewport.

		Executes a predefined JavaScript snippet to retrieve the inner width and height
		of the window.

		Returns:
			Size: A TypedDict containing the 'width' and 'height' of the viewport in pixels.
		"""
		
		...
	
	def get_window_handle(self, window: Optional[Union[str, int]] = None) -> str:
		"""
		Retrieves a window handle string based on the provided identifier.

		If the identifier is already a string, it's assumed to be a valid handle and returned directly.
		If it's an integer, it's treated as an index into the list of currently open window handles.
		If it's None or not provided, the handle of the currently active window is returned.

		Args:
			window (Optional[Union[str, int]]): The identifier for the desired window handle.
				- str: Assumed to be the window handle itself.
				- int: Index into the list of window handles (self.driver.window_handles).
				- None: Get the handle of the currently focused window.

		Returns:
			str: The window handle string corresponding to the input identifier.
		"""
		
		...
	
	def hide_automation(self, hide: bool):
		"""
		Sets whether to hide browser automation indicators.

		This method configures the browser
		"""
		
	
	@property
	def html(self) -> str:
		"""
		Gets the current page source.

		Retrieves the HTML source code of the currently loaded webpage. This is useful for
		inspecting the page structure and content, especially for debugging or data extraction purposes.

		Returns:
			str: The HTML source code of the current page.
		"""
		
		...
	
	@property
	def is_active(self) -> bool:
		"""
		Checks if the WebDriver instance is currently active and connected.

		This property provides a way to determine the current status of the WebDriver.
		It reflects whether the WebDriver is initialized and considered operational.

		Returns:
			bool: True if the WebDriver is active, False otherwise.
		"""
		
		...
	
	def key_down_action(
			self,
			value: str,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a key down (press and hold) action for a specific modifier key.

		Sends the key press to the specified element or the currently focused element.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			value (str): The modifier key to press (e.g., Keys.CONTROL, Keys.SHIFT).
			element (Optional[WebElement]): The element to send the key press to. If None,
				sends to the currently focused element. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the key down action added, allowing for method chaining.
		"""
		
		...
	
	def key_up_action(
			self,
			value: str,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a key up (release) action for a specific modifier key.

		Sends the key release to the specified element or the currently focused element.
		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action. Typically used after `key_down_action`.

		Args:
			value (str): The modifier key to release (e.g., Keys.CONTROL, Keys.SHIFT).
			element (Optional[WebElement]): The element to send the key release to. If None,
				sends to the currently focused element. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the key up action added, allowing for method chaining.
		"""
		
		...
	
	def move_to_element_action(
			self,
			element: WebElement,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a move mouse cursor action to the specified web element.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (WebElement): The target web element to move the mouse to.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the move action added, allowing for method chaining.
		"""
		
		...
	
	def move_to_element_with_offset_action(
			self,
			element: WebElement,
			xoffset: int,
			yoffset: int,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds an action to move the mouse cursor to an offset from the center of a specified element.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action.

		Args:
			element (WebElement): The target web element to base the offset from.
			xoffset (int): The horizontal offset from the element's center. Positive is right, negative is left.
			yoffset (int): The vertical offset from the element's center. Positive is down, negative is up.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the move-with-offset action added, allowing for method chaining.
		"""
		
		...
	
	def open_new_tab(self, link: str = ""):
		"""
		Opens a new tab with the given URL.

		Opens a new browser tab and optionally navigates it to a specified URL. If no URL is provided, a blank tab is opened.

		Args:
			link (str): URL to open in the new tab. If empty, opens a blank tab. Defaults to "".
		"""
		
		...
	
	@property
	def rect(self) -> WindowRect:
		"""
		Gets the window rectangle.

		Retrieves the current position and size of the browser window as a `WindowRect` object.
		This object contains the x and y coordinates of the window's top-left corner, as well as its width and height.

		Returns:
			WindowRect: The window rectangle object containing x, y, width, and height.
		"""
		
		...
	
	def refresh_webdriver(self):
		"""
		Refreshes the current page.

		Reloads the currently loaded webpage in the browser. This action fetches the latest version of the page from the server.
		"""
		
		...
	
	def release_action(
			self,
			element: Optional[WebElement] = None,
			duration: int = 250,
			action_chain: Optional[ActionChains] = None
	) -> ActionChains:
		"""
		Adds a release mouse button action. Releases the depressed left mouse button on the specified element or the current mouse position.

		If an existing ActionChains object is provided via `action_chain`, this action
		is appended to it. Otherwise, a new ActionChains object is created using
		`self.build_action_chains` with the specified duration before adding the action. Typically used after a `click_and_hold_action`.

		Args:
			element (Optional[WebElement]): The web element on which to release the mouse button.
				If None, releases at the current mouse cursor position. Defaults to None.
			duration (int): The duration in milliseconds to use when creating a new
				ActionChains instance if `action_chain` is None. Defaults to 250.
			action_chain (Optional[ActionChains]): An existing ActionChains instance to append
				this action to. If None, a new chain is created. Defaults to None.

		Returns:
			ActionChains: The ActionChains instance (either the one passed in or a new one)
				with the release action added, allowing for method chaining.
		"""
		
		...
	
	def remote_connect_driver(self, command_executor: Union[str, RemoteConnection], session_id: str):
		"""
		Connects to an existing remote WebDriver session.

		This method establishes a connection to a remote Selenium WebDriver server and reuses an existing browser session, instead of creating a new one.
		It's useful when you want to attach to an already running browser instance, managed by a remote WebDriver service like Selenium Grid or cloud-based Selenium providers.

		Args:
			command_executor (Union[str, RemoteConnection]): The URL of the remote WebDriver server or a `RemoteConnection` object.
			session_id (str): The ID of the existing WebDriver session to connect to.
		"""
		
		...
	
	def set_debugging_port(self, debugging_port: Optional[int]):
		"""
		Sets the debugging port.

		Configures the browser to start with a specific debugging port. This port is used for external tools,
		like debuggers or browser automation frameworks, to connect to and control the browser instance.
		Setting a fixed debugging port can be useful for consistent remote debugging or automation setups.

		Args:
			debugging_port (Optional[int]): Debugging port number. If None, the browser chooses a port automatically.
		"""
		
		...
	
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
		
		...
	
	def set_headless_mode(self, headless_mode: bool):
		"""
		Sets headless mode.

		Enables or disables headless browsing. In headless mode, the browser runs in the background without a visible UI.
		This is often used for automated testing and scraping to save resources and improve performance.

		Args:
			headless_mode (bool): Whether to start the browser in headless mode. True for headless, False for visible browser UI.
		"""
		
		...
	
	def set_implicitly_wait_timeout(self, timeout: float):
		"""
		Sets the implicit wait timeout for WebDriver element searches.

		Configures the implicit wait time, which is the maximum time WebDriver will wait
		when searching for elements before throwing a `NoSuchElementException`. This setting
		applies globally to all element searches for the duration of the WebDriver session.

		Args:
			timeout (float): The implicit wait timeout value in seconds.
		"""
		
		...
	
	def set_mute_audio(self, mute_audio: bool):
		"""
		Sets mute audio mode.

		Configures the browser to mute or unmute audio output. Muting audio can be useful in automated testing
		environments to prevent sound from interfering with tests or to conserve system resources.

		Args:
			mute_audio (bool): Whether to mute audio in the browser. True to mute, False to unmute.
		"""
		
		...
	
	def set_page_load_timeout(self, timeout: float):
		"""
		Sets the page load timeout for WebDriver operations.

		Defines the maximum time WebDriver will wait for a page to fully load before timing out
		and throwing a `TimeoutException`. This is useful to prevent tests from hanging indefinitely
		on slow-loading pages.

		Args:
			timeout (float): The page load timeout value in seconds.
		"""
		
		...
	
	def set_profile_dir(self, profile_dir: Optional[str]):
		"""
		Sets the profile directory.

		Specifies a custom browser profile directory to be used by the browser instance. Browser profiles store user-specific
		data such as bookmarks, history, cookies, and extensions. Using profiles allows for persistent browser settings
		across sessions and can be useful for testing with specific browser states.

		Args:
			profile_dir (Optional[str]): Path to the browser profile directory. If None, a default or temporary profile is used.
		"""
		
		...
	
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
		
		...
	
	def set_start_page_url(self, start_page_url: str):
		"""
		Sets the URL that the WebDriver will navigate to upon starting.

		Updates an internal configuration attribute (`_webdriver_start_args.start_page_url`)
		which is presumably used during WebDriver initialization.

		Args:
			start_page_url (str): The absolute URL for the browser to load initially.
		"""
		
		...
	
	def set_user_agent(self, user_agent: Optional[str]):
		"""
		Sets the user agent.

		Configures the browser to use a specific user agent string. Overriding the default user agent
		can be useful for testing website behavior under different browser or device conditions, or for privacy purposes.

		Args:
			user_agent (Optional[str]): User agent string to use. If None, the user agent setting is removed, reverting to the browser's default.
		"""
		
		...
	
	def switch_to_window(self, window: Optional[Union[str, int]] = None):
		"""
		Switches the driver's focus to the specified browser window.

		Uses get_window_handle to resolve the target window identifier (handle string or index)
		before instructing the driver to switch. If no window identifier is provided,
		it effectively switches to the current window.

		Args:
			window (Optional[Union[str, int]]): The identifier of the window to switch to.
				Can be a window handle (string) or an index (int) in the list of window handles.
				If None, targets the current window handle.
		"""
		
		...
	
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
		
		...
	
	@property
	def windows_handles(self) -> list[str]:
		"""
		Gets the handles of all open windows.

		Returns a list of handles for all browser windows or tabs currently open and managed by the WebDriver.
		This is useful for iterating through or managing multiple windows in a browser session.

		Returns:
		   list[str]: A list of window handles. Each handle is a string identifier for an open window.
		"""
		
		...
