import math, time, os
from math import cos, sin

FOV = 100

# Utils

class Colour:
	_modes = ["rgb", "hsv"]
	def __init__(self, r, g, b, mode="rgb") -> None:
		self.r = r
		self.g = g
		self.b = b
		self.mode = mode if mode in self._modes else "rgb"

	def __repr__(self) -> str:
		match self.mode:
			case "rgb":
				return f'\x1b[38;2;{int(self.r)};{int(self.g)};{int(self.b)}m'
			case "hsv":
				h /= 255
				s /= 255
				v /= 255
				i = math.floor(h*6)
				f = h*6 - i
				p = v * (1-s)
				q = v * (1-f*s)
				t = v * (1-(1-f)*s)

				r, g, b = [
					(v, t, p),
					(q, v, p),
					(p, v, t),
					(p, q, v),
					(t, p, v),
					(v, p, q),
				][int(i%6)]

				r, g, b = r*255, g*255, b*255

				return f'\x1b[38;2;{int(r)};{int(g)};{int(b)}m'

class Vec2D:
	"""Helper class for positions and sizes. A set of two ints. Can be initalised with `Vec2D(5,4)` or with `Vec2D([5,4])` Can also just be a replacement for `tuple[int,int]`

	Other examples:
	>>> Vec2D(5, 2) + Vec2D(4, -1)
	Vec2D(9, 1)
	>>> Vec2D(10, 10) - Vec2D(4,1)
	Vec2D(6, 9)"""

	def __init__(self, x: list|int, y:int=None):
		self.y = int(x[1] if isinstance(x, list|tuple|Vec2D) else y)
		self.x = int(x[0] if isinstance(x, list|tuple|Vec2D) else x)

	def __repr__(self):
		return (self.x, self.y)
	def __str__(self):
		return str(self.__repr__())
	def __getitem__(self, i: int):
		if i > 1:
			raise IndexError("Vec2D has no elements outside of x and y")
		return self.__repr__()[i]
	def __add__(self, value: 'Vec2D'):
		return Vec2D(self[0]+value[0], self[1]+value[1])
	__radd__ = __add__
	def __sub__(self, value: 'Vec2D'):
		return Vec2D(self[0]-value[0], self[1]-value[1])
	__rsub__ = __sub__
	def __mul__(self, value: int):
		return Vec2D(self.x*value,self.y*value)
	__rmul__ = __mul__
	def __truediv__(self, value: int):
		return Vec2D(self.x/value,self.y/value)
	def __mod__(self, limits: 'Vec2D'):
		return Vec2D(list(map(
			lambda x, y: x%y if x >= 0 else (y + x)%y,
			self, limits
		)))
	def __eq__(self, value: 'Vec2D') -> bool:
		return self.__repr__() == Vec2D(value).__repr__()

	def normalised(self):
		return Vec2D([i/abs(i) for i in self])

# Screen

class Display:
	"""## Display
	The 2D Display, can plot points and lines"""

	@property
	def size(self):
		return self._size
	@size.setter
	def size(self, value):
		self._size = Vec2D(value)
		self._blank = list(['░'] * (self._size.x * self._size.y))
		self.origin = Vec2D(self.size)/2


	def __init__(self, size: Vec2D) -> None:
		self.size = Vec2D(size)
		self.pixels = list(self._blank)

	def clear(self):
		self.pixels[:] = list(self._blank)

	def plot(self, x, y, colour: Colour="", txt="█"):
		end = "\x1b[0m" if colour else ""
		x %= self.size.x
		y %= self.size.y
		self.pixels[y*self.size.x+x] = f'{colour}{txt[0]}{end}'

	def plot_line(self, pos0, pos1, colour: Colour="", txt="█"):
		x0, y0 = pos0
		x1, y1 = pos1
		dx = abs(x1 - x0)
		sx = 1 if x0 < x1 else -1
		dy = -abs(y1 - y0)
		sy = 1 if y0 < y1 else -1
		error = dx + dy

		while True:
			self.plot(x0, y0, colour, txt)
			e2 = error * 2
			if e2 >= dy:
				if x0 == x1: break
				error += dy
				x0 += sx
			if e2 <= dx:
				if y0 == y1: break
				error += dx
				y0 += sy

	def render(self):
		nl = "\n"
		r = f'\x1b[H{"".join(p + (nl if i % self.size.x == -1 else "") for i, p in enumerate(self.pixels))}\x1b[J'
		self.clear()
		return r

# Projection

def is_clockwise(points: list[Vec2D]):
	return sum((p1.x-p2.x)*(p1.y+p2.y) for p1, p2 in zip(points, points[-1:]+points[:-1])) < 0

def get_coord(vec3d, origin, offset=[0,0,0], rotations=[0,0,0]):
	x, y, z = vec3d
	x, z = rotate(x, z, rotations[0])
	y, z = rotate(y, z, rotations[1])
	x, y = rotate(x, y, rotations[2])

	x += offset[0]
	y += offset[1]
	z += offset[2]

	f = FOV / z
	sx, sy = x * f, y * f

	r = Vec2D(sx*1.9,sy)

	r.z = z

	r += origin

	return r

def rotate(x, y, r):
	s, c = sin(r), cos(r)
	return x * c - y * s, x * s + y * c

# Misc

def sleep(secs: float):
	time.sleep(secs)

print("\n" * (os.get_terminal_size().lines-1))
