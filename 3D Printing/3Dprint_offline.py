# Type help("robolink") or help("robodk") for more information
# Press F5 to run the script
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *    # RoboDK API
from robodk import *      # Robot toolbox
import time
import re
from py_openshowvar import openshowvar

############################## FUNCTIONS #######################################


def extruder_offline(robot, arg):
    if arg == 'START':
        # if robot.getDI('$IN[10]') == 'True':
        robot.setDO('$OUT[16]', 'True')
        # else:
        #     print('Extruder not heated')
    elif arg == 'STOP':
        robot.setDO('$OUT[16]', 'False')
    else:
        print('The input of extruder() has to be either START or STOP')


def parser(filename):
    parsed_file = list()
    layer = 0
    with open(filename) as gcode:
        for line in gcode:
            line = line.strip()
            if re.findall("LAYER:", line):
                layer += 1
                continue
            if re.findall("G1", line):  # print
                coord = re.findall(r'[XY].?\d+.\d+', line)
                if len(coord) == 2:
                    X = re.findall('\d*\.?\d+', coord[0])[0]
                    Y = re.findall('\d*\.?\d+', coord[1])[0]
                    parsed_file.append([float(X), float(Y), layer, True])
    return parsed_file

################################## MAIN ########################################


# ROBODK INITIALIZATION
RDK = Robolink()  # sys.path.insert(0, "C:\Program Files\RoboDK\Python")
robot = RDK.Item('KUKA KR 6 R700 sixx')
RDK.setSimulationSpeed(1)
reference = robot.Parent()  # Retrieve the robot reference frame
robot.setPoseFrame(reference)  # Use the robot base frame as active reference
home = [0, -90, 90, 0, 0, 0]
robot.MoveJ(home)
path = parser(
    'C:/Users/Luky/Desktop/DTU/Industrial Robotics/Final_Assignemt/Notes/lion_spiralized.gcode')
robot.setSpeed(speed_linear=80, speed_joints=20,
               accel_linear=3000, accel_joints=20)

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
robot.MoveL(transl([0, 70, 0])*orient_frame2tool)
robot.MoveL(transl([70, 70, 0])*orient_frame2tool)
robot.MoveL(transl([70, 0, 0])*orient_frame2tool)
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)

# PRINTING
printing_status = False
for item in path:
    if item[3] == False and printing_status == True:
        extruder_offline(robot, "STOP")
        printing_status = False
    elif item[3] == True and printing_status == False:  # print
        extruder_offline(robot, "START")
        printing_status = True
    target_point = [item[0], item[1], 0.55*item[2]+0.15]
    target0 = transl(target_point)*orient_frame2tool
    robot.MoveL(target0, blocking=False)
robot.MoveJ(home)

# target0 is referenced to the task_frame, not baseframe of the robot afaik
# if we use SolveIK (inv kinematics), the angles of the

# P1: -9.78, -75.36, 84.92, 12.63, 35.7, -16.86
# P2: 10.73, -75.10, 84.60, -12.65, 35,76, 18.13
# P3: -7.88, -47.37, 45.49, 8.23, 46.61, -10.88
