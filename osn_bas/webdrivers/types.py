from typing import Literal, TypedDict


class WebdriverOption(TypedDict):
    """
    Represents a webdriver option configuration.

    This TypedDict defines the structure for specifying options that can be passed to a webdriver instance.
    It includes the option's name, the command-line command to set it, and its type.

    Attributes:
        name (str): The name of the webdriver option. This is a human-readable identifier for the option.
        command (str): The command-line command or argument used to set this option in the webdriver.
        type (Literal["normal", "experimental", None]): The type of the webdriver option, indicating its stability or purpose.
    """
    name: str
    command: str
    type: Literal["normal", "experimental", None]


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
