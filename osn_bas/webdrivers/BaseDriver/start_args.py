import pathlib
from typing import Optional, Union
from osn_bas.webdrivers._functions import (
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
		start_page_url (str): URL to open when the browser starts.
		debugging_port (Optional[int]): Current debugging port number, can be None if not set.
		profile_dir (Optional[str]): Current profile directory path, can be None if not set.
		headless_mode (bool): Current headless mode status.
		mute_audio (bool): Current mute audio status.
		user_agent (Optional[str]): Current user agent string, can be None if not set.
		proxy_server (Optional[str]): Current proxy server address, can be None if not set.
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
		"""
		
		self._browser_exe = browser_exe
		self._debugging_port_command_line = debugging_port_command_line
		self._profile_dir_command_line = profile_dir_command_line
		self._headless_mode_command_line = headless_mode_command_line
		self._mute_audio_command_line = mute_audio_command_line
		self._user_agent_command_line = user_agent_command_line
		self._proxy_server_command_line = proxy_server_command_line
		self.debugging_port: Optional[int] = None
		self.profile_dir: Optional[str] = None
		self.headless_mode = False
		self.mute_audio = False
		self.user_agent: Optional[str] = None
		self.proxy_server: Optional[str] = None
		self.start_page_url = ""
	
	@property
	def browser_exe(self) -> Union[str, pathlib.Path]:
		"""
		Returns the browser executable path.

		This property retrieves the path to the browser executable that will be used to start the browser instance.

		Returns:
			Union[str, pathlib.Path]: The path to the browser executable.
		"""
		
		return self._browser_exe
	
	def clear_command(self) -> None:
		"""
		Resets all optional arguments for the browser start command.

		This method clears the debugging port, profile directory,
		headless mode, mute audio, user agent, and proxy server settings,
		effectively reverting to a basic browser start command with only the executable path.
		"""
		
		self.debugging_port = None
		self.profile_dir = None
		self.headless_mode = False
		self.mute_audio = False
		self.user_agent = None
		self.proxy_server = None
	
	@property
	def debugging_port_command_line(self) -> str:
		"""
		Returns the command-line format string for setting the debugging port.

		This property provides access to the format string used to include the debugging port
		argument when constructing the browser start command.

		Returns:
			str: The command-line format string for the debugging port.
		"""
		
		return self._debugging_port_command_line
	
	@property
	def headless_mode_command_line(self) -> str:
		"""
		Returns the command-line argument to enable headless mode.

		This property provides access to the command-line argument used to enable
		headless mode when starting the browser.

		Returns:
			str: The command-line argument for headless mode.
		"""
		
		return self._headless_mode_command_line
	
	@property
	def mute_audio_command_line(self) -> str:
		"""
		Returns the command-line argument to mute audio.

		This property provides access to the command-line argument used to mute audio
		when starting the browser.

		Returns:
			str: The command-line argument for muting audio.
		"""
		
		return self._mute_audio_command_line
	
	@property
	def profile_dir_command_line(self) -> str:
		"""
		Returns the command-line format string for setting the profile directory.

		This property provides access to the format string used to include the profile directory
		argument when constructing the browser start command.

		Returns:
			str: The command-line format string for the profile directory.
		"""
		
		return self._profile_dir_command_line
	
	@property
	def proxy_server_command_line(self) -> str:
		"""
		Returns the command-line format string for setting the proxy server.

		This property provides access to the format string used to include the proxy server
		argument when constructing the browser start command.

		Returns:
			str: The command-line format string for the proxy server.
		"""
		
		return self._proxy_server_command_line
	
	@property
	def start_command(self) -> str:
		"""
		Generates the full browser start command.

		Composes the command line arguments based on the current settings
		(debugging port, profile directory, headless mode, etc.) and the browser executable path.

		Returns:
			str: The complete command string to start the browser with specified arguments.
		"""
		
		start_args = [build_first_start_argument(self._browser_exe)]
		
		if self.debugging_port is not None:
			start_args.append(self._debugging_port_command_line.format(value=self.debugging_port))
		
		if self.profile_dir is not None:
			start_args.append(self._profile_dir_command_line.format(value=self.profile_dir))
		
		if self.headless_mode:
			start_args.append(self._headless_mode_command_line)
		
		if self.mute_audio:
			start_args.append(self._mute_audio_command_line)
		
		if self.user_agent is not None:
			start_args.append(self._user_agent_command_line.format(value=self.user_agent))
		
		if self.proxy_server is not None:
			start_args.append(self._proxy_server_command_line.format(value=self.proxy_server))
		
		if self.start_page_url:
			start_args.append(self.start_page_url)
		
		return " ".join(start_args)
	
	@property
	def user_agent_command_line(self) -> str:
		"""
		Returns the command-line format string for setting the user agent.

		This property provides access to the format string used to include the user agent
		argument when constructing the browser start command.

		Returns:
			str: The command-line format string for the user agent.
		"""
		
		return self._user_agent_command_line
