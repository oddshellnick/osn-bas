import re
import sys
import pathlib
from subprocess import PIPE, Popen
from typing import Optional, Union
from osn_bas.webdrivers.types import JS_Scripts
from osn_windows_cmd.netstat import get_netstat_connections_data


def read_js_scripts() -> JS_Scripts:
	"""
	Reads JavaScript scripts from files and returns them in a JS_Scripts object.

	This function locates all `.js` files within the 'js_scripts' directory, which is expected to be located two levels above the current file's directory.
	It reads the content of each JavaScript file, using UTF-8 encoding, and stores these scripts in a dictionary-like `JS_Scripts` object.
	The filenames (without the `.js` extension) are used as keys in the `JS_Scripts` object to access the script content.

	Returns:
		JS_Scripts: An object of type JS_Scripts, containing the content of each JavaScript file as attributes.
	"""
	scripts = {}
	
	for script_file in (pathlib.Path(__file__).parent / "js_scripts").iterdir():
		scripts[re.sub(r"\.js$", "", script_file.name)] = open(script_file, "r", encoding="utf-8").read()
	
	return JS_Scripts(
			get_element_css=scripts["get_element_css"],
			open_new_tab=scripts["open_new_tab"],
			stop_window_loading=scripts["stop_window_loading"],
	)


def find_browser_previous_session(
		browser_exe: Union[str, pathlib.Path],
		profile_dir_command: str,
		profile_dir: Optional[str]
) -> Optional[int]:
	"""
	Finds the port number of a previously opened browser session, if it exists.

	This function checks for an existing browser session by examining network connections.
	It searches for listening connections associated with the given browser executable and profile directory.

	Args:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.
		profile_dir_command (str): Command line pattern to find the profile directory argument in the process command line. Should use `{value}` as a placeholder for the directory path.
		profile_dir (Optional[str]): The expected profile directory path to match against.

	Returns:
		Optional[int]: The port number of the previous session if found and matched, otherwise None.
	"""
	previous_session = get_netstat_connections_data(
			show_all_ports=True,
			show_connections_exe=True,
			show_connection_pid=True
	)
	
	found_ports = previous_session.loc[
		(
				previous_session["Executable"] == (browser_exe if isinstance(browser_exe, str) else browser_exe.name)
		) & previous_session["Local Address"].str.contains(r"127\.0\.0\.1:\d+", regex=True, na=False) & (previous_session["State"] == "LISTENING")
	]
	
	for index, row in found_ports.iterrows():
		stdout = Popen(
				f"wmic process where processid={int(row['PID'])} get CommandLine /FORMAT:LIST",
				stdout=PIPE,
				shell=True
		).communicate()[0].decode("866", errors="ignore").strip()
		found_command_line = re.sub(r"^CommandLine=", "", stdout).strip()
	
		found_profile_dir = re.search(profile_dir_command.format(value="(.*?)"), found_command_line)
		if found_profile_dir is not None:
			found_profile_dir = found_profile_dir.group(1)
	
		if found_profile_dir == profile_dir:
			return int(re.search(r"127\.0\.0\.1:(\d+)", row["Local Address"]).group(1))
	
	return None


def build_first_start_argument(browser_exe: Union[str, pathlib.Path]) -> str:
	"""
	Builds the first command line argument to start a browser executable.

	This function constructs the initial command line argument needed to execute a browser,
	handling different operating systems and executable path formats.

	Args:
		browser_exe (Union[str, pathlib.Path]): Path to the browser executable or just the executable name.

	Returns:
		str: The constructed command line argument string.

	Raises:
		OSError: If the platform is not supported.
		TypeError: If `browser_exe` is not of type str or pathlib.Path.
	"""
	if isinstance(browser_exe, str):
		return browser_exe
	elif isinstance(browser_exe, pathlib.Path):
		if sys.platform == "win32":
			return f"cd /d {str(browser_exe.parent.resolve())} && {browser_exe.name}"
		elif sys.platform in ["linux", "darwin"]:
			return f"cd '{str(browser_exe.parent.resolve())}' && './{browser_exe.name}'"
		else:
			raise OSError(f"Unsupported platform: {sys.platform}.")
	else:
		raise TypeError(f"browser_exe must be str or pathlib.Path, not {type(browser_exe)}.")
