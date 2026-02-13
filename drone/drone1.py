from easytello import tello

drone = tello.Tello()
drone.takeoff()

def square():
    for i in range(4):
        drone.forward(30)
        drone.cw(90)

def triangle():
    for i in range(3):
        drone.forward(50)
        drone.cw(120)

def circle():
    for i in range(90):
        drone.forward(20)
        drone.cw(4)

def star():
    for i in range(5):
        drone.forward(40)
        drone.cw(72)

def rectangle():
    for i in range (1, 4):
        if i == 2 or i == 4:
            drone.forward(50)
            drone.cw(90)
        else:
            drone.forward(32)
            drone.cw(90)

        


square()
triangle()
circle()
star()
rectangle()
drone.land()
