import re
import cv2
import numpy as np
from statistics import mean
import math


def move(joint, client):
    string = '{A1 ' + str(list(joint)[0][0]) + ', A2 ' + str(list(joint)[0][1]) + ', A3 ' + str(list(joint)[
        0][2]) + ', A4 ' + str(list(joint)[0][3]) + ', A5 ' + str(list(joint)[0][4]) + ', A6 ' + str(list(joint)[0][5]) + '}'
    client.write('MYAXIS', string)
# https://robodk.com/doc/en/PythonAPI/robolink.html?highlight=joint#robolink.Item.JointLimits


def extruder(client, arg):
    if arg == 'START':
        client.write('$OUT[16]', 'True')
    elif arg == 'STOP':
        client.write('$OUT[16]', 'False')
    else:
        print('The input of extruder() has to be either START or STOP')


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
            # if re.findall("G0", line):  # dont print
            #     coord = re.findall(r'[XY].?\d+.\d+', line)
            #     if len(coord) == 2:
            #         X = re.findall('\d*\.?\d+', coord[0])[0]
            #         Y = re.findall('\d*\.?\d+', coord[1])[0]
            #         parsed_file.append([float(X), float(Y), layer, False])
    return parsed_file


def interpolate(path, detail):
    # Adds extra points in case that Euler distance > 1.45
    extra = 0  # inserted value, colide with indexing
    for i in range(len(path)-1):
        number_of_cuts = int(distance(path[i+extra], path[i+extra+1])//detail)
        if number_of_cuts > 0:
            dist_x, dist_y = distance_x_y(
                path[i+extra], path[i+extra+1], number_of_cuts+1)
            for k in range(number_of_cuts):
                debug = path[i+extra]
                debug2 = path[i+extra+1]
                item = list()
                item.append((k+1)*dist_x + path[i+extra][0])
                item.append((k+1)*dist_y + path[i+extra][1])
                item.append(path[i+extra][2])
                item.append(path[i+extra][3])
                path.insert(i+k+extra+1, item)
        extra += number_of_cuts


def distance(point1, point2):
    # index 0 is X, index 1 is Y
    distance = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    return distance


def distance_x_y(point1, point2, number_of_cuts):
    distance_x = (point2[0] - point1[0])/(number_of_cuts)
    distance_y = (point2[1] - point1[1])/(number_of_cuts)
    return distance_x, distance_y
