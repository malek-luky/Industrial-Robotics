from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# VARIABLE INIT
yellow_lower = (20, 100, 100)  # green lower(29, 86, 6)
yellow_upper = (40, 255, 255)  # green upper (64, 255, 255)
pts = deque(maxlen=20)
cap = cv2.VideoCapture("rolling_ball_challenge.mp4")
cap.set(3, 1280)  # width
cap.set(4, 720)  # height

while True:
    ret, frame = cap.read()
    if frame is None:
        break
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    #  DRAW THE CENTER + RED LINE
    if len(cnts) > 0:
        # find the largest contour in the mask
        # use it to compute the minimum enclosing circle and centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        print(x, y)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        if radius > 10:
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
    pts.appendleft(center)

    # DRAW THE CIRCLES
    for i in range(1, len(pts)):
        if pts[i - 1] is None or pts[i] is None:
            continue
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), 2)

    # SHOW THE IMAGES
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    # PROGRAM TERMINATION
    if key == ord("q"):
        break
    cv2.waitKey(100)

cap.release()
cv2.destroyAllWindows()
