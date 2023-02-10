from py_openshowvar import openshowvar  # pip3.9 install py_openshowvar
import cv2
from collections import deque
from functions import *
from robodk import *      # Robot toolbox
from robolink import *    # RoboDK API
import time

# VIDEO SETUP
cap = cv2.VideoCapture(0)  # load the camera image
cap.set(3, 1280)  # width
cap.set(4, 720)  # height
center = deque(maxlen=10)

# ROBOT INITIALIZATION
# sys.path.insert(0, "C:\Program Files\RoboDK\Python")
RDK = Robolink()  # RDK = Robolink(args=["-HIDDEN"])
RDK.setSimulationSpeed(9999)
robot = RDK.Item('KUKA KR 6 R700 sixx')
reference = robot.Parent()  # Retrieve the robot reference frame
robot.setPoseFrame(reference)  # Use the robot base frame as active reference
home = RDK.Item('Home')
pose = home.Pose()  # Set the pose variable format
robot.MoveJ(home)  # Make the first movement a joint move!

# CONNECT TO ROBOT
client = openshowvar('172.31.1.147', 7000)  # I.P adress + port 7000

# CONNECT TO ROBOT - UNNECESSARY
# client.write('$OUT[17]', 'FALSE')
# client.write(
#     'XHOME', '{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')
# client.write(
#     'MYAXIS', '{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')

while True:
    coord = tuple(ball_coord(cap, center))  # x,y,radius
    if coord:  # if tuple is not empty
        blue = 1.6*(int(coord[2])+160)  # (10,140)->(300,500)
        green = 0.75*(int(coord[0])-640)  # (0,1280)->(-640,640)->(-480,480)
        red = 1.3*(750-int(coord[1]))  # (0,720)->(0,936)->(30,936)
        position = [blue, green, red]
        poisition_mm = [(coord[0]-640)*coord[3], (coord[1]-360)*coord[3]]
        pose.setPos(position)
        robot.MoveJ(pose)
    print(robot.Joints())
    # we can use inverse kinematic robot.SolveIK(pose) instead of robot.Joints
    # for demonstration visit cube file
    move(robot.Joints(), client)
