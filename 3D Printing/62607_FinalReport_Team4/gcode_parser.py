#----------------------------------------------------------------------
# This code parses the information from a .gcode file sliced using 
# Ultimaker cura.
#
# By Group 2 of 62607 - Applied Industrial Robotics - Winter 2021
# ---------------------------------------------------------------------

import os
import numpy as np                               # for array definition
import re           # regular expression(re) checking to read the Gcode
import tkinter as tk                        # tkinter for the basic GUI
from tkinter import filedialog as fd
              # filedialog from tkinter to open the file browser window
from robolink import *                                     # RoboDK API
from robodk import *                                    # Robot toolbox
              
class BrowseButton:
        def __init__(self):
            self.browse_button = tk.Button(root,text='Browse',
                command=self.save_gcode_path).grid(row=1, 
                column=3,sticky=tk.W,pady=4)
        def save_gcode_path(self):
                filetypes = (
                ('G-Code files', '*.gcode'),
                ('All files', '*.*'))
                self.path = fd.askopenfile(initialdir=os.getcwd(), title=
                                           'Select file', filetypes=
                                           filetypes).name
                e2.delete(0, 'end')
                if self.path:
                        e2.insert(0, self.path)

# Define the re pattern that is used to find the coordinates from the 
# gcode lines, such that every number following the letters 'G', 'X', 
# 'Y' and 'Z' are included.
RE_ARG = re.compile(r"[GXYZ]\d+[.]?\d*")

def get_pos_from_line(line):
    
    """Extracts the correct and complete coordinates and the state of 
    the extruder according to the current line of gcode.

    Returns:
        np.array, np.bool: position vector with position from the line,
                           4x1 bool vector containing whether a 
                           coordinate is valid or not
    """
    # Initialisation of arrays for storage of the returns.
    pos = np.zeros((4, 1))
    pos_valid = np.zeros((4, 1), dtype=np.bool_)
    
    # Dictionary to define which letter is followed by which position
    # it belongs to.
    COORD_DICT = {'G': 0, 'X': 1, 'Y': 2, 'Z': 3}
      
    # Checking whether each element i of line mathces RE_ARG and
    # if its updated by the gcode or not.                                                         
    if 'G' in line[0][0]:
        for i in line:
            if RE_ARG.match(i) is not None:
                pos[COORD_DICT[i[0]]] = float(i[1:])
                pos_valid[COORD_DICT[i[0]]] = True
    return pos, pos_valid
            

def calc_new_pos(last_pos, line):
    
    """calculates new position from the old position and the given
    gcode line.

    Returns:
        np.array: contains the new position
    """
    
    # Retrive the new position and the valid array from 
    # get_pos_from_line()
    pos_cmd, pos_cmd_valid = get_pos_from_line(line)
    
    new_pos = np.zeros((4, 1))  # Initialise array to store the pos.
    last_pos[pos_cmd_valid] = 0 # Set all valid positions to zero.
    
    # Add the new valid positions to the old position, where the valid
    # positions have be set to zero.
    new_pos = last_pos + pos_cmd

    return new_pos  # return the new calculated position as np.array

def gcode_to_list(gcode):
    
    """Extracts all coordinates contained in a .gcode file such that
    either a 0 or 1 to indicate whether extrusion is supposed to happen
    or not, is followed by xyz-coordinates.

    Returns:
        list of lists: contains all important information for the KUKA
    """
    
    # Open the .gcode file as gc and read the lines to use 
    # calc_new_pos() on each line.
    with open(gcode, 'r') as gc:
        
        # Read all the lines in a list of list.
        gc = [re.findall(RE_ARG, l) for l in gc.readlines()]
        
        # Filter out all empty elements of the list.
        gc = list(filter(None, gc))
    
        positions = []
        
        # Calculate first position and append it to 'positions'.
        last_pos = calc_new_pos(np.zeros((4, 1)), gc[0])             
        positions.append([item for sublist in last_pos.tolist()
                      for item in sublist])

        # Iterate through the rest of the lines from the gcode and
        # calculate the new position to append it to 'positions'.
        for i in gc[1:]:
            last_pos = calc_new_pos(last_pos,i)
            positions.append([item for sublist in last_pos.tolist()
                          for item in sublist])
            
    return positions    # return the positions list

def save_file_name():
    global file_name
    file_name = e1.get()
    root.destroy()


# Open a root window for the basic GUI using tkinter
root = tk.Tk()
root.geometry('500x200')
root.title('Create KUKA file from G-Code')
tk.Label(root, text="KUKA file Name").grid(row=0)
tk.Label(root, text="G-Code").grid(row=1)

# Establish entry boxes of width 50.
e1 = tk.Entry(root, width=50)
e2 = tk.Entry(root, width=50)
e1.grid(row=0, column=1)
e2.grid(row=1, column=1)

# Initialise the 'Cancel' Button in the window.
tk.Button(root, text='Cancel', command=root.quit).grid(row=3,
        column=1, sticky=tk.W, pady=4)

# Create object of class BrowseButton(), which then has path attribute.
browse = BrowseButton()

# Initialise the 'Create *.src file' Button in the window.
tk.Button(root, text='Create *.src file', command=save_file_name).grid(row=0, 
        column=3, sticky=tk.W, pady=4)

# mainloop() of the tkinter interface.
tk.mainloop()

# Check if the BrowseButton object has a 'path' attribute.
if hasattr(browse, 'path'):
    # Check if the attribute actually contains anything.
    if browse.path:
        p_Code = gcode_to_list(browse.path) # call on path
    else: 
        # If the path does not contain anything, an example is used.
        print('No File selected, an example is now being used.')
        p_Code = gcode_to_list('Final Assignment\\UM3E_3DBenchy.gcode')
else:
    # If the path does not exist, an example is used.
    print('No File selected, an example is now being used.')
    p_Code = gcode_to_list('Final Assignment\\UM3E_3DBenchy.gcode')
    
# Check is the file has been given a name, and otherwise call it 
# 'myfile'.
if not file_name:
    print('No File Name given, the default is: "myfile.src"')
    file_name = 'myfile.src'

# If the .src ending is not contained in the file name already it is
# added here.
if '.src' not in file_name:
    file_name = file_name + '.src'
#----------------------------------------------------------------------
# RoboDK stuff:

# Creation of the Robolink() object 'RDK'
RDK = Robolink()

# Define which robot is being used
robot = RDK.Item('KUKA KR 6 R700 sixx')


# set the home position of the robot
robot.setJoints([0.000000, -90.000000, 90.000000,
                 0.000000, 45.000000, 0.000000])


home = robot.Joints()   # save the home position
pose = robot.Pose()

# Move to all the extruding coordinated in the simulation for a
# clearer visual of the path in RoboDK. The actual path will include 
# waiting positions G0 from the gcode.
for i in p_Code:
    if i[0]:
        pos = [i[1], i[2], i[3]]
        pose.setPos(pos)      
        robot.MoveJ(pose)

robot.MoveJ(home)

# Open a new file with the name file_name in order to write the KRL
# script into, as my_file.
with open(os.getcwd()+file_name + file_name,
          'w') as my_file:
    # Write the header into the file.
    my_file.write(
        'DEF ' + file_name.replace('.src','') + ' ( )\n'
        '\n'
        ';FOLD INI;%{PE}\n'
        ';FOLD BASISTECH INI\n'
        'GLOBAL INTERRUPT DECL 3 WHEN $STOPMESS==TRUE DO IR_STOPM ( )\n'
        'INTERRUPT ON 3 \n'
        'BAS (#INITMOV,0 )\n'
        ';ENDFOLD (BASISTECH INI)\n'
        ';FOLD USER INI\n'
        ';ENDFOLD (USER INI)\n'
        ';ENDFOLD (INI)\n'
        '\n'
        '$ADVANCE=12'
        '\n'
        '$OUT[16]=FALSE\n'
        ';FOLD PTP HOME  Vel= 100% DEFAULT\n'
        '$BWDSTART= FALSE\n'
        'FDAT_ACT= {TOOL_NO 11, BASE_NO 1, IPO_FRAME #BASE}\n'
        'BAS(#PTP_PARAMS,100 )\n'
        '$H_POS=XHOME\n'
        'PTP XHOME\n'
        ';ENDFOLD\n'
        '\n'
        'PTP {X ' + str(p_Code[1][1]) + ',Y ' + str(p_Code[1][2]) + ',Z '
        + str(p_Code[1][3]+20) + ',A 0,B 135,C 0}\n'
        '$VEL.CP = 0.07\n'
    )
    
    my_file.write('WAIT FOR ($IN[10])\n'    # wait for
                              # the hotend to heat up and start the 
                              # extrusion.
                  '$OUT[16]=TRUE\n' # Start the extrusion.
                 )
    
    extruding = 0   # Establish a variable, to check whether extrusion
                    # is happening or not.
                    
    for i in p_Code:    # Iterate through the positions list of lists
        if i[0] == 1:   # If extrusion should happen
            
            # Write the according line for a liner move to the next
            # postition into the .src file.    
            my_file.write('LIN {X '+str(i[1])+',Y '+str(i[2])+',Z '
                          + str(i[3])+'} C_VEL\n')  # C_VEL inter-
                # polates for constand velocity, while C_DIS tries
                # to achieve eqal distance between path points
    my_file.write('$OUT[16]=FALSE\n'
                  'PTP XHOME\n'
                  'END')
    
print('Done')