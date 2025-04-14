from typing import Literal, TypedDict


class WebdriverOption(TypedDict):
	"""
	Type definition for WebDriver option configuration.

	This TypedDict defines the structure for configuring WebDriver options,
	allowing to specify the name, command, and type of option to be set for a browser instance.

	Attributes:
	   name (str): The name of the option, used as an identifier within the options manager.
	   command (str): The actual command or option string that WebDriver understands.
	   type (Literal["normal", "experimental", "attribute", None]): Specifies the type of WebDriver option.
			Can be "normal" for standard arguments, "experimental" for experimental options,
			"attribute" for setting browser attributes directly, or None if the option type is not applicable.
	"""
	
	name: str
	command: str
	type: Literal["normal", "experimental", "attribute", None]


class JS_Scripts(TypedDict):
	"""
	Type definition for a collection of JavaScript script snippets.

	This TypedDict defines the structure for storing a collection of JavaScript snippets as strings.
	It is used to organize and access various JavaScript functionalities intended to be executed
	within a browser context, typically via Selenium WebDriver's `execute_script` method.

	Attributes:
		check_element_in_viewport (str): JavaScript code to check if an element is fully within the current browser viewport. Expects the element as arguments[0].
		get_document_scroll_size (str): JavaScript code to retrieve the total scrollable width and height of the document.
		get_element_css (str): JavaScript code to retrieve all computed CSS style properties of a DOM element. Expects the element as arguments[0].
		get_element_rect_in_viewport (str): JavaScript code to get the bounding rectangle (position and dimensions) of an element relative to the viewport. Expects the element as arguments[0].
		get_random_element_point_in_viewport (str): JavaScript code to calculate a random point (x, y coordinates) within the visible portion of a given element in the viewport. Expects the element as arguments[0].
		get_viewport_position (str): JavaScript code to get the current scroll position (X and Y offsets) of the viewport.
		get_viewport_rect (str): JavaScript code to get the viewport's position (scroll offsets) and dimensions (width, height).
		get_viewport_size (str): JavaScript code to get the current dimensions (width and height) of the viewport.
		stop_window_loading (str): JavaScript code to stop the current window's page loading process (`window.stop()`).
		open_new_tab (str): JavaScript code to open a new browser tab/window using `window.open()`. Expects an optional URL as arguments[0].
	"""
	
	check_element_in_viewport: str
	get_document_scroll_size: str
	get_element_css: str
	get_element_rect_in_viewport: str
	get_random_element_point_in_viewport: str
	get_viewport_position: str
	get_viewport_rect: str
	get_viewport_size: str
	stop_window_loading: str
	open_new_tab: str
