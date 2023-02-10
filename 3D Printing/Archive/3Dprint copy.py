# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
import time
from py_openshowvar import openshowvar
from functions import *

# ROBODK INITIALIZATION
RDK = Robolink()  # sys.path.insert(0, "C:\Program Files\RoboDK\Python")
robot = RDK.Item('KUKA KR 6 R700 sixx')
RDK.setSimulationSpeed(0.4)  # initialization is slow
reference = robot.Parent()  # Retrieve the robot reference frame
robot.setPoseFrame(reference)  # Use the robot base frame as active reference
home = [0, -90, 90, 0, 0, 0]
robot.MoveJ(home)
path = parser(
    'C:/Users/Luky/Desktop/DTU/Industrial Robotics/Final_Assignemt/Notes/vase.gcode')

# CONNECT TO ROBOT
client = openshowvar('172.31.1.147', 7000)  # I.P adress + port 7000
client.write('$OUT[17]', 'FALSE')
client.write(
    'XHOME', '{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')
client.write(
    'MYAXIS', '{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')
time.sleep(1)

# 1) move to points P1, P2, P3, define a frame
# 2) move to one of the P and get angles of it and insert to home_joints
# 3) dont start extruder until loop
item_frame = RDK.Item('task_frame')
home_joints = [-5.520000, -107.550000, 115.910000, 1.620000,
               37.390000, -0.2400006]  # orient robot with joints to P1
robot.setFrame(item_frame)
robot.MoveJ(home_joints)


# invH(item_frame.Pose()) = homogeneous matrix
# robot.SolveFK(home_joints) = joint orientation
orient_frame2tool = invH(item_frame.Pose())*robot.SolveFK(home_joints)
# remove the last column of homogeneous
orient_frame2tool[0:3, 3] = Mat([0, 0, 0])
# result = homogeneous matrix orientation of the robot with zeros in last column

# move in workspace to see if it doesn't hit table:
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)
move(robot.Joints(), client)
robot.MoveL(transl([0, 70, 0])*orient_frame2tool)
move(robot.Joints(), client)
robot.MoveL(transl([70, 70, 0])*orient_frame2tool)
move(robot.Joints(), client)
robot.MoveL(transl([70, 0, 0])*orient_frame2tool)
move(robot.Joints(), client)
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)
move(robot.Joints(), client)

# GET RID OF EXTRA FILAMENT
robot.MoveL(transl([0, 0, 1])*orient_frame2tool)
move(robot.Joints(), client)
time.sleep(6)
extruder(client, "START")
time.sleep(4)

# PRINTING
RDK.setSimulationSpeed(0.4)  # printing is fast
printing_status = False
for item in path:
    if item[3] == False and printing_status == True:
        extruder(client, "STOP")
        printing_status = False
    elif item[3] == True and printing_status == False:  # print
        extruder(client, "START")
        printing_status = True
    target_point = [item[0], item[1], 0.4*item[2]+0.4]
    target0 = transl(target_point)*orient_frame2tool
    robot.MoveL(target0)
    move(robot.Joints(), client)
extruder(client, "STOP")
robot.moveJ(home)

# target0 is referenced to the task_frame, not baseframe of the robot afaik
# if we use SolveIK (inv kinematics), the angles of the

# P1: -5.52 -107.55 115.91 1.62 37.39 -0.24
# P2: 13.34 -108.15 116.43 -18.85 40.36 29.33
# P2 dal: 23.72 -105.25 114.28 -28 43.73 43.69
# P3: -6.59 -86.19 96.72 3 35.27 -2.17
