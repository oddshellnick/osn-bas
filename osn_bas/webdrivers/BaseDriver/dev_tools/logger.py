from contextlib import AbstractAsyncContextManager
from types import TracebackType

import trio
import inspect
import warnings
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import (
	Any,
	Literal,
	Optional
)
from osn_bas.webdrivers.BaseDriver.dev_tools.utils import (
	TargetData,
	log_error
)


class SessionLogger:
	def __init__(
			self,
			target_data: TargetData,
			receive_channel: trio.MemoryReceiveChannel,
			file_path: Path
	):
		self._target_data = target_data
		self._receive_channel = receive_channel
		self._file_path = file_path
	
	async def run(self):
		try:
			io_wrapper = await trio.open_file(self._file_path, "a+", encoding="utf-8")
			end_of_entry = "\n\n" + "=" * 100 + "\n\n"
		
			async with io_wrapper as file:
				async for log_entry in self._receive_channel:
					await file.write(log_entry.to_string() + end_of_entry)
		except trio.Cancelled:
			pass
		except (Exception,):
			log_error()


@dataclass(frozen=True)
class Log:
	target_data: TargetData
	message: str
	level: "LogLevel"
	timestamp: datetime
	source_function: str
	extra_data: Optional[dict[str, Any]] = None
	
	def to_dict(self) -> dict[str, Any]:
		log_dict = {
			"target_data": self.target_data.to_dict(),
			"timestamp": self.timestamp.isoformat(),
			"level": self.level,
			"source_function": self.source_function,
			"message": self.message,
		}
		
		if self.extra_data is not None:
			log_dict["extra_data"] = self.extra_data
		
		return log_dict
	
	def to_string(self) -> str:
		return "\n".join(f"{key}: {value}" for key, value in self.to_dict().items())


class LoggerManager:
	def __init__(self, log_file_path: Path):
		self._file_path = log_file_path
		self._nursery: Optional[AbstractAsyncContextManager[trio.Nursery, Optional[bool]]] = None
		self._nursery_object: Optional[trio.Nursery] = None
		self._session_channels: dict[str, trio.MemorySendChannel] = {}
		self._lock = trio.Lock()

	async def __aenter__(self):
		self._nursery = trio.open_nursery()
		self._nursery_object = await self._nursery.__aenter__()

	async def __aexit__(
			self,
			exc_type: Optional[type],
			exc_val: Optional[BaseException],
			exc_tb: Optional[TracebackType]
	):
		def _close_nursery_object():
			"""Closes the Trio nursery object and cancels all tasks within it."""

			if self._nursery_object is not None:
				self._nursery_object.cancel_scope.cancel()
				self._nursery_object = None

		async def _close_nursery():
			"""Asynchronously exits the Trio nursery context manager."""

			if self._nursery is not None:
				await self._nursery.__aexit__(exc_type, exc_val, exc_tb)
				self._nursery = None

		_close_nursery_object()
		await _close_nursery()
	
	async def check_session_exists(self, target_data: TargetData) -> bool:
		async with self._lock:
			return target_data.target_id in self._session_channels
	
	async def add_session(self, target_data: TargetData):
		if self._nursery_object is None:
			raise RuntimeError("Nursery has not been set. Call set_nursery() first.")

		if await self.check_session_exists(target_data):
			return

		async with self._lock:
			send_channel, receive_channel = trio.open_memory_channel(max_buffer_size=100)
			session_logger = SessionLogger(target_data, receive_channel, self._file_path)

			self._nursery_object.start_soon(session_logger.run,)
			self._session_channels[target_data.target_id] = send_channel
	
	async def log(
			self,
			target_data: TargetData,
			level: "LogLevel",
			message: str,
			source_function: str,
			extra_data: Optional[dict[str, Any]] = None
	):
		log_entry = Log(
				target_data=target_data,
				message=message,
				level=level,
				timestamp=datetime.now(),
				source_function=source_function,
				extra_data=extra_data
		)

		if await self.check_session_exists(target_data):
			try:
				self._session_channels[target_data.target_id].send_nowait(log_entry)
			except trio.WouldBlock:
				warnings.warn(
						f"WARNING: Log channel for session {target_data.target_id} is full. Log dropped: {message}"
				)
		else:
			warnings.warn(
					f"WARNING: Attempted to log to a non-existent session: {target_data.target_id}\n\n{log_entry.to_string()}"
			)
	
	async def remove_session(self, target_data: TargetData):
		if not await self.check_session_exists(target_data):
			return

		async with self._lock:
			channel = self._session_channels.pop(target_data.target_id)
			await channel.aclose()


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
