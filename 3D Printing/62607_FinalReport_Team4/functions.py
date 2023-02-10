import re                                                   #standard library providing regular expression facilities
import math                                                 #standard library providing mathematical operations

def move(joint, client):
    '''converts the output (joint angles) as commands to the robot controller'''
    string = '{A1 ' + str(list(joint)[0][0]) + ', A2 ' + str(list(joint)[0][1]) + ', A3 '\
        + str(list(joint)[0][2]) + ', A4 ' + str(list(joint)[0][3]) + ', A5 '\
        + str(list(joint)[0][4]) + ', A6 ' + str(list(joint)[0][5]) + '}'
    client.write('MYAXIS', string)


def extruder_online(client, arg):
    '''Converts parser's instruction to start/stop extruding to robot controller as ON/OFF on I/O
        and prints the change of extruding state'''
    if arg == 'START':
        client.write('$OUT[16]', 'True')
    elif arg == 'STOP':
        client.write('$OUT[16]', 'False')
    else:
        print('The input of extruder() has to be either START or STOP')


def extruder_offline(robot, arg):
    '''Same as extruder(), just for offline usage '''
    if arg == 'START':
        robot.setDO('$OUT[16]', 'True')
    elif arg == 'STOP':
        robot.setDO('$OUT[16]', 'False')
    else:
        print('The input of extruder() has to be either START or STOP')


def parser(filename):
    '''parse gcode commands to be used in our code'''
    parsed_file = list()                                                    # create a list
    layer = 0                                                               # z-axis, or current height of the print
    with open(filename) as gcode:                                           # open gcode path and use as variable
        for line in gcode:                                                  # for each line in gcode:
            line = line.strip()                                             # delete all unnecessary ASCII characters 
            if re.findall("LAYER:", line):                                  # if new layer found, update z-axes
                layer += 1
                continue                                                    # similar to elif
            if re.findall("G1", line):                                      # check if line begins with "G1"
                coord = re.findall(r'[XY].?\d+.\d+', line)                  # assign coord values
                if len(coord) == 2:                                         # if both coords were assigned
                    X = re.findall('\d*\.?\d+', coord[0])[0]                # assign X-value
                    Y = re.findall('\d*\.?\d+', coord[1])[0]                # assign Y-value
                    parsed_file.append([float(X), float(Y), layer, True])   # append our desired output for use in the project:
    return parsed_file                                                      # return parsed list


def interpolate(path, detail):
    '''Interpolates end-effector's path for smooth and linear velocity.
        Not used, hence not commented.'''
    extra = 0                                                       # inserted value, colide with indexing
    for i in range(len(path)-1):                                    # go through all points
        number_of_cuts = int(distance(path[i+extra], path[i+extra+1])//detail) #calculates how many times we fit distance 1.45
        if number_of_cuts > 0:                                      # interpolate the 2 points only if the distance is > 1.45
            dist_x, dist_y = distance_x_y( 
                path[i+extra], path[i+extra+1], number_of_cuts+1)   # return the distance to be added to each coordinate 
            for k in range(number_of_cuts):                         # for each index k depending on value of number_of_cuts
                item = list()                                       # each iteration create a new list and discard the last
                item.append((k+1)*dist_x + path[i+extra][0])        # append new interpolated x coordinate to the path
                item.append((k+1)*dist_y + path[i+extra][1])        # append new interpolated y coordinate to the path
                item.append(path[i+extra][2])                       # append which lazer it is
                item.append(path[i+extra][3])                       # append the true or false value whether we are extruding
                path.insert(i+k+extra+1, item)                      # insert the created list above to the path on the correct index
        extra += number_of_cuts                                     # store how many items were added for correct indexing


def distance(point1, point2):
    '''computes distance between points for use in interpolate()'''
    # index 0 is X, index 1 is Y
    distance = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2) # calculates the eular distance between 2 points
    return distance


def distance_x_y(point1, point2, number_of_cuts):
    '''return the distance which is added to each points so that the points are equally distanced'''
    distance_x = (point2[0] - point1[0])/(number_of_cuts)       # calculate the distance for x coord depending on number_of_cuts
    distance_y = (point2[1] - point1[1])/(number_of_cuts)       # calculate the distance for y coord depending on number_of_cuts
    return distance_x, distance_y
