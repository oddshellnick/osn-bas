from typing import Optional, TypedDict
from osn_bas.webdrivers.BaseDriver.dev_tools.domains.fetch import (
	RequestPausedHandlerSettings
)


class Fetch(TypedDict):
	"""
	Configuration settings for the Fetch domain of DevTools.

	This TypedDict defines the structure for configuring settings related to the Fetch domain in DevTools,
	which is used for intercepting and modifying network requests.

	Attributes:
		use (bool): A flag to indicate whether the Fetch domain event handling is enabled.
			Set to True to enable handling of Fetch domain events, False to disable.
		enable_func_path (str): The path to the function in the DevTools API to enable the Fetch domain.
			This string specifies the location of the 'enable' method within the DevTools API namespace (e.g., "fetch.enable").
		disable_func_path (str): The path to the function in the DevTools API to disable the Fetch domain.
			Similar to `enable_func_path`, but for disabling the Fetch domain (e.g., "fetch.disable").
		request_paused (Optional[RequestPausedHandlerSettings]): Optional settings specific to handling 'requestPaused' events within the Fetch domain.
			This allows for detailed configuration of how network requests are intercepted and modified when they are paused by DevTools.
	"""
	
	use: bool
	enable_func_path: str
	disable_func_path: str
	request_paused: Optional[RequestPausedHandlerSettings]


class CallbacksSettings(TypedDict):
	"""
	Settings for configuring callbacks for different DevTools event domains.
	This TypedDict aggregates settings for various DevTools event types, allowing for structured configuration
	of event handling within the DevTools integration. Currently, it specifically includes settings for the 'fetch' domain.

	Attributes:
		fetch (Fetch): Configuration settings for the Fetch domain events.
			This includes settings to enable/disable fetch event handling and specific configurations for 'requestPaused' events.
	"""
	
	fetch: Fetch


special_keys = ["use", "enable_func_path", "disable_func_path"]
