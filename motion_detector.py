from imutils.video import VideoStream
import argparse
import imutils
import time
from time import sleep
import cv2
import serial

# helpers
def communication(cPosition, middleOfAxis, axis):
        difference = cPosition-middleOfAxis
        side = "+"
        if difference < 0: side = "-"
        print(axis + " " + side)
        ser.write(b'/')
        difference = abs(difference)
        ser.write(side.encode())
        ser.write(b'%d' %len(str(difference)))
        ser.write(b'%d' %difference)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-x", "--resolution-x", type=int, default=1184, help="x resolution")
ap.add_argument("-y", "--resolution-y", type=int, default=720, help="y resolution")
ap.add_argument("-a", "--min-area", type=int, default=4000, help="minimum area size")
args = vars(ap.parse_args())

# if the video argument is None, use camera stream
if args.get("video", None) is None:
        vs = VideoStream(usePiCamera=True, resolution=(args["resolution_x"], args["resolution_y"]), framerate=15).start()
        time.sleep(2.0)
 
# otherwise, read from video file
else:
        vs = cv2.VideoCapture(args["video"])


# try to initialize connection with arduino
for i in range(4):
        channel = "/dev/ttyACM" + str(i)
        try:
          ser=serial.Serial(channel,9600)
        except:
                continue
        else:
                break

ser.baudrate=9600

# Define center of out frame - for later computing of pixel difference/distance
xMiddle = 329
yMiddle = 200

# loop over the frames of the video
while True:
        # initialize the first frame in the video stream
        firstFrame = None
        iterations = 0
        for i in range(2):
                # grab the current frame and initialize
                frame = vs.read()
                frame = frame if args.get("video", None) is None else frame[1]
         
                # if the frame could not be grabbed, then we have reached the end
                # of the video
                if frame is None:
                        break
         
                # resize the frame, convert it to grayscale, and blur it
                frame = imutils.resize(frame, width=658)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
         
                # if the first frame is None, initialize it
                if firstFrame is None:
                        firstFrame = gray
                        continue
                # compute the absolute difference between the current frame and
                # first frame
                frameDelta = cv2.absdiff(firstFrame, gray)
                thresh = cv2.threshold(frameDelta, 40, 255, cv2.THRESH_BINARY)[1]
         
                # dilate the thresholded image to fill in holes, then find contours
                # on thresholded image
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
         
                # loop over the contours
                biggestContourArea = 0
                indexOfBiggest = 0
                motion = False
                for c in cnts:
                        # if the contour is too small, than defined min_area, ignore it
                        # or in scenarior when we want to make an assumption that a biggest motion is the target
                        # for a better performance - ignore it aswell
                        contourArea = cv2.contourArea(c)
                        if contourArea < args["min_area"]:
                                continue
                        if contourArea > biggestContourArea:
                                motion = True
                                biggestContourArea = contourArea
                                indexOfBiggest = c
                if motion == True:
                        # show the frame and record if the user presses a key
                        # shows where barrel of the gun is --> always middle of the frame
                        iterations += 1
                        cv2.circle(frame,(xMiddle, yMiddle), 2, (0,0,255), -1)
                        cv2.circle(frame,(xMiddle, yMiddle), 10, (0,0,255))
                        (x, y, w, h) = cv2.boundingRect(indexOfBiggest)
                        M = cv2.moments(indexOfBiggest)
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        # center of the moving object
                        cv2.circle(frame,(cX, cY), 2, (0,255,0), -1)
                        # allowed to shoot area
                        cv2.circle(frame,(cX, cY), 10, (0,255,0))
                        # borders of the motion and coordinates of its center
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, "X coordinates: {}".format(cX), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        cv2.putText(frame, "Y coordinates: {}".format(cY), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.imshow("Frame Delta", frameDelta)
                cv2.imshow("Thresh", thresh)
                cv2.imshow("Main Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if iterations == 1:
                        print(cX-xMiddle)
                        print(cY-yMiddle)
                        communication(cX, xMiddle, "x")
                        communication(cY, yMiddle, "y")
                        while True:
                                frame = vs.read()
                                frame = imutils.resize(frame, width=658)
                                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                                cv2.circle(frame,(cX, cY), 2, (0,255,0), -1)
                                cv2.circle(frame,(cX, cY), 10, (0,255,0))
                                cv2.circle(frame,(xMiddle, yMiddle), 2, (0,0,255), -1)
                                cv2.circle(frame,(xMiddle, yMiddle), 10, (0,0,255))
                                cv2.imshow("Main Frame", frame)
                                key = cv2.waitKey(1) & 0xFF
                                if key == ord("c") or key == ord("q"):
                                        break

                # if the `q` key is pressed, break from the loop
                if key == ord("q"):
                        break
        if key == ord("q"):
                break

# cleanup the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()
