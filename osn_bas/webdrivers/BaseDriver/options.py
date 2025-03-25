from random import choice
from selenium import webdriver
from typing import Any, Optional, Union
from osn_bas.webdrivers.types import WebdriverOption


class BrowserOptionsManager:
	"""
	Manages browser options for Selenium WebDriver.

	This class provides an abstract interface for managing browser options,
	allowing for setting and removing various options such as experimental options,
	arguments, and attributes. It is designed to be inherited by browser-specific
	option managers (e.g., ChromeOptionsManager, FirefoxOptionsManager).

	Attributes:
		_options (Union[webdriver.ChromeOptions, webdriver.EdgeOptions, webdriver.FirefoxOptions]):
			WebDriver options object, specific to the browser type.
		_debugging_port_command (WebdriverOption):
			Configuration for the debugging port option.
		_user_agent_command (WebdriverOption):
			Configuration for the user agent option.
		_proxy_command (WebdriverOption):
			Configuration for the proxy option.
		_enable_bidi_command (WebdriverOption):
			Configuration for the enable BiDi option.
	"""
	
	def __init__(
			self,
			debugging_port_command: WebdriverOption,
			user_agent_command: WebdriverOption,
			proxy_command: WebdriverOption,
			enable_bidi_command: WebdriverOption,
	):
		"""
		Initializes the BrowserOptionsManager with WebDriver option configurations.

		Args:
			debugging_port_command (WebdriverOption): Configuration for the debugging port option.
			user_agent_command (WebdriverOption): Configuration for the user agent option.
			proxy_command (WebdriverOption): Configuration for the proxy option.
			enable_bidi_command (WebdriverOption): Configuration for the enable BiDi option.
		"""
		
		self._options: Union[
			webdriver.ChromeOptions,
			webdriver.EdgeOptions,
			webdriver.FirefoxOptions
		] = self.renew_webdriver_options()
		self._debugging_port_command = debugging_port_command
		self._user_agent_command = user_agent_command
		self._proxy_command = proxy_command
		self._enable_bidi_command = enable_bidi_command
	
	def renew_webdriver_options(self) -> Any:
		"""
		Abstract method to renew WebDriver options. Must be implemented in child classes.

		This method is intended to be overridden in subclasses to provide
		browser-specific WebDriver options instances (e.g., ChromeOptions, FirefoxOptions).

		Returns:
			Any: A new instance of WebDriver options (e.g., ChromeOptions, FirefoxOptions).

		Raises:
			NotImplementedError: If the method is not implemented in a subclass.
		"""
		
		raise NotImplementedError("This function must be implemented in child classes.")
	
	def hide_automation(self, hide: bool):
		"""
		Abstract method to hide browser automation. Must be implemented in child classes.

		This method is intended to be overridden in subclasses to implement
		browser-specific techniques for hiding browser automation features,
		making the browser appear more like a normal user agent.

		Args:
			hide (bool): Whether to enable or disable hiding automation features.

		Raises:
			NotImplementedError: If the method is not implemented in a subclass.
		"""
		
		raise NotImplementedError("This function must be implemented in child classes.")
	
	def remove_attribute(self, attribute_name: str):
		"""
		Removes a browser attribute by its attribute name.

		Browser attributes are properties of the WebDriver options object that
		control certain aspects of the browser session. This method removes a previously set attribute.

		Args:
			attribute_name (str): Attribute name of the attribute to remove.
		"""
		
		if hasattr(self, attribute_name):
			argument = getattr(self, attribute_name)
		
			if hasattr(self._options, argument):
				delattr(self, attribute_name)
				delattr(self._options, argument)
	
	def remove_experimental_option(self, experimental_option_name: str):
		"""
		Removes an experimental browser option by its attribute name.

		Experimental options are specific features or behaviors that are not
		part of the standard WebDriver API and may be browser-specific or unstable.
		This method allows for removing such options that were previously set.

		Args:
			experimental_option_name (str): Attribute name of the experimental option to remove.
		"""
		
		if hasattr(self, experimental_option_name):
			experimental_option = getattr(self, experimental_option_name)
		
			if experimental_option[0] in self._options.experimental_options:
				self._options.experimental_options.pop(experimental_option[0])
				delattr(self, experimental_option_name)
	
	def remove_argument(self, argument_name: str):
		"""
		Removes a browser argument by its attribute name.

		Browser arguments are command-line flags that can modify the browser's behavior
		at startup. This method removes an argument that was previously added to the browser options.

		Args:
			argument_name (str): Attribute name of the argument to remove.
		"""
		
		if hasattr(self, argument_name):
			argument = getattr(self, argument_name)
		
			if argument in self._options.arguments:
				self._options.arguments.remove(argument)
				delattr(self, argument_name)
	
	def remove_option(self, option: WebdriverOption):
		"""
		Removes a browser option by its configuration object.

		This method removes a browser option, whether it's a normal argument,
		an experimental option, or an attribute, based on the provided `WebdriverOption` configuration.
		It determines the option type and calls the appropriate removal method.

		Args:
			option (WebdriverOption): The configuration object defining the option to be removed.

		Raises:
			ValueError: If the option type is not recognized.
		"""
		
		if option["type"] == "normal":
			self.remove_argument(option["name"])
		elif option["type"] == "experimental":
			self.remove_experimental_option(option["name"])
		elif option["type"] == "attribute":
			self.remove_attribute(option["name"])
		elif option["type"] is None:
			pass
		else:
			raise ValueError(f"Unknown option type ({option}).")
	
	def set_attribute(self, attribute_name: str, attribute: str, value: Optional[Any] = None):
		"""
		Sets a browser attribute.

		Browser attributes are properties of the WebDriver options object that
		can be set to configure the browser session. This method sets or updates a browser attribute.

		Args:
			attribute_name (str): Name to store the attribute under (attribute name in the class).
			attribute (str): Attribute name to set on the options object.
			value (Optional[Any]): Value to set for the attribute. Defaults to None.
		"""
		
		self.remove_attribute(attribute_name)
		
		setattr(self._options, attribute, value)
		setattr(self, attribute_name, attribute)
	
	def set_experimental_option(
			self,
			experimental_option_name: str,
			experimental_option: str,
			value: Any
	):
		"""
		Sets an experimental browser option.

		Experimental options allow for enabling or modifying browser features that
		are not part of the standard WebDriver API. This method adds or updates an experimental option.

		Args:
			experimental_option_name (str): Name to store the experimental option under (attribute name in the class).
			experimental_option (str): Experimental option name.
			value (Any): Value for the experimental option.
		"""
		
		self.remove_experimental_option(experimental_option_name)
		
		self._options.add_experimental_option(experimental_option, value)
		setattr(self, experimental_option_name, (experimental_option, value))
	
	def set_argument(self, argument_name: str, argument: str, value: Optional[str] = None):
		"""
		Sets a browser argument.

		Browser arguments are command-line flags that can be passed to the browser
		when it starts. This method adds or updates a browser argument.

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
		
		self._options.add_argument(argument_line)
		setattr(self, argument_name, argument_line)
	
	def set_option(self, option: WebdriverOption, value: Any):
		"""
		Sets a browser option based on its configuration object.

		This method configures a browser option, handling normal arguments,
		experimental options, and attributes as defined in the provided `WebdriverOption`.
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
		elif option["type"] == "attribute":
			self.set_attribute(option["name"], option["command"], value)
		elif option["type"] is None:
			pass
		else:
			raise ValueError(f"Unknown option type ({option}).")
	
	def set_debugger_address(self, debugging_port: Optional[int]):
		"""
		Sets the debugger address experimental option.

		This option allows attaching a debugger to a running browser instance,
		typically used for inspecting or controlling the browser externally.

		Args:
			debugging_port (Optional[int]): Debugging port number. If None, removes the debugger-address option. Defaults to None.
		"""
		
		if debugging_port is not None:
			self.set_option(self._debugging_port_command, f"127.0.0.1:{debugging_port}")
		else:
			self.remove_option(self._debugging_port_command)
	
	def set_enable_bidi(self, enable_bidi: bool):
		"""
		Sets the enable BiDi option.

		BiDi (Bidirectional) is a protocol that allows for more advanced communication
		between the WebDriver client and the browser, enabling features like network interception and CDP access.

		Args:
			enable_bidi (bool): Whether to enable BiDi protocol support.
		"""
		
		if enable_bidi is not None:
			self.set_option(self._enable_bidi_command, enable_bidi)
	
	def set_proxy(self, proxy: Optional[Union[str, list[str]]] = None):
		"""
		Sets the proxy browser option.

		Configures the browser to use a proxy server for network requests.
		This can be a single proxy or a list from which a random proxy will be selected.

		Args:
			proxy (Optional[Union[str, list[str]]]): Proxy string or list of proxy strings. If a list, a random proxy is chosen. If None, removes the proxy argument. Defaults to None.
		"""
		
		if proxy is not None:
			if isinstance(proxy, list):
				proxy = choice(proxy)
		
			self.set_option(self._proxy_command, proxy)
		else:
			self.remove_option(self._proxy_command)
	
	def set_user_agent(self, user_agent: Optional[str] = None):
		"""
		Sets the user agent browser option.

		Overrides the browser's default user agent string, which identifies the browser
		to websites. Setting a custom user agent can be useful for testing or compatibility purposes.

		Args:
			user_agent (Optional[str]): User agent string to set. If None, removes the user-agent argument. Defaults to None.
		"""
		
		if user_agent is not None:
			self.set_option(self._user_agent_command, user_agent)
		else:
			self.remove_option(self._user_agent_command)
