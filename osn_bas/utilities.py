from typing import Optional
from win32api import GetSystemMetrics


class WindowRect:
	"""
	Represents a window rectangle with x, y, width, and height.

	Attributes:
		x (int): The x-coordinate of the top-left corner. Defaults to 1/4 of screen width.
		y (int): The y-coordinate of the top-left corner. Defaults to 10% of screen height.
		width (int): The width of the rectangle. Defaults to 1/2 of screen width.
		height (int): The height of the rectangle. Defaults to 80% of screen height.

	:Usage:
		rect = WindowRect()
		print(rect.x, rect.y, rect.width, rect.height)

		rect = WindowRect(x=100, y=50, width=800, height=600)
		print(rect.x, rect.y, rect.width, rect.height)
	"""
	
	def __init__(
			self,
			x: Optional[int] = None,
			y: Optional[int] = None,
			width: Optional[int] = None,
			height: Optional[int] = None
	):
		"""
		Initializes WindowRect with optional x, y, width, and height values.

		Args:
			x (Optional[int]): The x-coordinate. Defaults to None.
			y (Optional[int]): The y-coordinate. Defaults to None.
			width (Optional[int]): The width. Defaults to None.
			height (Optional[int]): The height. Defaults to None.

		:Usage:
		   rect = WindowRect(0, 0, 300, 200)
		"""
		self.x = GetSystemMetrics(0) // 4
		
		self.y = int(GetSystemMetrics(1) * 0.1)
		
		self.width = GetSystemMetrics(0) // 2
		
		self.height = int(GetSystemMetrics(1) * 0.8)
		
		self.set_rect(x, y, width, height)
	
	def set_rect(
			self,
			x: Optional[int] = None,
			y: Optional[int] = None,
			width: Optional[int] = None,
			height: Optional[int] = None
	) -> "WindowRect":
		"""
		Sets the rectangle dimensions.

		Args:
			x (Optional[int]): The x-coordinate. Defaults to None.
			y (Optional[int]): The y-coordinate. Defaults to None.
			width (Optional[int]): The width. Defaults to None.
			height (Optional[int]): The height. Defaults to None.

		Returns:
			WindowRect: Returns the instance for method chaining.

		:Usage:
			rect = WindowRect().set_rect(0, 0, 300, 200)
		"""
		if x is not None:
			self.x = x
		
		if y is not None:
			self.y = y
		
		if width is not None:
			self.width = width
		
		if height is not None:
			self.height = height
		
		return self
