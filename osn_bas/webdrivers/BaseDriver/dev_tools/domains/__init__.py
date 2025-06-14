from dataclasses import dataclass
from typing import (
	Literal,
	Optional,
	TypedDict,
	Union
)
from osn_bas.webdrivers.BaseDriver.dev_tools.domains.fetch import (
	FetchSettings,
	_Fetch
)


class Domains(TypedDict, total=False):
	"""
	Settings for configuring callbacks for different DevTools event domains.
	This TypedDict aggregates settings for various DevTools event types, allowing for structured configuration
	of event handling within the DevTools integration. Currently, it specifically includes settings for the 'fetch' domain.

	Attributes:
		fetch (_Fetch): Configuration settings for the Fetch domain events.
			This includes settings to enable/disable fetch event handling and specific configurations for 'requestPaused' events.
	"""
	
	fetch: _Fetch


@dataclass
class DomainsSettings:
	fetch: Optional[FetchSettings] = None
	
	def to_dict(self) -> Domains:
		kwargs = {}
		
		if self.fetch is not None:
			kwargs["fetch"] = self.fetch.to_dict()
		
		return Domains(**kwargs)


domains_type = Literal["fetch"]
domains_classes_type = Union[_Fetch]
