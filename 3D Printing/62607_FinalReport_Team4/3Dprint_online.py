# Type help("robolink") or help("robodk") for more information
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
from robolink import *                                       # RoboDK API
from robodk import *                                         # Robot toolbox
import time                                                  # Standard library for representing time
from py_openshowvar import openshowvar                       # Python port of KUKA VarProxy client
from functions import *                                      # Our functions

# ROBODK INITIALIZATION
RDK = Robolink()                                             # Initialize Robolink as RDK
robot = RDK.Item('KUKA KR 6 R700 sixx')                      # Retrieve robot from RDK
RDK.setSimulationSpeed(1)                                    # ADJUSTABLE speed which corelates with speed of robot
reference = robot.Parent()                                   # Retrieve the robot reference frame
robot.setPoseFrame(reference)                                # Use the robot base frame as active reference
home = [0, -90, 90, 0, 0, 0]                                 # Joint angles for default home position
robot.MoveJ(home)                                            # Move to default home position in RoboDK
robot.setSpeed(speed_linear=20, speed_joints=20,             # ADJUSTABLE 
               accel_linear=3000, accel_joints=20)           # Robot speed together w/ line 11
layer_height = 0.55                                          # ADJUSTABLE layer height


# PARSER 
path = parser('desired/path/to/gcode')                       # ADJUSTABLE: Parse the gcode

#INTERPOLATION CHECK
detail = 1.4                                                 # Everything over this distance is interpolated
interpolate(path, detail)                                    # New interpolated path
error = False                                                # Initialize error status
for i in range(len(path)-1):                                 # Additional check, loop through parsed list
    if distance(path[i], path[i+1]) > detail:                # If consequent point are far apart
        error = True                                         # Error has occured, debug.
print('Smoothing Error') if error else print('Smoothing OK') # Print status validation


# CONNECT TO ROBOT
# client = openshowvar('172.31.1.147', 7000)                   # I.P adress + port 7000
# client.write('$OUT[16]', 'FALSE')                            # Turn off extruder if some before left it on
# client.write(                                                
#   'XHOME', '{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0,\
#         E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')    # Set home command position to the robot
# client.write(                                                
#   'MYAXIS', '{A1 0.0, A2 -90, A3 90, A4 0, A5 -0, A6 0.0,\
#        E1 0.0, E2 0.0, E3 0.0, E4 0.0, E5 0.0, E6 0.0}')     # Command robot to move home as well
# time.sleep(3)                                                # Wait for safety reasons
print('To run the simulation on real robot, uncomment all lines with keyword "client"')


#TASK FRAME INIT
# 1) move robot to points P1, P2 on X-Axis and P3 on Y-Axis
# 2) define frame by algebraic properties and basis transformation or in RoboDK
# 2) move to one of the P and retrieve end-effector angle
item_frame = RDK.Item('task_frame')                          # ADJUSTABLE retrieve task_frame from RoboDK
home_joints = [-5.520000, -107.550000, 115.910000, 1.620000,
               37.390000, -0.2400006]                        # ADJUSTABLE Orient end-effector wrt task_frame angle
robot.setFrame(item_frame)                                   # Use newly obtained frame as reference
robot.MoveJ(home_joints)                                     # Move to home, first move must be joint move to avoid singularities
# move(robot.Joints(), client)                             

#INVERSE KINEMATICS
# For use with general starting position of the robot: compute 
# future movement's joint angles by inverse kinematics transformation used on
# desired destination point in space, which is obtained by forward kinematics of 
# current robot pose.
orient_frame2tool = invH(item_frame.Pose())*robot.SolveFK(home_joints)
# remove unnecessary position vector of homogeneous transformation matrix
# -> only rotational matrix is persieved
orient_frame2tool[0:3, 3] = Mat([0, 0, 0])


# GET RID OF EXTRA FILAMENT (CAN BE REMOVED)
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)             # Printing blob
# move(robot.Joints(), client)                               
time.sleep(2)                                                # Used to leave the blob
robot.MoveL(transl([0, 0, 3])*orient_frame2tool)             # Move up to get rid of the filament 

# ADJUSTABLE SAFETY CHECK of task_frame margins
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)             # Move to the first corner
# move(robot.Joints(), client)                               
robot.MoveL(transl([0, 70, 0])*orient_frame2tool)            # Move to the second corner
# move(robot.Joints(), client)                               
robot.MoveL(transl([70, 70, 0])*orient_frame2tool)           # Move to the third corner
# move(robot.Joints(), client)                               
robot.MoveL(transl([70, 0, 0])*orient_frame2tool)            # Move to the forth corner
# move(robot.Joints(), client)                               
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)             # Move back to the start
# move(robot.Joints(), client)                               

# PRINTING
RDK.setSimulationSpeed(4)                                    # ADJUSTABLE set sim speed
for item in path:                                            # For each line of parsed file:
    # inject parsed coordinates and calculate Z-axis (based on layer height, and adjustable 0.15 offset for first layer)
    target_point = [item[0], item[1], layer_height*item[2]+0.15]
    target0 = transl(target_point)*orient_frame2tool         # Compute translation with respect to task_frame
    robot.MoveL(target0, blocking=False)                     # move to the target in linear manner
    # move(robot.Joints(), client)                           
robot.MoveJ(home)                                            # When done, move to home joint position
