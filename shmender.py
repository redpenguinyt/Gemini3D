from gemini import Scene, Line, sleep, Vec2D, Sprite, Input, Polygon, txtcolours as tc
from gemini.utils import is_clockwise, hsv_to_rgb
from math import sin, cos, pi
import json, os, datetime

print("\n".join([f"{i+1}. {n[:-5]}" for i, n in enumerate(os.listdir("3D models"))]))
SAVE_FILE = f"3D models/{input('Enter the file name you wish to edit: ')}.json"

MAX_FPS = 60
fps = MAX_FPS

if not os.path.exists(SAVE_FILE):
	with open(SAVE_FILE, "w") as f:
		f.write('{"vertices": [], "faces": [], "offset": [0,0,10,0,0.25], "rotation": ["0", "t", "0"]}')

with open(SAVE_FILE, "r") as f:
	data = json.load(f)
	VERTICES = data["vertices"]

	FACES = data["faces"]

	offset = data["offset"]
	rotation = data["rotation"]

FOV = 100
ZOOM = 20

counter = 0
draw_mode = 3
draw_mode_count = 4
texture_mode = 0
texture_mode_count = 2
is_move_enabled = False
move_keys = ["d", "a", "e", "q", "w", "s", "left_arrow", "right_arrow", "down_arrow", "up_arrow"]
OFFSET_AMOUNT = [2,2,2,pi/4,pi/8]

view = Scene((140,40), is_main_scene=True, clear_char=" ")
ORIGIN = view.size/2

def get_coord(x, y, z):
	x, z = rotate(x, z, offset[3]+eval(rotation[1], {"t": counter}))
	y, z = rotate(y, z, offset[4]+eval(rotation[0], {"t": counter}))
	x, y = rotate(x, y, eval(rotation[2], {"t": counter}))

	x += offset[0]
	y += offset[1]
	z += offset[2]
	f = FOV / z
	sx, sy = x * f, y * f

	r = Vec2D(sx*1.9,sy)

	r.z = z

	return r

def average_z_axis(vertices):
	return sum(get_coord(*VERTICES[i]).z for i in vertices)/len(vertices)

def get_colour(face):
	match texture_mode:
		case 0:
			shade = 255/len(FACES)*(FACES.index(face)+1)
			return tc.custom_fore(*hsv_to_rgb(shade, 255, 255))
		case 1:
			shade = 64+128/len(FACES)*(FACES.index(face)+1)
			return tc.custom_fore(shade, shade, shade)

def loop():
	match draw_mode:
		case 0:
			for i, vertex in enumerate(VERTICES):
				a = Sprite(ORIGIN + get_coord(*vertex), str(i))
		case 1:
			for face in FACES:
				points = [ORIGIN + get_coord(*VERTICES[vertex]) for vertex in face]
				if is_clockwise(points):
					for i in range(len(points)):
						a = Line(points[i], points[(i+1)%len(points)])
		case 2:
			for face in list(sorted(FACES, key=average_z_axis, reverse=True)):
				points = [ORIGIN + get_coord(*VERTICES[vertex]) for vertex in face]
				if is_clockwise(points):
					a = Polygon(points, colour=get_colour(face))
		case 3:
			for face in list(sorted(FACES, key=average_z_axis, reverse=True)):
				points = [ORIGIN + get_coord(*VERTICES[vertex]) for vertex in face]
				if is_clockwise(points):
					a = Polygon(points, colour=get_colour(face))
					for i in range(len(points)):
						a = Line(points[i], points[(i+1)%len(points)], colour=tc.custom_fore(0,0,0))

def rotate(x, y, r):
	s, c = sin(r), cos(r)
	return x * c - y * s, x * s + y * c

while True:
	start = datetime.datetime.now()
	view.children[:] = []
	counter += pi/64

	loop()
	fps_display = Sprite((0,0), f"FPS: {round(fps, 1)}")

	view.size = Vec2D(os.get_terminal_size()) - Vec2D(0,4)
	view.render()
	print("move (WASD/EQ), rotate (arrow keys), back (m)"  if is_move_enabled else "move (m), vertices (v), faces (f), views (t), rotate (r), texture (c), save (s)")

	elapsed_time = ( datetime.datetime.now() - start ).total_seconds()
	used_fps = min(1/elapsed_time, MAX_FPS)
	sleep(((1/used_fps) - elapsed_time) if elapsed_time < (1/used_fps) else 0)
	fps = 1/elapsed_time
	k = Input().pressed_key
	if is_move_enabled:
		if k == "m":
			is_move_enabled = False
		elif k in move_keys:
			i = move_keys.index(k)
			offset[int(i/2)] += OFFSET_AMOUNT[int(i/2)] if i%2==1 else -OFFSET_AMOUNT[int(i/2)]
	else:
		match k:
			case "m":
				is_move_enabled = True
			case "v":
				option = ""
				while True:
					print(VERTICES)
					option = input("X,Y,Z or q: ")
					if option == "q":
						break
					else:
						VERTICES.append(eval(f"({option})"))
			case "f":
				print(FACES)
				option = ""
				while option != "q":
					print("add or delete a face? (a/d/q) ")
					option = Input().get_key_press(is_wait=True)
					if option == "a":
						FACES.append(eval(f"({input('Vertex IDs, seperated by commas: ')})"))
						print(FACES)
					elif option == "d":
						FACES.pop(int(input("Enter the index of the face you wish to remove: ")))
						print(FACES)
			case "t":
				draw_mode += 1
				draw_mode %= draw_mode_count
			case "c":
				texture_mode += 1
				texture_mode %= texture_mode_count
			case "r":
				user_input = input("X/Y/Z followed by algebraic equation with t being the value for time").lower()
				if user_input.startswith(("x", "y", "z")):
					rotation[["x","y","z"].index(user_input[0])] = user_input[1:]
					sleep(.5)
			case "s":
				json.dump({"vertices": VERTICES, "faces": FACES, "offset": offset, "rotation": rotation}, open(SAVE_FILE, "w"), indent=4)
				print(f"Saved to {SAVE_FILE}!")
				sleep(.5)