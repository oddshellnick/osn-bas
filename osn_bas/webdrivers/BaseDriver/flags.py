import pathlib
from selenium import webdriver
from osn_bas.webdrivers._functions import (
	build_first_start_argument
)
from typing import (
	Any,
	Callable,
	Literal,
	Optional,
	TypedDict,
	Union
)
from osn_bas.webdrivers.types import (
	AutoplayPolicyType,
	LogLevelType,
	UseGLType
)


def _str_adding_validation_function(value: Optional[str]) -> bool:
	"""
	Validation function that checks if a value is a non-empty string.

	Args:
		value (Optional[str]): The value to validate.

	Returns:
		bool: `True` if the value is a non-empty string, `False` otherwise.
	"""
	
	if value is not None and not isinstance(value, str):
		return False
	
	return bool(value)


def _optional_bool_adding_validation_function(value: Optional[bool]) -> bool:
	"""
	Validation function that checks if a value is a boolean or None.

	The function returns `True` if the value is not None, allowing the flag
	to be added.

	Args:
		value (Optional[bool]): The value to validate.

	Returns:
		bool: `True` if the value is not None, `False` if the value is not a boolean.
	"""
	
	if value is not None and not isinstance(value, bool):
		return False
	
	return value is not None


def _path_adding_validation_function(value: Optional[Union[str, pathlib.Path]]) -> bool:
	"""
	Validation function that checks if a value is a non-empty string or a pathlib.Path object.

	Args:
		value (Optional[Union[str, pathlib.Path]]): The value to validate.

	Returns:
		bool: `True` if the value is a valid path-like object, `False` otherwise.
	"""
	
	if value is not None and not isinstance(value, (str, pathlib.Path)):
		return False
	
	return bool(value)


def _bool_adding_validation_function(value: Optional[bool]) -> bool:
	"""
	Validation function that checks if a value is a boolean and `True`.

	Args:
		value (Optional[bool]): The value to validate.

	Returns:
		bool: `True` if the value is `True`, `False` otherwise.
	"""
	
	if not isinstance(value, bool):
		return False
	
	return value


def _int_adding_validation_function(value: Optional[int]) -> bool:
	"""
	Validation function that checks if a value is an integer.

	Args:
		value (Optional[int]): The value to validate.

	Returns:
		bool: `True` if the value is an integer or None, `False` otherwise.
	"""
	
	if value is not None and not isinstance(value, int):
		return False
	
	return True


class FlagNotDefined:
	"""A sentinel class to indicate that a flag definition was not found."""
	
	pass


class FlagDefinition(TypedDict):
	name: str
	command: str
	type: Literal["argument", "experimental_option", "attribute", "blink_feature"]
	mode: Literal["webdriver_option", "startup_argument", "both"]
	adding_validation_function: Callable[[Any], bool]


class FlagType(TypedDict):
	set_flag_function: Callable[[FlagDefinition, Any], None]
	remove_flag_function: Callable[[str], None]
	set_flags_function: Callable[[dict[str, Any]], None]
	update_flags_function: Callable[[dict[str, Any]], None]
	clear_flags_function: Callable[[], None]
	build_options_function: Callable[["_any_webdriver_option_type"], "_any_webdriver_option_type"]
	build_start_args_function: Callable[[], list[str]]


class BrowserExperimentalOptions(TypedDict, total=False):
	pass


class BlinkExperimentalOptions(BrowserExperimentalOptions, total=False):
	debugger_address: Optional[str]


class BlinkFeatures(TypedDict, total=False):
	calculate_native_win_occlusion: Optional[bool]
	accept_ch_frame: Optional[bool]
	avoid_unload_check_sync: Optional[bool]
	bfcache_feature: Optional[bool]
	heavy_ad_mitigations: Optional[bool]
	isolate_origins: Optional[bool]
	lazy_frame_loading: Optional[bool]
	script_streaming: Optional[bool]
	global_media_controls: Optional[bool]
	improved_cookie_controls: Optional[bool]
	privacy_sandbox_settings4: Optional[bool]
	media_router: Optional[bool]
	autofill_server_comm: Optional[bool]
	cert_transparency_updater: Optional[bool]
	optimization_hints: Optional[bool]
	dial_media_route_provider: Optional[bool]
	paint_holding: Optional[bool]
	destroy_profile_on_browser_close: Optional[bool]
	site_per_process: Optional[bool]
	automation_controlled: Optional[bool]


class BrowserAttributes(TypedDict, total=False):
	enable_bidi: Optional[bool]


class BlinkAttributes(BrowserAttributes, total=False):
	pass


class BrowserArguments(TypedDict, total=False):
	pass


class BlinkArguments(BrowserArguments, total=False):
	headless_mode: bool
	mute_audio: bool
	no_first_run: bool
	disable_background_timer_throttling: bool
	disable_backgrounding_occluded_windows: bool
	disable_hang_monitor: bool
	disable_ipc_flooding_protection: bool
	disable_renderer_backgrounding: bool
	disable_back_forward_cache: bool
	disable_notifications: bool
	disable_popup_blocking: bool
	disable_prompt_on_repost: bool
	disable_sync: bool
	disable_background_networking: bool
	disable_breakpad: bool
	disable_component_update: bool
	disable_domain_reliability: bool
	disable_new_content_rendering_timeout: bool
	disable_threaded_animation: bool
	disable_threaded_scrolling: bool
	disable_checker_imaging: bool
	disable_image_animation_resync: bool
	disable_partial_raster: bool
	disable_skia_runtime_opts: bool
	disable_dev_shm_usage: bool
	disable_gpu: bool
	aggressive_cache_discard: bool
	allow_running_insecure_content: bool
	no_process_per_site: bool
	enable_precise_memory_info: bool
	use_fake_device_for_media_stream: bool
	use_fake_ui_for_media_stream: bool
	deny_permission_prompts: bool
	disable_external_intent_requests: bool
	noerrdialogs: bool
	enable_automation: bool
	test_type: bool
	remote_debugging_pipe: bool
	silent_debugger_extension_api: bool
	enable_logging_stderr: bool
	password_store_basic: bool
	use_mock_keychain: bool
	enable_crash_reporter_for_testing: bool
	metrics_recording_only: bool
	no_pings: bool
	allow_pre_commit_input: bool
	deterministic_mode: bool
	run_all_compositor_stages_before_draw: bool
	enable_begin_frame_control: bool
	in_process_gpu: bool
	block_new_web_contents: bool
	new_window: bool
	no_service_autorun: bool
	process_per_tab: bool
	single_process: bool
	no_sandbox: bool
	user_agent: Optional[str]
	user_data_dir: Optional[str]
	proxy_server: Optional[str]
	remote_debugging_port: Optional[int]
	remote_debugging_address: Optional[str]
	use_file_for_fake_video_capture: Optional[Union[str, pathlib.Path]]
	autoplay_policy: Optional[AutoplayPolicyType]
	log_level: Optional[LogLevelType]
	use_gl: Optional[UseGLType]
	force_color_profile: Optional[str]


class BlinkFlags(TypedDict, total=False):
	argument: BlinkArguments
	experimental_option: BlinkExperimentalOptions
	attribute: BlinkAttributes
	blink_feature: BlinkFeatures


class ExperimentalOptionValue(TypedDict):
	option_name: str
	value: Any


class AttributeValue(TypedDict):
	attribute_name: str
	value: Any


class ArgumentValue(TypedDict):
	command_line: str
	value: Any


class FlagTypeNotDefined:
	"""A sentinel class to indicate that a flag type definition was not found."""
	
	pass


def _argument_to_flag(argument: ArgumentValue) -> str:
	"""
	Formats a command-line argument from an ArgumentValue dictionary.

	If the command string contains '{value}', it will be replaced by the argument's value.
	Otherwise, the command string is returned as is.

	Args:
		argument (ArgumentValue): A dictionary containing the command-line string and its value.

	Returns:
		str: The formatted command-line argument string.
	"""
	
	argument_command = argument["command_line"]
	argument_value = argument["value"]
	
	if "{value}" in argument_command:
		return argument_command.format(value=argument_value)
	else:
		return argument_command


class BrowserFlags(TypedDict, total=False):
	argument: BrowserArguments
	experimental_option: BrowserExperimentalOptions
	attribute: BrowserAttributes


class BrowserFlagsManager:
	"""
	Manages browser flags, including arguments, experimental options, and attributes for a generic WebDriver.

	This class provides a structured way to define, set, and build browser options
	for various Selenium WebDriver instances.

	Attributes:
		_flags_types (dict[str, FlagType]): A dictionary mapping flag types to their handler functions.
		_flags_definitions (dict[str, FlagDefinition]): A dictionary of all available flag definitions.
		_flags_definitions_by_types (dict[str, dict[str, FlagDefinition]]): Flags definitions grouped by type.
		_arguments (dict[str, ArgumentValue]): Stores the configured command-line arguments.
		_experimental_options (dict[str, ExperimentalOptionValue]): Stores the configured experimental options.
		_attributes (dict[str, AttributeValue]): Stores the configured WebDriver attributes.
	"""
	
	def __init__(
			self,
			flags_types: Optional[dict[str, FlagType]] = None,
			flags_definitions: Optional[dict[str, FlagDefinition]] = None
	):
		"""
		Initializes the BrowserFlagsManager.

		Args:
			flags_types (Optional[dict[str, FlagType]]): Custom flag types and their corresponding functions.
			flags_definitions (Optional[dict[str, FlagDefinition]]): Custom flag definitions to add or override.
		"""
		
		inner_flags_types = {
			"argument": FlagType(
					set_flag_function=self.set_argument,
					remove_flag_function=self.remove_argument,
					set_flags_function=self.set_arguments,
					update_flags_function=self.update_arguments,
					clear_flags_function=self.clear_arguments,
					build_options_function=self.build_options_arguments,
					build_start_args_function=self.build_start_args_arguments
			),
			"experimental_option": FlagType(
					set_flag_function=self.set_experimental_option,
					remove_flag_function=self.remove_experimental_option,
					set_flags_function=self.set_experimental_options,
					update_flags_function=self.update_experimental_options,
					clear_flags_function=self.clear_experimental_options,
					build_options_function=self.build_options_experimental_options,
					build_start_args_function=lambda: []
			),
			"attribute": FlagType(
					set_flag_function=self.set_attribute,
					remove_flag_function=self.remove_attribute,
					set_flags_function=self.set_attributes,
					update_flags_function=self.update_attributes,
					clear_flags_function=self.clear_attributes,
					build_options_function=self.build_options_attributes,
					build_start_args_function=lambda: []
			),
		}
		
		if flags_types is not None:
			inner_flags_types.update(flags_types)
		
		inner_flags_definitions = {
			"enable_bidi": FlagDefinition(
					name="enable_bidi",
					command="enable_bidi",
					type="attribute",
					mode="webdriver_option",
					adding_validation_function=_optional_bool_adding_validation_function
			),
		}
		
		if flags_definitions is not None:
			inner_flags_definitions.update(flags_definitions)
		
		self._flags_types = inner_flags_types
		self._flags_definitions = inner_flags_definitions
		
		self._flags_definitions_by_types: dict[str, dict[str, FlagDefinition]] = {
			option_type: dict(
					filter(lambda di: di[1]["type"] == option_type, self._flags_definitions.items())
			)
			for option_type in self._flags_types.keys()
		}
		
		self._arguments: dict[str, ArgumentValue] = {}
		self._experimental_options: dict[str, ExperimentalOptionValue] = {}
		self._attributes: dict[str, AttributeValue] = {}
	
	def build_options_attributes(self, options: "_any_webdriver_option_type") -> "_any_webdriver_option_type":
		"""
		Applies configured attributes to the WebDriver options object.

		Only attributes with `mode` set to 'webdriver_option' or 'both' are applied.

		Args:
			options (_any_webdriver_option_type): The WebDriver options object to modify.

		Returns:
			_any_webdriver_option_type: The modified WebDriver options object.
		"""
		
		for name, value in self._attributes.items():
			if self._flags_definitions_by_types["attribute"][name]["mode"] in ["webdriver_option", "both"]:
				setattr(options, value["attribute_name"], value["value"])
		
		return options
	
	def clear_attributes(self):
		"""Clears all configured browser attributes."""
		
		self._attributes = {}
	
	def remove_attribute(self, attribute_name: str):
		"""
		Removes a browser attribute by its attribute name.

		Browser attributes are properties of the WebDriver options object that
		control certain aspects of the browser session. This method removes a previously set attribute.

		Args:
			attribute_name (str): Attribute name of the attribute to remove.
		"""
		
		self._attributes.pop(attribute_name, None)
	
	def set_attribute(self, attribute: FlagDefinition, value: Any):
		"""
		Sets a browser attribute. If the attribute already exists, it is overwritten.

		Args:
			attribute (FlagDefinition): The definition of the attribute to set.
			value (Any): The value to assign to the attribute.
		"""
		
		attribute_name = attribute["name"]
		attribute_command = attribute["command"]
		adding_validation_function = attribute["adding_validation_function"]
		
		self.remove_attribute(attribute_name)
		
		if adding_validation_function(value):
			self._attributes[attribute_name] = AttributeValue(attribute_name=attribute_command, value=value)
	
	def update_attributes(self, attributes: Union[BrowserAttributes, dict[str, Any]]):
		"""
		Updates browser attributes from a dictionary without clearing existing ones.

		Args:
			attributes (Union[BrowserAttributes, dict[str, Any]]): A dictionary of attributes to set or update.

		Raises:
			ValueError: If an unknown attribute key is provided.
		"""
		
		for key, value in attributes.items():
			flag_definition = self._flags_definitions_by_types["attribute"].get(key, FlagNotDefined())
		
			if isinstance(flag_definition, FlagNotDefined):
				raise ValueError(f"Unknown attribute: {key}.")
		
			self.set_attribute(flag_definition, value)
	
	def set_attributes(self, attributes: Union[BrowserAttributes, dict[str, Any]]):
		"""
		Clears existing and sets new browser attributes from a dictionary.

		Args:
			attributes (Union[BrowserAttributes, dict[str, Any]]): A dictionary of attributes to set.

		Raises:
			ValueError: If an unknown attribute key is provided.
		"""
		
		self.clear_attributes()
		self.update_attributes(attributes)
	
	def build_options_experimental_options(self, options: "_any_webdriver_option_type") -> "_any_webdriver_option_type":
		"""
		Adds configured experimental options to the WebDriver options object.

		Only options with `mode` set to 'webdriver_option' or 'both' are added.

		Args:
			options (_any_webdriver_option_type): The WebDriver options object to modify.

		Returns:
			_any_webdriver_option_type: The modified WebDriver options object.
		"""
		
		for name, value in self._experimental_options.items():
			if self._flags_definitions_by_types["experimental_option"][name]["mode"] in ["webdriver_option", "both"]:
				options.add_experimental_option(value["option_name"], value["value"])
		
		return options
	
	def clear_experimental_options(self):
		"""Clears all configured experimental options."""
		
		self._experimental_options = {}
	
	def remove_experimental_option(self, experimental_option_name: str):
		"""
		Removes an experimental browser option by its attribute name.

		Experimental options are specific features or behaviors that are not
		part of the standard WebDriver API and may be browser-specific or unstable.
		This method allows for removing such options that were previously set.

		Args:
			experimental_option_name (str): Attribute name of the experimental option to remove.
		"""
		
		self._experimental_options.pop(experimental_option_name, None)
	
	def set_experimental_option(self, experimental_option: FlagDefinition, value: Any):
		"""
		Sets an experimental browser option. If the option already exists, it is overwritten.

		Args:
			experimental_option (FlagDefinition): The definition of the experimental option to set.
			value (Any): The value to assign to the option.
		"""
		
		experimental_option_name = experimental_option["name"]
		experimental_option_command = experimental_option["command"]
		adding_validation_function = experimental_option["adding_validation_function"]
		
		self.remove_experimental_option(experimental_option_name)
		
		if adding_validation_function(value):
			self._experimental_options[experimental_option_name] = ExperimentalOptionValue(option_name=experimental_option_command, value=value)
	
	def update_experimental_options(
			self,
			experimental_options: Union[BrowserExperimentalOptions, dict[str, Any]]
	):
		"""
		Updates experimental options from a dictionary without clearing existing ones.

		Args:
			experimental_options (Union[BrowserExperimentalOptions, dict[str, Any]]): A dictionary of experimental options to set or update.

		Raises:
			ValueError: If an unknown experimental option key is provided.
		"""
		
		for key, value in experimental_options.items():
			flag_definition = self._flags_definitions_by_types["experimental_option"].get(key, FlagNotDefined())
		
			if isinstance(flag_definition, FlagNotDefined):
				raise ValueError(f"Unknown experimental option: {key}.")
		
			self.set_experimental_option(flag_definition, value)
	
	def set_experimental_options(
			self,
			experimental_options: Union[BrowserExperimentalOptions, dict[str, Any]]
	):
		"""
		Clears existing and sets new experimental options from a dictionary.

		Args:
			experimental_options (Union[BrowserExperimentalOptions, dict[str, Any]]): A dictionary of experimental options to set.

		Raises:
			ValueError: If an unknown experimental option key is provided.
		"""
		
		self.clear_experimental_options()
		self.update_experimental_options(experimental_options)
	
	def build_start_args_arguments(self) -> list[str]:
		"""
		Builds a list of command-line arguments intended for browser startup.

		Only arguments with `mode` set to 'startup_argument' or 'both' are included.

		Returns:
			list[str]: A list of formatted command-line argument strings.
		"""
		
		return [
			_argument_to_flag(value)
			for name, value in self._arguments.items()
			if self._flags_definitions_by_types["argument"][name]["mode"] in ["startup_argument", "both"]
		]
	
	def build_options_arguments(self, options: "_any_webdriver_option_type") -> "_any_webdriver_option_type":
		"""
		Adds configured command-line arguments to the WebDriver options object.

		Only arguments with `mode` set to 'webdriver_option' or 'both' are added.

		Args:
			options (_any_webdriver_option_type): The WebDriver options object to modify.

		Returns:
			_any_webdriver_option_type: The modified WebDriver options object.
		"""
		
		for name, value in self._arguments.items():
			if self._flags_definitions_by_types["argument"][name]["mode"] in ["webdriver_option", "both"]:
				options.add_argument(_argument_to_flag(value))
		
		return options
	
	def clear_arguments(self):
		"""Clears all configured browser arguments."""
		
		self._arguments = {}
	
	def remove_argument(self, argument_name: str):
		"""
		Removes a browser argument by its attribute name.

		Browser arguments are command-line flags that can modify the browser's behavior
		at startup. This method removes an argument that was previously added to the browser options.

		Args:
			argument_name (str): Attribute name of the argument to remove.
		"""
		
		self._arguments.pop(argument_name, None)
	
	def set_argument(self, argument: FlagDefinition, value: Any):
		"""
		Sets a command-line argument. If the argument already exists, it is overwritten.

		Args:
			argument (FlagDefinition): The definition of the argument to set.
			value (Any): The value for the argument. This may be a boolean for a simple flag or a string/number for a valued flag.
		"""
		
		argument_name = argument["name"]
		argument_command = argument["command"]
		adding_validation_function = argument["adding_validation_function"]
		
		self.remove_argument(argument_name)
		
		if adding_validation_function(value):
			self._arguments[argument_name] = ArgumentValue(command_line=argument_command, value=value)
	
	def update_arguments(self, arguments: Union[BrowserArguments, dict[str, Any]]):
		"""
		Updates command-line arguments from a dictionary without clearing existing ones.

		Args:
			arguments (Union[BrowserArguments, dict[str, Any]]): A dictionary of arguments to set or update.

		Raises:
			ValueError: If an unknown argument key is provided.
		"""
		
		for key, value in arguments.items():
			flag_definition = self._flags_definitions_by_types["argument"].get(key, FlagNotDefined())
		
			if isinstance(flag_definition, FlagNotDefined):
				raise ValueError(f"Unknown argument: {key}.")
		
			self.set_argument(flag_definition, value)
	
	def set_arguments(self, arguments: Union[BrowserArguments, dict[str, Any]]):
		"""
		Clears existing and sets new command-line arguments from a dictionary.

		Args:
			arguments (Union[BrowserArguments, dict[str, Any]]): A dictionary of arguments to set.

		Raises:
			ValueError: If an unknown argument key is provided.
		"""
		
		self.clear_arguments()
		self.update_arguments(arguments)
	
	def clear_flags(self):
		"""Clears all configured flags of all types (arguments, options, attributes)."""
		
		for type_name, type_functions in self._flags_types.items():
			type_functions["clear_flags_function"]()
	
	def _renew_webdriver_options(self) -> "_any_webdriver_option_type":
		"""
		Abstract method to renew WebDriver options. Must be implemented in child classes.

		This method is intended to be overridden in subclasses to provide
		browser-specific WebDriver options instances (e.g., ChromeOptions, FirefoxOptions).

		Returns:
			_any_webdriver_option_type: A new instance of WebDriver options (e.g., ChromeOptions, FirefoxOptions).

		Raises:
			NotImplementedError: If the method is not implemented in a subclass.
		"""
		
		raise NotImplementedError("This function must be implemented in child classes.")
	
	@property
	def options(self) -> "_any_webdriver_option_type":
		"""
		Builds and returns a WebDriver options object with all configured flags applied.

		Returns:
			_any_webdriver_option_type: A configured WebDriver options object.
		"""
		
		options = self._renew_webdriver_options()
		
		for type_name, type_functions in self._flags_types.items():
			options = type_functions["build_options_function"](options)
		
		return options
	
	def remove_option(self, option: FlagDefinition):
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
		
		for type_name, type_functions in self._flags_types.items():
			if option["type"] == type_name:
				type_functions["remove_flag_function"](option["name"])
		
		raise ValueError(f"Unknown option type ({option}).")
	
	def set_flags(self, flags: Union[BrowserFlags, dict[str, dict[str, Any]]]):
		"""
		Clears all existing flags and sets new ones from a comprehensive dictionary.

		This method iterates through the provided flag types (e.g., 'arguments', 'experimental_options')
		and calls the corresponding `set_*` function for each type, effectively replacing all
		previously configured flags for that type.

		Args:
			flags (Union[BrowserFlags, dict[str, dict[str, Any]]]): A dictionary where keys are flag types
				and values are dictionaries of flags to set for that type.

		Raises:
			ValueError: If an unknown flag type is provided in the `flags` dictionary.
		"""
		
		for type_name, type_flags in flags.items():
			flags_type_definition = self._flags_types.get(type_name, FlagTypeNotDefined())
		
			if isinstance(flags_type_definition, FlagTypeNotDefined):
				raise ValueError(f"Unknown flag type: {type_name}.")
		
			flags_type_definition["set_flags_function"](type_flags)
	
	def set_option(self, option: FlagDefinition, value: Any):
		"""
		Sets a browser option based on its configuration object.

		This method configures a browser option, handling normal arguments,
		experimental options, and attributes as defined in the provided `FlagDefinition`.
		It uses the option's type to determine the appropriate method for setting the option with the given value.

		Args:
			option (FlagDefinition): A dictionary-like object containing the configuration for the option to be set.
			value (Any): The value to be set for the option. The type and acceptable values depend on the specific browser option being configured.

		Raises:
			ValueError: If the option type is not recognized.
		"""
		
		for type_name, type_functions in self._flags_types.items():
			if option["type"] == type_name:
				type_functions["set_flag_function"](option, value)
		
		raise ValueError(
				f"Unknown option type ({option}). Acceptable types are: {', '.join(self._flags_types.keys())}."
		)
	
	def update_flags(self, flags: Union[BrowserFlags, dict[str, dict[str, Any]]]):
		"""
		Updates all flags from a comprehensive dictionary without clearing existing ones.

		This method iterates through the provided flag types (e.g., 'arguments', 'experimental_options')
		and calls the corresponding `update_*` function for each type, adding or overwriting
		flags without affecting other existing flags.

		Args:
			flags (Union[BrowserFlags, dict[str, dict[str, Any]]]): A dictionary where keys are flag types
				and values are dictionaries of flags to update for that type.

		Raises:
			ValueError: If an unknown flag type is provided in the `flags` dictionary.
		"""
		
		for type_name, type_flags in flags.items():
			flags_type_definition = self._flags_types.get(type_name, FlagTypeNotDefined())
		
			if isinstance(flags_type_definition, FlagTypeNotDefined):
				raise ValueError(f"Unknown flag type: {type_name}.")
		
			flags_type_definition["update_flags_function"](type_flags)


class BlinkFlagsManager(BrowserFlagsManager):
	"""
	Manages browser flags specifically for Blink-based browsers (like Chrome, Edge), adding support for Blink Features.

	This class extends `BrowserFlagsManager` to handle Blink-specific features,
	such as `--enable-blink-features` and `--disable-blink-features`, and provides
	a comprehensive set of predefined flags for these browsers.

	Attributes:
		_browser_exe (Optional[Union[str, pathlib.Path]]): Path to the browser executable.
		_start_page_url (Optional[str]): The URL to open when the browser starts.
		_enable_blink_features (dict[str, str]): Stores enabled Blink feature commands.
		_disable_blink_features (dict[str, str]): Stores disabled Blink feature commands.
	"""
	
	def __init__(
			self,
			browser_exe: Optional[Union[str, pathlib.Path]] = None,
			start_page_url: Optional[str] = None,
			flags_types: Optional[dict[str, FlagType]] = None,
			flags_definitions: Optional[dict[str, FlagDefinition]] = None
	):
		"""
		Initializes the BlinkFlagsManager.

		Args:
			browser_exe (Optional[Union[str, pathlib.Path]]): Path to the browser executable file.
			start_page_url (Optional[str]): Initial URL to open on browser startup.
			flags_types (Optional[dict[str, FlagType]]): Custom flag types to add or override.
			flags_definitions (Optional[dict[str, FlagDefinition]]): Custom flag definitions to add or override.
		"""
		
		blink_flags_types = {
			"blink_feature": FlagType(
					set_flag_function=self.set_blink_feature,
					remove_flag_function=self.remove_blink_feature,
					set_flags_function=self.set_blink_features,
					update_flags_function=self.update_blink_features,
					clear_flags_function=self.clear_blink_features,
					build_options_function=self.build_options_blink_features,
					build_start_args_function=self.build_start_args_blink_features
			),
		}
		
		if flags_types is not None:
			blink_flags_types.update(flags_types)
		
		blink_flags_definitions = {
			"debugger_address": FlagDefinition(
					name="debugger_address",
					command="debuggerAddress",
					type="experimental_option",
					mode="webdriver_option",
					adding_validation_function=_str_adding_validation_function
			),
			"remote_debugging_port": FlagDefinition(
					name="remote_debugging_port",
					command='--remote-debugging-port={value}',
					type="argument",
					mode="startup_argument",
					adding_validation_function=_int_adding_validation_function
			),
			"remote_debugging_address": FlagDefinition(
					name="remote_debugging_address",
					command='--remote-debugging-address="{value}"',
					type="argument",
					mode="startup_argument",
					adding_validation_function=_str_adding_validation_function
			),
			"user_agent": FlagDefinition(
					name="user_agent",
					command='--user-agent="{value}"',
					type="argument",
					mode="both",
					adding_validation_function=_str_adding_validation_function
			),
			"user_data_dir": FlagDefinition(
					name="user_data_dir",
					command='--user-data-dir="{value}"',
					type="argument",
					mode="startup_argument",
					adding_validation_function=_str_adding_validation_function
			),
			"proxy_server": FlagDefinition(
					name="proxy_server",
					command='--proxy-server="{value}"',
					type="argument",
					mode="webdriver_option",
					adding_validation_function=_str_adding_validation_function
			),
			"headless_mode": FlagDefinition(
					name="headless_mode",
					command="--headless",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"mute_audio": FlagDefinition(
					name="mute_audio",
					command="--mute-audio",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_background_timer_throttling": FlagDefinition(
					name="disable_background_timer_throttling",
					command="--disable-background-timer-throttling",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_backgrounding_occluded_windows": FlagDefinition(
					name="disable_backgrounding_occluded_windows",
					command="--disable-backgrounding-occluded-windows",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_hang_monitor": FlagDefinition(
					name="disable_hang_monitor",
					command="--disable-hang-monitor",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_ipc_flooding_protection": FlagDefinition(
					name="disable_ipc_flooding_protection",
					command="--disable-ipc-flooding-protection",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_renderer_backgrounding": FlagDefinition(
					name="disable_renderer_backgrounding",
					command="--disable-renderer-backgrounding",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"aggressive_cache_discard": FlagDefinition(
					name="aggressive_cache_discard",
					command="--aggressive-cache-discard",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"allow_running_insecure_content": FlagDefinition(
					name="allow_running_insecure_content",
					command="--allow-running-insecure-content",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_back_forward_cache": FlagDefinition(
					name="disable_back_forward_cache",
					command="--disable-back-forward-cache",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"no_process_per_site": FlagDefinition(
					name="no_process_per_site",
					command="--no-process-per-site",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"enable_precise_memory_info": FlagDefinition(
					name="enable_precise_memory_info",
					command="--enable-precise-memory-info",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"use_fake_device_for_media_stream": FlagDefinition(
					name="use_fake_device_for_media_stream",
					command="--use-fake-device-for-media-stream",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"use_fake_ui_for_media_stream": FlagDefinition(
					name="use_fake_ui_for_media_stream",
					command="--use-fake-ui-for-media-stream",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"use_file_for_fake_video_capture": FlagDefinition(
					name="use_file_for_fake_video_capture",
					command='--use-file-for-fake-video-capture={value}',
					type="argument",
					mode="both",
					adding_validation_function=_path_adding_validation_function
			),
			"autoplay_policy": FlagDefinition(
					name="autoplay_policy",
					command='--autoplay-policy={value}',
					type="argument",
					mode="both",
					adding_validation_function=_str_adding_validation_function
			),
			"deny_permission_prompts": FlagDefinition(
					name="deny_permission_prompts",
					command="--deny-permission-prompts",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_external_intent_requests": FlagDefinition(
					name="disable_external_intent_requests",
					command="--disable-external-intent-requests",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_notifications": FlagDefinition(
					name="disable_notifications",
					command="--disable-notifications",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_popup_blocking": FlagDefinition(
					name="disable_popup_blocking",
					command="--disable-popup-blocking",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_prompt_on_repost": FlagDefinition(
					name="disable_prompt_on_repost",
					command="--disable-prompt-on-repost",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"noerrdialogs": FlagDefinition(
					name="noerrdialogs",
					command="--noerrdialogs",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"enable_automation": FlagDefinition(
					name="enable_automation",
					command="--enable-automation",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"test_type": FlagDefinition(
					name="test_type",
					command="--test-type",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"remote_debugging_pipe": FlagDefinition(
					name="remote_debugging_pipe",
					command="--remote-debugging-pipe",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"silent_debugger_extension_api": FlagDefinition(
					name="silent_debugger_extension_api",
					command="--silent-debugger-extension-api",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"enable_logging_stderr": FlagDefinition(
					name="enable_logging_stderr",
					command="enable-logging=stderr",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"log_level": FlagDefinition(
					name="log_level",
					command='--log-level={value}',
					type="argument",
					mode="both",
					adding_validation_function=_str_adding_validation_function
			),
			"password_store_basic": FlagDefinition(
					name="password_store_basic",
					command="--password-store=basic",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"use_mock_keychain": FlagDefinition(
					name="use_mock_keychain",
					command="--use-mock-keychain",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_background_networking": FlagDefinition(
					name="disable_background_networking",
					command="--disable-background-networking",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_breakpad": FlagDefinition(
					name="disable_breakpad",
					command="--disable-breakpad",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_component_update": FlagDefinition(
					name="disable_component_update",
					command="--disable-component-update",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_domain_reliability": FlagDefinition(
					name="disable_domain_reliability",
					command="--disable-domain-reliability",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_sync": FlagDefinition(
					name="disable_sync",
					command="--disable-sync",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"enable_crash_reporter_for_testing": FlagDefinition(
					name="enable_crash_reporter_for_testing",
					command="--enable-crash-reporter-for-testing",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"metrics_recording_only": FlagDefinition(
					name="metrics_recording_only",
					command="--metrics-recording-only",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"no_pings": FlagDefinition(
					name="no_pings",
					command="--no-pings",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"allow_pre_commit_input": FlagDefinition(
					name="allow_pre_commit_input",
					command="--allow-pre-commit-input",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"deterministic_mode": FlagDefinition(
					name="deterministic_mode",
					command="--deterministic-mode",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"run_all_compositor_stages_before_draw": FlagDefinition(
					name="run_all_compositor_stages_before_draw",
					command="--run-all-compositor-stages-before-draw",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_new_content_rendering_timeout": FlagDefinition(
					name="disable_new_content_rendering_timeout",
					command="--disable-new-content-rendering-timeout",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"enable_begin_frame_control": FlagDefinition(
					name="enable_begin_frame_control",
					command="--enable-begin-frame-control",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_threaded_animation": FlagDefinition(
					name="disable_threaded_animation",
					command="--disable-threaded-animation",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_threaded_scrolling": FlagDefinition(
					name="disable_threaded_scrolling",
					command="--disable-threaded-scrolling",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_checker_imaging": FlagDefinition(
					name="disable_checker_imaging",
					command="--disable-checker-imaging",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_image_animation_resync": FlagDefinition(
					name="disable_image_animation_resync",
					command="--disable-image-animation-resync",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_partial_raster": FlagDefinition(
					name="disable_partial_raster",
					command="--disable-partial-raster",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_skia_runtime_opts": FlagDefinition(
					name="disable_skia_runtime_opts",
					command="--disable-skia-runtime-opts",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"in_process_gpu": FlagDefinition(
					name="in_process_gpu",
					command="--in-process-gpu",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"use_gl": FlagDefinition(
					name="use_gl",
					command='--use-gl={value}',
					type="argument",
					mode="both",
					adding_validation_function=_str_adding_validation_function
			),
			"block_new_web_contents": FlagDefinition(
					name="block_new_web_contents",
					command="--block-new-web-contents",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"force_color_profile": FlagDefinition(
					name="force_color_profile",
					command='--force-color-profile={value}',
					type="argument",
					mode="both",
					adding_validation_function=_str_adding_validation_function
			),
			"new_window": FlagDefinition(
					name="new_window",
					command="--new-window",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"no_service_autorun": FlagDefinition(
					name="no_service_autorun",
					command="--no-service-autorun",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"process_per_tab": FlagDefinition(
					name="process_per_tab",
					command="--process-per-tab",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"single_process": FlagDefinition(
					name="single_process",
					command="--single-process",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"no_sandbox": FlagDefinition(
					name="no_sandbox",
					command="--no-sandbox",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_dev_shm_usage": FlagDefinition(
					name="disable_dev_shm_usage",
					command="--disable-dev-shm-usage",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"disable_gpu": FlagDefinition(
					name="disable_gpu",
					command="--disable-gpu",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"no_first_run": FlagDefinition(
					name="no_first_run",
					command="--no-first-run",
					type="argument",
					mode="both",
					adding_validation_function=_bool_adding_validation_function
			),
			"calculate_native_win_occlusion": FlagDefinition(
					name="calculate_native_win_occlusion",
					command="CalculateNativeWinOcclusion",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"accept_ch_frame": FlagDefinition(
					name="accept_ch_frame",
					command="AcceptCHFrame",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"avoid_unload_check_sync": FlagDefinition(
					name="avoid_unload_check_sync",
					command="AvoidUnnecessaryBeforeUnloadCheckSync",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"bfcache_feature": FlagDefinition(
					name="bfcache_feature",
					command="BackForwardCache",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"heavy_ad_mitigations": FlagDefinition(
					name="heavy_ad_mitigations",
					command="HeavyAdPrivacyMitigations",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"isolate_origins": FlagDefinition(
					name="isolate_origins",
					command="IsolateOrigins",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"lazy_frame_loading": FlagDefinition(
					name="lazy_frame_loading",
					command="LazyFrameLoading",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"script_streaming": FlagDefinition(
					name="script_streaming",
					command="ScriptStreaming",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"global_media_controls": FlagDefinition(
					name="global_media_controls",
					command="GlobalMediaControls",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"improved_cookie_controls": FlagDefinition(
					name="improved_cookie_controls",
					command="ImprovedCookieControls",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"privacy_sandbox_settings4": FlagDefinition(
					name="privacy_sandbox_settings4",
					command="PrivacySandboxSettings4",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"media_router": FlagDefinition(
					name="media_router",
					command="MediaRouter",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"autofill_server_comm": FlagDefinition(
					name="autofill_server_comm",
					command="AutofillServerCommunication",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"cert_transparency_updater": FlagDefinition(
					name="cert_transparency_updater",
					command="CertificateTransparencyComponentUpdater",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"optimization_hints": FlagDefinition(
					name="optimization_hints",
					command="OptimizationHints",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"dial_media_route_provider": FlagDefinition(
					name="dial_media_route_provider",
					command="DialMediaRouteProvider",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"paint_holding": FlagDefinition(
					name="paint_holding",
					command="PaintHolding",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"destroy_profile_on_browser_close": FlagDefinition(
					name="destroy_profile_on_browser_close",
					command="DestroyProfileOnBrowserClose",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"site_per_process": FlagDefinition(
					name="site_per_process",
					command="site-per-process",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
			"automation_controlled": FlagDefinition(
					name="automation_controlled",
					command="AutomationControlled",
					type="blink_feature",
					mode="both",
					adding_validation_function=_optional_bool_adding_validation_function
			),
		}
		
		if flags_definitions is not None:
			blink_flags_definitions.update(flags_definitions)
		
		super().__init__(
				flags_types=blink_flags_types,
				flags_definitions=blink_flags_definitions
		)
		
		self._browser_exe = browser_exe
		self._start_page_url = start_page_url
		self._enable_blink_features: dict[str, str] = {}
		self._disable_blink_features: dict[str, str] = {}
	
	def build_start_args_blink_features(self) -> list[str]:
		"""
		Builds a list of Blink feature arguments for browser startup.

		Returns:
			list[str]: A list of startup arguments for Blink features.
		"""
		
		start_args = []
		
		enable_blink_features = dict(
				filter(
						lambda item: self._flags_definitions_by_types["blink_feature"][item[0]]["mode"] in ["startup_argument", "both"],
						self._enable_blink_features.items()
				)
		)
		disable_blink_features = dict(
				filter(
						lambda item: self._flags_definitions_by_types["blink_feature"][item[0]]["mode"] in ["startup_argument", "both"],
						self._disable_blink_features.items()
				)
		)
		
		if enable_blink_features:
			start_args.append("--enable-blink-features=" + ",".join(enable_blink_features.values()))
		
		if disable_blink_features:
			start_args.append("--disable-blink-features=" + ",".join(disable_blink_features.values()))
		
		return start_args
	
	def build_options_blink_features(self, options: "_blink_webdriver_option_type") -> "_blink_webdriver_option_type":
		"""
		Adds configured Blink features (`--enable-blink-features` and `--disable-blink-features`) to the WebDriver options.

		Args:
			options (_blink_webdriver_option_type): The WebDriver options object to modify.

		Returns:
			_blink_webdriver_option_type: The modified WebDriver options object.
		"""
		
		enable_blink_features = dict(
				filter(
						lambda item: self._flags_definitions_by_types["blink_feature"][item[0]]["mode"] in ["webdriver_option", "both"],
						self._enable_blink_features.items()
				)
		)
		disable_blink_features = dict(
				filter(
						lambda item: self._flags_definitions_by_types["blink_feature"][item[0]]["mode"] in ["webdriver_option", "both"],
						self._disable_blink_features.items()
				)
		)
		
		if enable_blink_features:
			options.add_argument("--enable-blink-features=" + ",".join(enable_blink_features.values()))
		
		if disable_blink_features:
			options.add_argument("--disable-blink-features=" + ",".join(disable_blink_features.values()))
		
		return options
	
	def clear_blink_features(self):
		"""Clears all configured Blink features."""
		
		self._enable_blink_features = {}
		self._disable_blink_features = {}
	
	def remove_blink_feature(self, blink_feature_name: str):
		"""
		Removes a configured Blink feature.

		This removes the feature from both the enabled and disabled lists.

		Args:
			blink_feature_name (str): The name of the Blink feature to remove.
		"""
		
		self._enable_blink_features.pop(blink_feature_name, None)
		self._disable_blink_features.pop(blink_feature_name, None)
	
	def set_blink_feature(self, blink_feature: FlagDefinition, enable: Optional[bool]):
		"""
		Sets a Blink feature to be either enabled or disabled.

		Args:
			blink_feature (FlagDefinition): The definition of the Blink feature.
			enable (Optional[bool]): `True` to enable, `False` to disable. If `None`, the feature is removed.
		"""
		
		blink_feature_name = blink_feature["name"]
		blink_feature_command = blink_feature["command"]
		adding_validation_function = blink_feature["adding_validation_function"]
		
		self.remove_blink_feature(blink_feature_command)
		
		if adding_validation_function(enable):
			if enable:
				self._enable_blink_features[blink_feature_name] = blink_feature_command
			else:
				self._disable_blink_features[blink_feature_name] = blink_feature_command
	
	def update_blink_features(self, blink_features: Union[BlinkFeatures, dict[str, Optional[bool]]]):
		"""
		Updates Blink features from a dictionary without clearing existing ones.

		Args:
			blink_features (Union[BlinkFeatures, dict[str, Optional[bool]]]): A dictionary of Blink features to set or update.

		Raises:
			ValueError: If an unknown Blink feature key is provided.
		"""
		
		for key, value in blink_features.items():
			flag_definition = self._flags_definitions_by_types["blink_feature"].get(key, FlagNotDefined())
		
			if isinstance(flag_definition, FlagNotDefined):
				raise ValueError(f"Unknown blink feature: {key}.")
		
			self.set_blink_feature(flag_definition, value)
	
	def set_blink_features(self, blink_features: Union[BlinkFeatures, dict[str, Optional[bool]]]):
		"""
		Clears existing and sets new Blink features from a dictionary.

		Args:
			blink_features (Union[BlinkFeatures, dict[str, Optional[bool]]]): A dictionary of Blink features to set.

		Raises:
			ValueError: If an unknown Blink feature key is provided.
		"""
		
		self.clear_blink_features()
		self.update_blink_features(blink_features)
	
	def _renew_webdriver_options(self) -> "_blink_webdriver_option_type":
		"""
		Abstract method to renew WebDriver options. Must be implemented in child classes.

		This method is intended to be overridden in subclasses to provide
		browser-specific WebDriver options instances (e.g., ChromeOptions, EdgeOptions).

		Returns:
			_blink_webdriver_option_type: A new instance of WebDriver options (e.g., ChromeOptions, EdgeOptions).

		Raises:
			NotImplementedError: If the method is not implemented in a subclass.
		"""
		
		raise NotImplementedError("This function must be implemented in child classes.")
	
	@property
	def browser_exe(self) -> Optional[Union[str, pathlib.Path]]:
		"""
		Returns the browser executable path.

		This property retrieves the path to the browser executable that will be used to start the browser instance.

		Returns:
			Optional[Union[str, pathlib.Path]]: The path to the browser executable.
		"""
		
		return self._browser_exe
	
	@browser_exe.setter
	def browser_exe(self, value: Optional[Union[str, pathlib.Path]]):
		"""
		Sets the path to the browser executable.

		Args:
			value (Optional[Union[str, pathlib.Path]]): The new path for the browser executable.
		"""
		
		self._browser_exe = value
	
	def build_options_arguments(self, options: "_blink_webdriver_option_type") -> "_blink_webdriver_option_type":
		"""
		Adds configured command-line arguments to the WebDriver options.

		Args:
			options (_blink_webdriver_option_type): The WebDriver options object.

		Returns:
			_blink_webdriver_option_type: The modified WebDriver options object.
		"""
		
		return super().build_options_arguments(options)
	
	def build_options_attributes(self, options: "_blink_webdriver_option_type") -> "_blink_webdriver_option_type":
		"""
		Applies configured attributes to the WebDriver options.

		Args:
			options (_blink_webdriver_option_type): The WebDriver options object.

		Returns:
			_blink_webdriver_option_type: The modified WebDriver options object.
		"""
		
		return super().build_options_attributes(options)
	
	def build_options_experimental_options(self, options: "_blink_webdriver_option_type") -> "_blink_webdriver_option_type":
		"""
		Adds experimental options to the WebDriver options.

		Args:
			options (_blink_webdriver_option_type): The WebDriver options object.

		Returns:
			_blink_webdriver_option_type: The modified WebDriver options object.
		"""
		
		return super().build_options_experimental_options(options)
	
	def build_start_args_arguments(self) -> list[str]:
		"""
		Builds a list of command-line arguments for browser startup.

		Returns:
			list[str]: A list of startup arguments.
		"""
		
		return super().build_start_args_arguments()
	
	def clear_flags(self):
		"""Clears all configured flags and resets the start page URL."""
		
		super().clear_flags()
		self._start_page_url = None
	
	@property
	def options(self) -> "_blink_webdriver_option_type":
		"""
		Builds and returns a Blink-specific WebDriver options object.

		Returns:
			_blink_webdriver_option_type: A configured Blink-based WebDriver options object.
		"""
		
		return super().options
	
	def set_arguments(self, arguments: Union[BlinkArguments, dict[str, Any]]):
		"""
		Clears existing and sets new command-line arguments from a dictionary.

		Args:
			arguments (Union[BlinkArguments, dict[str, Any]]): A dictionary of arguments to set.

		Raises:
			ValueError: If an unknown argument key is provided.
		"""
		
		super().set_arguments(arguments)
	
	def set_attributes(self, attributes: Union[BlinkAttributes, dict[str, Any]]):
		"""
		Clears existing and sets new browser attributes from a dictionary.

		Args:
			attributes (Union[BlinkAttributes, dict[str, Any]]): A dictionary of attributes to set.

		Raises:
			ValueError: If an unknown attribute key is provided.
		"""
		
		super().set_attributes(attributes)
	
	def set_experimental_options(
			self,
			experimental_options: Union[BlinkExperimentalOptions, dict[str, Any]]
	):
		"""
		Clears existing and sets new experimental options from a dictionary.

		Args:
			experimental_options (Union[BlinkExperimentalOptions, dict[str, Any]]): A dictionary of experimental options to set.

		Raises:
			ValueError: If an unknown experimental option key is provided.
		"""
		
		super().set_experimental_options(experimental_options)
	
	def set_flags(self, flags: Union[BlinkFlags, dict[str, dict[str, Any]]]):
		"""
		Clears all existing flags and sets new ones, including Blink features.

		This method delegates to the parent `set_flags` method, allowing it to handle
		all flag types defined in this manager, including 'arguments', 'experimental_options',
		'attributes', and 'blink_features'.

		Args:
			flags (Union[BlinkFlags, dict[str, dict[str, Any]]]): A dictionary where keys are flag types
				and values are dictionaries of flags to set for that type.
		"""
		
		super().set_flags(flags)
	
	@property
	def start_args(self) -> list[str]:
		"""
		Builds and returns a list of all command-line arguments for browser startup.

		Returns:
			list[str]: A list of startup arguments.
		"""
		
		args = []
		
		for type_name, type_functions in self._flags_types.items():
			args += type_functions["build_start_args_function"]()
		
		return args
	
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
		start_args += self.start_args
		
		if self._start_page_url is not None:
			start_args.append(self._start_page_url)
		
		return " ".join(start_args)
	
	@property
	def start_page_url(self) -> Optional[str]:
		"""
		Gets the initial URL to open when the browser starts.

		Returns:
			Optional[str]: The start page URL.
		"""
		
		return self._start_page_url
	
	@start_page_url.setter
	def start_page_url(self, value: Optional[str]):
		"""
		Sets the initial URL to open when the browser starts.

		Args:
			value (Optional[str]): The URL to set as the start page.
		"""
		
		self._start_page_url = value
	
	def update_arguments(self, arguments: Union[BlinkArguments, dict[str, Any]]):
		"""
		Updates command-line arguments from a dictionary without clearing existing ones.

		Args:
			arguments (Union[BlinkArguments, dict[str, Any]]): A dictionary of arguments to set or update.

		Raises:
			ValueError: If an unknown argument key is provided.
		"""
		
		super().update_arguments(arguments)
	
	def update_attributes(self, attributes: Union[BlinkAttributes, dict[str, Any]]):
		"""
		Updates browser attributes from a dictionary without clearing existing ones.

		Args:
			attributes (Union[BlinkAttributes, dict[str, Any]]): A dictionary of attributes to set or update.

		Raises:
			ValueError: If an unknown attribute key is provided.
		"""
		
		super().update_attributes(attributes)
	
	def update_experimental_options(
			self,
			experimental_options: Union[BlinkExperimentalOptions, dict[str, Any]]
	):
		"""
		Updates experimental options from a dictionary without clearing existing ones.

		Args:
			experimental_options (Union[BlinkExperimentalOptions, dict[str, Any]]): A dictionary of experimental options to set or update.

		Raises:
			ValueError: If an unknown experimental option key is provided.
		"""
		
		super().update_experimental_options(experimental_options)
	
	def update_flags(self, flags: Union[BlinkFlags, dict[str, dict[str, Any]]]):
		"""
		Updates all flags, including Blink features, without clearing existing ones.

		This method delegates to the parent `update_flags` method, allowing it to handle
		all flag types defined in this manager, including 'arguments', 'experimental_options',
		'attributes', and 'blink_features'.

		Args:
			flags (Union[BlinkFlags, dict[str, dict[str, Any]]]): A dictionary where keys are flag types
				and values are dictionaries of flags to update for that type.
		"""
		
		super().update_flags(flags)


_any_webdriver_option_type = Union[
	webdriver.ChromeOptions,
	webdriver.EdgeOptions,
	webdriver.FirefoxOptions
]
_blink_webdriver_option_type = Union[webdriver.ChromeOptions, webdriver.EdgeOptions]
