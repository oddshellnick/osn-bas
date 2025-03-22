import pathlib
from random import choice
from typing import Optional, Union
from osn_bas.webdrivers.functions import (
	build_first_start_argument
)


class BrowserStartArgs:
	"""
	Manages browser start arguments for WebDriver.

	This class is responsible for constructing and managing the command-line arguments
	used to start a browser instance with specific configurations for Selenium WebDriver.
	It allows setting various options such as debugging port, profile directory,
	headless mode, mute audio, user agent, and proxy server.

	Attributes:
		_browser_exe (Union[str, pathlib.Path]): Path to the browser executable.
		_debugging_port_command_line (str): Command-line format string for setting the debugging port.
		_profile_dir_command_line (str): Command-line format string for setting the profile directory.
		_headless_mode_command_line (str): Command-line argument to enable headless mode.
		_mute_audio_command_line (str): Command-line argument to mute audio.
		_user_agent_command_line (str): Command-line format string for setting the user agent.
		_proxy_server_command_line (str): Command-line format string for setting the proxy server.
		_start_page_url (str): URL to open when the browser starts.
		_debugging_port (Optional[int]): Current debugging port number, can be None if not set.
		_profile_dir (Optional[str]): Current profile directory path, can be None if not set.
		_headless_mode (Optional[bool]): Current headless mode status, can be None if not set.
		_mute_audio (Optional[bool]): Current mute audio status, can be None if not set.
		_user_agent (Optional[str]): Current user agent string, can be None if not set.
		_proxy_server (Optional[str]): Current proxy server address, can be None if not set.
		_start_command (str): The full command string to start the browser with all specified arguments.
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
			start_page_url: str,
	):
		"""
		Initializes BrowserStartArgs with command-line templates and browser executable path.

		This method sets up the BrowserStartArgs instance by storing the browser executable path,
		command-line format strings for various browser options, and the initial start page URL.
		It also initializes attributes to hold the current values for these options and builds the initial start command.

		Args:
			browser_exe (Union[str, pathlib.Path]): Path to the browser executable.
			debugging_port_command_line (str): Command-line format string for debugging port.
			profile_dir_command_line (str): Command-line format string for profile directory.
			headless_mode_command_line (str): Command-line argument for headless mode.
			mute_audio_command_line (str): Command-line argument for mute audio.
			user_agent_command_line (str): Command-line format string for user agent.
			proxy_server_command_line (str): Command-line format string for proxy server.
			start_page_url (str): URL to open on browser start.
		"""
		
		self._browser_exe = browser_exe
		self._debugging_port_command_line = debugging_port_command_line
		self._profile_dir_command_line = profile_dir_command_line
		self._headless_mode_command_line = headless_mode_command_line
		self._mute_audio_command_line = mute_audio_command_line
		self._user_agent_command_line = user_agent_command_line
		self._proxy_server_command_line = proxy_server_command_line
		self._start_page_url = start_page_url
		self._debugging_port: Optional[int] = None
		self._profile_dir: Optional[str] = None
		self._headless_mode: Optional[bool] = None
		self._mute_audio: Optional[bool] = None
		self._user_agent: Optional[str] = None
		self._proxy_server: Optional[str] = None
		self._start_command = build_first_start_argument(self._browser_exe)
		
		self.update_command()
	
	@property
	def browser_exe(self) -> Union[str, pathlib.Path]:
		"""
		Gets the browser executable path.

		Returns:
			Union[str, pathlib.Path]: The path to the browser executable.
		"""
		
		return self._browser_exe
	
	def update_command(self) -> str:
		"""
		Updates the start command string based on current settings.

		This method rebuilds the `start_command` attribute by concatenating the browser executable
		with the currently set optional arguments (debugging port, profile directory, etc.) and the start page URL.

		Returns:
			str: The updated start command string.
		"""
		
		start_args = [build_first_start_argument(self._browser_exe)]
		
		if self._debugging_port is not None:
			start_args.append(self._debugging_port_command_line.format(value=self._debugging_port))
		
		if self._profile_dir is not None:
			start_args.append(self._profile_dir_command_line.format(value=self._profile_dir))
		
		if self._headless_mode:
			start_args.append(self._headless_mode_command_line)
		
		if self._mute_audio is not None:
			start_args.append(self._mute_audio_command_line)
		
		if self._user_agent is not None:
			start_args.append(self._user_agent_command_line.format(value=self._user_agent))
		
		if self._proxy_server is not None:
			start_args.append(self._proxy_server_command_line.format(value=self._proxy_server))
		
		start_args.append(self._start_page_url)
		self._start_command = " ".join(start_args)
		
		return self._start_command
	
	def clear_command(self):
		"""
		Clears all optional arguments from the start command, resetting to the base executable.

		This method resets the start command to only include the browser executable path,
		effectively removing all configured optional arguments such as debugging port,
		profile directory, headless mode, etc.
		"""
		
		self._debugging_port = None
		self._profile_dir = None
		self._headless_mode = False
		self._mute_audio = False
		self._user_agent = None
		self._proxy_server = None
		
		self.update_command()
	
	@property
	def debugging_port(self) -> Optional[int]:
		"""
		Gets the debugging port number.

		Returns:
			Optional[int]: The debugging port number, or None if not set.
		"""
		
		return self._debugging_port
	
	@property
	def debugging_port_command_line(self) -> str:
		"""
		Gets the command-line format string for setting the debugging port.

		Returns:
			str: The command-line format string used to include the debugging port argument when starting the browser.
		"""
		
		return self._debugging_port_command_line
	
	@property
	def headless_mode(self) -> Optional[bool]:
		"""
		Gets the headless mode status.

		Returns:
			Optional[bool]: The headless mode status, or None if not set.
		"""
		
		return self._headless_mode
	
	@property
	def headless_mode_command_line(self) -> str:
		"""
		Gets the command-line argument to enable headless mode.

		Returns:
			str: The command-line argument used to enable headless mode when starting the browser.
		"""
		
		return self._headless_mode_command_line
	
	@property
	def mute_audio(self) -> Optional[bool]:
		"""
		Gets the mute audio status.

		Returns:
			Optional[bool]: The mute audio status, or None if not set.
		"""
		
		return self._mute_audio
	
	@property
	def mute_audio_command_line(self) -> str:
		"""
		Gets the command-line argument to mute audio.

		Returns:
			str: The command-line argument used to mute audio when starting the browser.
		"""
		
		return self._mute_audio_command_line
	
	@property
	def profile_dir(self) -> Optional[str]:
		"""
		Gets the profile directory path.

		Returns:
			Optional[str]: The profile directory path, or None if not set.
		"""
		
		return self._profile_dir
	
	@property
	def profile_dir_command_line(self) -> str:
		"""
		Gets the command-line format string for setting the profile directory.

		Returns:
			str: The command-line format string used to include the profile directory argument when starting the browser.
		"""
		
		return self._profile_dir_command_line
	
	@property
	def proxy_server(self) -> Optional[str]:
		"""
		Gets the proxy server address.

		Returns:
			Optional[str]: The proxy server address, or None if not set.
		"""
		
		return self._proxy_server
	
	@property
	def proxy_server_command_line(self) -> str:
		"""
		Gets the command-line format string for setting the proxy server.

		Returns:
			str: The command-line format string used to include the proxy server argument when starting the browser.
		"""
		
		return self._proxy_server_command_line
	
	def set_debugging_port(self, debugging_port: Optional[int]) -> str:
		"""
		Sets the debugging port argument and updates the start command.

		Configures the debugging port number to be used when starting the browser.
		This is useful for attaching debuggers or remote automation tools to the browser instance.

		Args:
			debugging_port (Optional[int]): Debugging port number to set. If None, removes debugging port argument.

		Returns:
			str: The updated start command string.
		"""
		
		self._debugging_port = debugging_port
		
		return self.update_command()
	
	def set_headless_mode(self, headless_mode: Optional[bool]) -> str:
		"""
		Sets the headless mode argument and updates the start command.

		Enables or disables headless browsing mode. In headless mode, the browser runs
		without a graphical user interface, which is often used for automated testing and scraping.

		Args:
			headless_mode (Optional[bool]): Boolean value to enable or disable headless mode.

		Returns:
			str: The updated start command string.
		"""
		
		self._headless_mode = headless_mode
		
		return self.update_command()
	
	def set_mute_audio(self, mute_audio: Optional[bool]) -> str:
		"""
		Sets the mute audio argument and updates the start command.

		Configures the browser to start with audio muted or unmuted. Muting audio can be
		useful in automated environments to prevent sound output.

		Args:
			mute_audio (Optional[bool]): Boolean value to enable or disable mute audio.

		Returns:
			str: The updated start command string.
		"""
		
		self._mute_audio = mute_audio
		
		return self.update_command()
	
	def set_profile_dir(self, profile_dir: Optional[str]) -> str:
		"""
		Sets the profile directory argument and updates the start command.

		Specifies a browser profile directory to use. Browser profiles store user-specific data
		like bookmarks, history, and cookies, allowing for persistent browser sessions.

		Args:
			profile_dir (Optional[str]): Profile directory path to set. If None, removes profile directory argument.

		Returns:
			str: The updated start command string.
		"""
		
		self._profile_dir = profile_dir
		
		return self.update_command()
	
	def set_proxy_server(self, proxy_server: Optional[Union[str, list[str]]]) -> str:
		"""
		Sets the proxy server argument and updates the start command.

		Configures the browser to use a proxy server for network connections. This can be a single
		proxy server or a list from which a random proxy will be selected. Proxies can be used for
		anonymity, accessing geo-restricted content, or for testing purposes.

		Args:
			proxy_server (Optional[Union[str, list[str]]]): Proxy server string to set. If None, removes proxy server argument. Can be a single proxy string or list of proxy strings, in which case a random proxy will be chosen.

		Returns:
			str: The updated start command string.
		"""
		
		if isinstance(proxy_server, list):
			proxy_server = choice(proxy_server)
		
		self._proxy_server = proxy_server
		
		return self.update_command()
	
	def set_user_agent(self, user_agent: Optional[str]) -> str:
		"""
		Sets the user agent argument and updates the start command.

		Overrides the browser's default user agent string. Setting a custom user agent can be
		useful for testing website behavior under different browsers or devices, or for masking
		the browser's identity.

		Args:
			user_agent (Optional[str]): User agent string to set. If None, removes user agent argument.

		Returns:
			str: The updated start command string.
		"""
		
		self._user_agent = user_agent
		
		return self.update_command()
	
	@property
	def start_command(self) -> str:
		"""
		Gets the full browser start command string.

		Returns:
			str: The full command string to start the browser.
		"""
		
		return self._start_command
	
	@property
	def user_agent(self) -> Optional[str]:
		"""
		Gets the user agent string.

		Returns:
			Optional[str]: The user agent string, or None if not set.
		"""
		
		return self._user_agent
	
	@property
	def user_agent_command_line(self) -> str:
		"""
		Gets the command-line format string for setting the user agent.

		Returns:
			str: The command-line format string used to include the user agent argument when starting the browser.
		"""
		
		return self._user_agent_command_line
