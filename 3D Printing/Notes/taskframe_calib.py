RDK.AddFrame("task_frame")
RDK.setPose(transl(100, 200, 300) * rotz(pi/2))
task_frame = RDK.Item('task_frame')
robot.setPoseFrame(task_frame)  # Use the robot task_frame as active reference


# Specify the pose (position with respect to the reference frame):
target.setPose(KUKA_2_Pose([x, y, z, w, p, r]))
# Add a new movement instruction linked to that target:
program.MoveJ(target)


# Run on robot: Force the program to run on the connected robot (same behavior as right clicking the program, then, selecting "Run on Robot")
# RDK.setRunMode(RUNMODE_RUN_ROBOT)

# Get the main/only robot in the station
robot = RDK.Item('', ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("Robot not valid or not available")

# Get the active reference frame
frame = robot.getLink(ITEM_TYPE_FRAME)
if not frame.Valid():
    frame = robot.Parent()
    robot.setPoseFrame(frame)

# Get the reference pose with respect to the robot
frame_pose = robot.PoseFrame()

# Get the active tool
tool = robot.getLink(ITEM_TYPE_TOOL)
if not tool.Valid():
    tool = robot.AddTool(transl(0, 0, 75), "Tool Grid")
    robot.setPoseTool(tool)

# Get the target reference RefTarget
target_ref = RDK.Item(REFERENCE_TARGET, ITEM_TYPE_TARGET)
if not target_ref.Valid():
    target_ref = RDK.AddTarget(REFERENCE_TARGET, frame, robot)

# Get the reference position (pose=4x4 matrix of the target with respect to the reference frame)
pose_ref = target_ref.Pose()
startpoint = target_ref.Joints()
config_ref = robot.JointsConfig(startpoint)

# Retrieve the tool pose
tool_pose = tool.PoseTool()

# Retrieve the degrees of freedom or axes (num_dofs = 6 for a 6 axis robot)
num_dofs = len(robot.JointsHome().list())

# Get the reference frame of the target reference
ref_frame = target_ref.Parent()
