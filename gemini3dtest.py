from gemini3d import Display, sleep, Colour
import os

FPS = 5

window_size = os.get_terminal_size()
window_size = (window_size.columns, window_size.lines-3)
display = Display(window_size)

i = 0
while True:
	i += 1; i %= 10
	display.plot(0,i, colour=Colour(0,255,0))
	print(display.render())
	sleep(1/FPS)