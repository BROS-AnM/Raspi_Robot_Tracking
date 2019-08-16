#Description: will send location data based on image ball tracking
#of green reference ball, blue left ball, and ref right ball.
#location and orientation are sent via TCP to main computer.
#This is a continual loop program and will not end.

import socket
import time
from RobotTrack import *
from client import *

client = client('10.0.0.10', 12345)
robot = RobotTrack()

client.connect()

done = False
wait = time.time()
while done is False:
    p = robot.Robot_position()
    position = '128d' +str(p[0][0]) + 'd' + str(p[0][1]) + 'd' + str(p[1]) + 'd129'
    #For Testing - comment out when not needed
    #print(p)
    #print(position)
    client.sendMessage(position)
    #Can alter the below time limit to extend or shorten the time between pictures taken
    if time.time() > 100 + wait:
        robot.Capture_image()
        wait = time.time()

