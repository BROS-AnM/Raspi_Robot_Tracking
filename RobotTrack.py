from picamera.array import PiRGBArray
from picamera import PiCamera
from collections import deque
import numpy as np
import time
import cv2
import imutils
import os
import sys

class RobotTrack:
	def __init__(self):
		# 1. Initialise
		self.flag = True
		#Set buffer size for automatically to 64
		self.buffer = 64
		#Set Lower & upper limits for green, blue, and red for HSV colour space
		self.greenLower = (30, 70, 10)
		self.greenUpper = (70, 255, 255)
		self.blueLower = (95, 113, 45)
		self.blueUpper = (135, 255, 255)
		self.redLower = (0, 100, 20)
		self.redUpper = (10, 255, 255)
		#Initialise the list of tracked points
		zeroArray = [0, 0]
		self.ptsg = deque(maxlen = self.buffer)
		self.ptsg.appendleft(zeroArray)
		self.ptsb = deque(maxlen = self.buffer)
		self.ptsb.appendleft(zeroArray)
		self.ptsr = deque(maxlen = self.buffer)
		self.ptsr.appendleft(zeroArray)
		self.ptcp = deque(maxlen = self.buffer)
		self.ptcp.appendleft(zeroArray)
		self.ptan = deque(maxlen = self.buffer)
		self.ptan.appendleft(zeroArray)
		#initialize the camera and grab a reference to the raw camera capture
		self.camera = PiCamera()
		self.camera.resolution = (640, 480)
		self.camera.framerate = 32
		self.rawCapture = PiRGBArray(self.camera, size=(640,480))
		#Allow camera to warmup
		time.sleep(2.0)
		#Make folder to log pictures
		timestr = time.strftime("%Y%m%d-%H%M%S")
		self.path = os.path.join("./CameraLog_", timestr)
		os.makedirs(self.path)
		self.savecount = 0

	def Robot_position(self):
		# 2. ROBOT (X,Y) POSITION & ORIENTATION
		self.rawCapture.truncate(0)
		#Messy need to alter but working regardless
		for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port = False):
			#Grab raw numpy array of image, initialize timestamp & occupied/unoccupied text
			self.image = frame.array
			#If no image end program
			if self.image is None:
				return
			self.rawCapture.truncate(0)
			break
		#If there is an image resize and blur and convert to HSV
		self.image = imutils.resize(self.image, width = 600)
		blurred = cv2.GaussianBlur(self.image, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
		#Mask for green, blue, & red
		maskg = cv2.inRange(hsv, self.greenLower, self.greenUpper)
		maskb = cv2.inRange(hsv, self.blueLower, self.blueUpper)
		maskr = cv2.inRange(hsv, self.redLower, self.redUpper)
		#erode and dilate iteratively to remove noise from image
		maskg = cv2.erode(maskg, None, iterations = 2)
		maskb = cv2.erode(maskb, None, iterations = 2)
		maskr = cv2.erode(maskr, None, iterations = 2)
		maskg = cv2.dilate(maskg, None, iterations = 2)
		maskb = cv2.dilate(maskb, None, iterations = 2)
		maskr = cv2.dilate(maskr, None, iterations = 2)
		#find contours in masks
		cntsg = cv2.findContours(maskg.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsg = cntsg[0] if imutils.is_cv2() else cntsg[1]
		cntsb = cv2.findContours(maskb.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsb = cntsb[0] if imutils.is_cv2() else cntsb[1]
		cntsr = cv2.findContours(maskr.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cntsr = cntsr[0] if imutils.is_cv2() else cntsr[1]
		#Only proceed if at least one contour for each colour was found
		if len(cntsg) > 0 and len(cntsb) > 0 and len(cntsr) > 0:
			#find largest contour in mask
			cg = max(cntsg, key = cv2.contourArea)
			cb = max(cntsb, key = cv2.contourArea)
			cr = max(cntsr, key = cv2.contourArea)
			#compute minimum enclosing circle
			((xg, yg), radiusg) = cv2.minEnclosingCircle(cg)
			((xb, yb), radiusb) = cv2.minEnclosingCircle(cb)
			((xr, yr), radiusr) = cv2.minEnclosingCircle(cr)
			#Compute centers from moments
			Mg = cv2.moments(cg)
			Mb = cv2.moments(cb)
			Mr = cv2.moments(cr)
			centerg = (int(Mg["m10"] / Mg["m00"]), int(Mg["m01"] / Mg["m00"]))
			centerb = (int(Mb["m10"] / Mb["m00"]), int(Mb["m01"] / Mb["m00"]))
			centerr = (int(Mr["m10"] / Mr["m00"]), int(Mr["m01"] / Mr["m00"]))
		else:
			print("No contours detected for either green, blue, or red")
			print("using last known positions")
			centerg = self.ptsg[0]
			centerb = self.ptsb[0]
			centerr = self.ptsr[0]
			#For Testing - Comment out when not needed.
			#print(centerg,centerb,centerr,"\n")
			(xg, yg) = centerg
			(xb, yb) = centerb
			(xr, yr) = centerr
		#update the points in the queue
		self.ptsg.appendleft(centerg)
		self.ptsb.appendleft(centerb)
		self.ptsr.appendleft(centerr)
		#Measure distance between red & blue referenced to green & robot angle
		angle = np.arctan2(yr-yb,xr-xb) * 100 / np.pi #robot angle
		Cp = [0, 0]
		Cp[0] = xb + 0.5 * (xr - xb) #x-position
		Cp[1] = yb + 0.5 * (yr - yb) #y-position
		#Add relevant values to dequeue buffer
		self.ptcp.appendleft(Cp)
		self.ptan.appendleft(angle)
		self.rawCapture.truncate(0)
		return(Cp, angle)


	def Capture_image(self):
		cv2.imshow("Frame", self.image)
		cv2.imwrite(self.path + "/(" + str(self.savecount) + ").png", self.image)
		self.savecount += 1
		self.rawCapture.truncate(0)

	def Destroy_Window(self):
		cv2.destroyAllWindows()
		self.savecount = 0
