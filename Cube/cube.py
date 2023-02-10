import time
from py_openshowvar import openshowvar  # pip3.9 install py_openshowvar
from robolink import *    # API to communicate with RoboDK
from robodk import *      # robodk robotics toolbox
from functions import *

# ROBOT INITIALIZATION
# sys.path.insert(0, "C:\Program Files\RoboDK\Python")
RDK = Robolink()  # args=["-HIDDEN"]
RDK.setSimulationSpeed(1)
robot = RDK.ItemUserPick('Select a robot', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception('No robot selected or available')
reference = robot.Parent()  # Retrieve the robot reference frame
robot.setPoseFrame(reference)  # Use the robot base frame as active reference
target1 = RDK.Item('Target 1')
target2 = RDK.Item('Target 2')
robot.MoveJ(target1)  # Make the first movement a joint move!
pose = target1.Pose()  # Set the pose variable format

# CONNECT TO ROBOT
client = openshowvar('172.31.1.147', 7000)  # I.P adress + port 7000
client.write('$OUT[17]', 'FALSE')
client.write(
    'XHOME', '{A1 0.0, A2 -90, A3 90, A4 0, A5 0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 -90.0}')
client.write(
    'MYAXIS', '{A1 0.0, A2 -90, A3 90, A4 0, A5 0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')

# CUBE AROUND HOME:
robot.MoveJ(target1)
move(robot.Joints(), client)
for i in range(5):
    ang = i*2*pi/4  # angle: 0, 60, 120, ...
    pose = (rotz(ang)*transl(120, 0, 0)*rotz(-ang))*target1.Pose()
    robot.MoveL(pose)
    move(robot.Joints(), client)  # default solution


# CUBE AROUND TARGET:
robot.MoveL(target2)
move(robot.Joints(), client)  # default solution
for i in range(5):
    ang = i*2*pi/4  # angle: 0, 60, 120, ...
    pose = rotz(ang)*transl(120, 0, 0)*rotz(-ang)*target2.Pose()
    robot.MoveL(pose)
    move(robot.Joints(), client)  # default solution

# Move back to the center, then target1:
robot.MoveJ(target1)
move(robot.Joints(), client)
