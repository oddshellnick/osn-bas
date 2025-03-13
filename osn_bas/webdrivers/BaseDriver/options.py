from random import choice
from selenium import webdriver
from typing import Any, Optional, Union
from osn_bas.webdrivers.types import WebdriverOption


class BrowserOptionsManager:
	"""
	Manages browser options for WebDriver.

	This class is responsible for handling and setting browser options for Selenium WebDriver instances.
	It provides methods to add, remove, and modify browser arguments and experimental options.

	Attributes:
	   options (Union[webdriver.ChromeOptions, webdriver.EdgeOptions, webdriver.FirefoxOptions]): The WebDriver options object, specific to the browser type (e.g., ChromeOptions, FirefoxOptions). Initialized by `renew_webdriver_options`.
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
		self.options: Union[
			webdriver.ChromeOptions,
			webdriver.EdgeOptions,
			webdriver.FirefoxOptions
		] = self.renew_webdriver_options()
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
