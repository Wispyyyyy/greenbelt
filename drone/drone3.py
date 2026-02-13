from easytello import tello

import math
drone = tello.Tello()

drone.takeoff()

# drone.go(67, -67, -67, 67)

drone.curve(x1 = 67, x2 = 100, y1= 100, y2 = 67, z1= 100, z2 = 67, speed = math.sqrt(6.7))

drone.land