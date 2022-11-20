from gemini3d import sleep, is_clockwise, get_coord, Display
from math import pi
import os

window_size = os.get_terminal_size()
window_size = (window_size.columns, window_size.lines-3)
display = Display(window_size)

FPS = 60

VERTICES = [[1,1,1],[1,1,-1,],[-1,1,1],[-1,1,-1],[1,-1,1],[1,-1,-1],[-1,-1,1],[-1,-1,-1]]

FACES = [[1,0,2,3],[5,4,0,1],[7,5,1,3],[6,7,3,2],[4,6,2,0],[6,4,5,7]]

offset = [0,0,10]
rotation = ["0","t","0.25"]

FOV = 100

counter = 0

def loop():
	for face in FACES:
		points = [
			get_coord(
				VERTICES[vertex],
				offset,
				[
					eval(rotation[1], {"t": counter}),
					eval(rotation[0], {"t": counter}),
					eval(rotation[2], {"t": counter})
				]
				) for vertex in face
		]
		if is_clockwise(points):
			for i in range(len(points)):
				display.plot_line(points[i], points[(i+1)%len(points)])



while True:
	counter += pi/64

	loop()
	print(display.render())
	print(display.origin, display.size)
	sleep(1/FPS)