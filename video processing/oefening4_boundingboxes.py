import cv2
import numpy as np

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(0)

fgbg = cv2.createBackgroundSubtractorMOG2(history=100)

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:

    frame = cv2.resize(frame, (320, 240))

    fgmask = fgbg.apply(frame)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    contours, hierarchy = cv2.findContours(fgmask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
      area = cv2.contourArea(cnt)
      if area>100:
        image = cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)

        x,y,w,h = cv2.boundingRect(cnt)
        box = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    
    # Display the resulting frame
    cv2.imshow('Frame',image)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

  # Break the loop
  else: 
    break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
