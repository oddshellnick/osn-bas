import pathlib
from random import choice
from typing import Optional, Union
from osn_bas.webdrivers.functions import build_first_start_argument


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
		self.debugging_port: Optional[int] = None
		self.profile_dir: Optional[str] = None
		self.headless_mode: Optional[bool] = None
		self.mute_audio: Optional[bool] = None
		self.user_agent: Optional[str] = None
		self.proxy_server: Optional[str] = None
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
	
	def set_debugging_port(self, debugging_port: Optional[int]):
		"""
		Sets the debugging port argument and updates the start command.

		Args:
			debugging_port (Optional[int]): Debugging port number to set. If None, removes debugging port argument.
		"""
		self.debugging_port = debugging_port
		
		self.update_command()
	
	def set_headless_mode(self, headless_mode: Optional[bool]):
		"""
		Sets the headless mode argument and updates the start command.

		Args:
			headless_mode (Optional[bool]): Boolean value to enable or disable headless mode.
		"""
		self.headless_mode = headless_mode
		
		self.update_command()
	
	def set_mute_audio(self, mute_audio: Optional[bool]):
		"""
		Sets the mute audio argument and updates the start command.

		Args:
			mute_audio (Optional[bool]): Boolean value to enable or disable mute audio.
		"""
		self.mute_audio = mute_audio
		
		self.update_command()
	
	def set_profile_dir(self, profile_dir: Optional[str]):
		"""
		Sets the profile directory argument and updates the start command.

		Args:
			profile_dir (Optional[str]): Profile directory path to set. If None, removes profile directory argument.
		"""
		self.profile_dir = profile_dir
		
		self.update_command()
	
	def set_proxy_server(self, proxy_server: Optional[Union[str, list[str]]]):
		"""
		Sets the proxy server argument and updates the start command.

		Args:
			proxy_server (Optional[Union[str, list[str]]]): Proxy server string to set. If None, removes proxy server argument. Can be a single proxy string or list of proxy strings, in which case a random proxy will be chosen.
		"""
		if isinstance(proxy_server, list):
			proxy_server = choice(proxy_server)
		
		self.proxy_server = proxy_server
		
		self.update_command()
	
	def set_user_agent(self, user_agent: Optional[str]):
		"""
		Sets the user agent argument and updates the start command.

		Args:
			user_agent (Optional[str]): User agent string to set. If None, removes user agent argument.
		"""
		self.user_agent = user_agent
		
		self.update_command()
