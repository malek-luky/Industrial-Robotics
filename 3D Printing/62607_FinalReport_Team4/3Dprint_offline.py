# Type help("robolink") or help("robodk") for more information
# Documentation: https://robodk.com/doc/en/RoboDK-API.html
# Reference:     https://robodk.com/doc/en/PythonAPI/index.html
# Note: It is not required to keep a copy of this file, your python script is saved with the station
from robolink import *                                              # RoboDK API
from robodk import *                                                # Robot toolbox
import time                                                         # Standard time library
import re                                                           # Imports the regex expressions

######################################################### FUNCTIONS #########################################################


def extruder_offline(robot, arg):
    '''Turns on and off the extrusion '''                           # Not used in code for reasons described above
    if arg == 'START':                                              # User sets the arg to start printing
        robot.setDO('$OUT[16]', 'True')                             # Set the output value to start printing
    elif arg == 'STOP':                                             # User sets the arg to stop printing
        robot.setDO('$OUT[16]', 'False')                            # Set the output value to stop printing
    else:
        print('The input of extruder() has to be either START or STOP')

def parser(filename):
    '''Parse gcode commands to be used in our code'''
    parsed_file = list()                                            # Create a list
    layer = 0                                                       # Z-axis, or current height of the print
    with open(filename) as gcode:                                   # Open gcode path and use as variable
        for line in gcode:                                          # For each line in gcode:
            line = line.strip()                                     # Delete all unnecessary ASCII characters 
            if re.findall("LAYER:", line):                          # If new layer found, update z-axes
                layer += 1                                          # Add the layer value
                continue                                            # Skip the next if
            if re.findall("G1", line):                              # Check if line begins with "G1"
                coord = re.findall(r'[XY].?\d+.\d+', line)          # Assign coord values
                if len(coord) == 2:                                 # If both coords were assigned
                    X = re.findall('\d*\.?\d+', coord[0])[0]        # Assign X-value
                    Y = re.findall('\d*\.?\d+', coord[1])[0]        # Assign Y-value
                    parsed_file.append([float(X), float(Y), layer, True])   # Append our desired output for use in the project
    return parsed_file   


########################################################### MAIN ###########################################################

# ROBODK INITIALIZATION
RDK = Robolink()                                                     # sys.path.insert(0, "C:\ProgramFiles\RoboDK\Python")
robot = RDK.Item('KUKA KR 6 R700 sixx')                              # Create the robot instance
RDK.setSimulationSpeed(1)                                            # ADJUSTABLE: Simulation speed (1=default)
reference = robot.Parent()                                           # Retrieve the robot reference frame
robot.setPoseFrame(reference)                                        # Use the robot base frame as active reference
home = [0, -90, 90, 0, 0, 0]                                         # Setup the home joint position
robot.MoveJ(home)                                                    # Move to home in RoboDK
robot.setSpeed(speed_linear=100)                                     # ADJUSTABLE: Change the printing speed here
layer_height = 0.55                                                  # ADJUSTABLE: edit the layer height
path = parser('desired/path/to/gcode') # ADJUSTABLE: Parse the gcode
item_frame = RDK.Item('task_frame')                                  # ADJUSTABLE Load the task_frame from RoboDK
home_joints = [-5.520000, -107.550000, 115.910000, 1.620000,
               37.390000, -0.2400006]                                # ADJUSTABLE Orient robot with joints to P1
robot.setFrame(item_frame)                                           # Set the robot frame
robot.MoveJ(home_joints)                                             # Move to home position (First move must be in joints)


# TOOL ORIENTATION + INVERSE KINEMATICS
orient_frame2tool = invH(item_frame.Pose())*robot.SolveFK(home_joints)  # Homogeneous matrix * joint orientation
orient_frame2tool[0:3, 3] = Mat([0, 0, 0])                              # Remove the last column of homogeneous matrix


# TASK_FRAME CHECK
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)                      # Move to the first corner
robot.MoveL(transl([0, 70, 0])*orient_frame2tool)                     # Move to the second corner
robot.MoveL(transl([70, 70, 0])*orient_frame2tool)                    # Move to the third corner
robot.MoveL(transl([70, 0, 0])*orient_frame2tool)                     # Move to the forth corner
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)                      # Move back to the start


# GET RID OF EXTRA FILAMENT (CAN BE REMOVED)
robot.MoveL(transl([0, 0, 0])*orient_frame2tool)                      # Printing blob
time.sleep(2)                                                         # Used to leave the blob
robot.MoveL(transl([0, 0, 3])*orient_frame2tool)                      # Move up to get rid of the filament 


# PRINTING
RDK.setSimulationSpeed(1)                                             # ADJUSTABLE, set to default speed
printing_status = False                                               # Default value for printing status
for item in path:                                                     # Go through each coordinate from the parsed GCode file
    if item[3] == False and printing_status == True:                  # If we want to stop extrusion which is running right now
        extruder_offline(robot, "STOP")                               # Function to stop extrusion is called
        printing_status = False                                       # Set the printing status to false
    elif item[3] == True and printing_status == False:                # If we want to start printing and we are not
        extruder_offline(robot, "START")                              # Call the function to start extruding
        printing_status = True                                        # Set the printing status to true
    target_point = [item[0], item[1], layer_height*item[2]+0.15]      # ADJSUTABLE, call the coord to go to, 0.55 is the layer heigh
    target0 = transl(target_point)*orient_frame2tool                  # Set the target point with correct rotation of the extruder
    robot.MoveL(target0, blocking=False)                              # Move the robot to target
robot.MoveJ(home)                                                     # Move back home at the end of program