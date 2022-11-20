import contextlib, sys, termios, fcntl # Input
import math, time, os

FPS = 20

class WindowSize():
	def __init__(self) -> None:
		self._window_size = os.get_terminal_size()
		self.lines = self._window_size.lines - 2
		self.columns = self._window_size.columns
window_size = WindowSize()

BLANK_SCREEN = ['░'] * (window_size.lines * window_size.columns)
pixels = BLANK_SCREEN[:]

class Input:
	_arrow_keys = {"a": "up","b": "down","c": "right","d": "left"}

	def __init__(self):
		self.pressed_key = self.get_key_press()

	def __repr__(self) -> str:
		return self.pressed_key
	def __str__(self) -> str:
		return str(self.__repr__())

	def string_key(self, c: str | None) -> str:
		key = repr(c)[1:-1].lower() if c else None
		if key == "\\x1b" and self.get_key_press() == "[":
			key = f"{self._arrow_keys[self.get_key_press()]}_arrow"
		return key

	def get_key_press(self) -> str|None:
		fd = sys.stdin.fileno()

		oldterm = termios.tcgetattr(fd)
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

		try:
			with contextlib.suppress(IOError):
				c = sys.stdin.read(1)
				return self.string_key(c)
		finally:
			termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
			fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

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

def plot(x, y, colour: Colour="", txt="█"):
	end = "\x1b[0m" if colour else ""
	try:
		pixels[y*window_size.columns+x] = f'{colour}{txt[0]}{end}'
	except IndexError:
		return

def render():
	global pixels
	nl = "\n"
	print(f'\x1b[H{"".join(p + (nl if i % window_size.columns == -1 else "") for i, p in enumerate(pixels))}\x1b[J')
	pixels = BLANK_SCREEN[:]

def sleep(secs: float):
	time.sleep(secs)

print("\n" * (os.get_terminal_size().lines-1))

pos = 0,0
direction = 2,1
while True:
	pos = pos[0] + direction[0], pos[1] + direction[1]
	plot(pos[0],pos[1], colour=Colour(0,255,0))
	render()
	sleep(1/FPS)