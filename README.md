# KUKA Robot Lab Project

This project was completed during a semester where we had 24/7 access to the KUKA Robot Lab. The tasks we accomplished during this time were coded in Python and executed using an interpreter that converted our commands into the KUKA format that the robot could understand.

## Tasks

1. The first task was to make the robot follow a specified path. To do this, we needed to translate real-world distances into robot coordinates (6 angles for each DOF).

2. We then mounted a camera on the KUKA robot and used it to track a red ball. To accomplish this, we created an algorithm to find the center of the ball, fine-tuned the robot's reachable area so it wouldn't collide with the table below, and finally gave the robot the right coordinates where the ball was located.

3. The semester project was a 3D printing machine. We designed a 3D printer using coordinates from a GCode file for 3D printing. The most challenging part was to move the head at a constant speed because the robot was very fast and didn't follow curves, only the quickest path between points. Therefore, we interpolated longer distances with more points to make the movement much smoother.