from easytello import tello
import time
import csv

drone = tello.Tello()

def hover():
    drone.takeoff()
    time.sleep(3)
    drone.land()

with open ("test.txt", "r") as file:
    content = file.read()
    print(content)


for i in range(100):
    hover()
