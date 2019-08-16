# Robot_Tracking
Hi all,

This is a Raspberry Pi project looked at tracking the position and orientation of a robot (or anything you want really) that is 
confined on a platform. It uses a green reference ball placed as you origin (x,y) psoition, and a red and blue ball for right and 
left respectively. A Raspberry Pi and camera are positioned above the platform with the camera facing vertically down perpendicular 
to the platform.

The programs are broken into 2 classes and a main. Classes are: 
- RobotTracking: Tracks the robot position (x,y) and orientation in degrees using the centre point positions (x,y) of the 
green, red, and blue balls.
- Client: Sets up a TCP client and sends data to the TCP Host (basic of the basics).

The main program just runs to get the position and orientation data and transfer it to the TCP Host. It is a continual loop and needs to be manually stopped.

User Specific Notes:
- The tracking class identifies contours, there is a chance that the balls you use may be too small, if this is the case 
increase their size.
- The tracking class uses HSV masking to seperate the balls from the rest of the image. Ensure that the platform is of a high 
contrasting colour to the balls (I suggest black).
- It is advisable to adjust and test what colour windows are best for identifying the balls you use.
