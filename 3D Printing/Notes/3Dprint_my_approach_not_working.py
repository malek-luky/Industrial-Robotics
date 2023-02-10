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
RDK.setSimulationSpeed(1000)
robot = RDK.Item('KUKA KR 6 R700 sixx')
reference = robot.Parent()  # Retrieve the robot reference frame
robot.setPoseFrame(reference)  # Use the robot base frame as active reference
pose = robot.Pose()
frame = RDK.Item('task_frame')
robot.setFrame(frame)


# # CONNECT TO ROBOT
# client = openshowvar('172.31.1.147', 7000)  # I.P adress + port 7000
# client.write('$OUT[17]', 'FALSE')
# client.write(
#     'XHOME', '{A1 0, A2 -88.76, A3 106.57, A4 0, A5 22.78, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')
# client.write(
#     'MYAXIS', '{A1 0, A2 -88.76, A3 106.57, A4 0, A5 22.78, A6 0.0, E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')
# time.sleep(1)

# PARSER
# format [X, Y, layer]
path = parser(
    'C:/Users/Luky/Desktop/DTU/Industrial Robotics/Final_Assignemt/Notes/vase.gcode')

# PRINTING
#extruder(client, "START")
for item in path:
    pose = transl(518.024, -3.606, 700.050)*rotz(-87.625)*roty(-2.976)*rotx(1.175) * \
        pose.setPos([item[0], item[1], 0.4*item[2]+0.4])
    # robot.MoveL(pose)
    print(robot.SolveIK(pose))
    time.sleep(2)
    #move(robot.Joints(), client)
#extruder(client, "STOP")
