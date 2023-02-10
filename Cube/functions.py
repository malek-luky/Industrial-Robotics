# SHOULD BE WORKING WITHOUT RUNNING THE ROBODK SIMULATION
def move_inverse(robot, pose, client):
    joint = robot.SolveIK(pose)
    string = '{A1 ' + str(list(joint)[0][0]) + ',A2 ' + str(list(joint)[0][1]) + ',A3 ' + str(list(joint)[
        0][2]) + ', A4 ' + str(list(joint)[0][3]) + ',A5 ' + str(list(joint)[0][4]) + ', A6 ' + str(list(joint)[0][5]) + '}'
    print('HERE: MYAXIS', string)
    client.write('MYAXIS', string)
    # https://robodk.com/doc/en/PythonAPI/robolink.html?highlight=joint#robolink.Item.JointLimits


def move(joint, client):
    string = '{A1 ' + str(list(joint)[0][0]) + ', A2 ' + str(list(joint)[0][1]) + ', A3 ' + str(list(joint)[
        0][2]) + ', A4 ' + str(list(joint)[0][3]) + ', A5 ' + str(list(joint)[0][4]) + ', A6 ' + str(list(joint)[0][5]) + '}'
    client.write('MYAXIS', string)
# https://robodk.com/doc/en/PythonAPI/robolink.html?highlight=joint#robolink.Item.JointLimits
