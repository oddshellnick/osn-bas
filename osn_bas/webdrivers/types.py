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
	Type definition for a collection of JavaScript scripts.

	This TypedDict defines the structure for storing a collection of JavaScript scripts as strings.
	It is used to organize and access various JavaScript functionalities intended to be executed within a browser context using Selenium WebDriver.

	Attributes:
	   get_element_css (str): JavaScript code as a string to retrieve the computed CSS style of a DOM element.
	   stop_window_loading (str): JavaScript code as a string to stop the current window's page loading process.
	   open_new_tab (str): JavaScript code as a string to open a new browser tab, optionally with a specified URL.
	"""
	
	get_element_css: str
	stop_window_loading: str
	open_new_tab: str
