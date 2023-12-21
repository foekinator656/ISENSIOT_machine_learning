import cv2
import numpy as np

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture('Robot_hd.mp4')

template = cv2.imread('Robot_templateV3.PNG', 0)
print(template.shape)
w, h = template.shape[::-1]
print(w)




# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video stream or file")
method = eval('cv2.TM_CCOEFF_NORMED')
# Read until video is completed
while (cap.isOpened()):
    # Capture frame-by-frame
    ret, frame = cap.read()
    print(frame.shape)
    if ret == True:

        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        # De maat van het object in de template dat je wilt tracken uitgedrukt in pixels moet in het geschaalde frame
        # ongeveer hetzelfde zijn.
        frameHeight = frame.shape[0] #1080
        frameWidth = frame.shape[1] #1920
        # schaal instellen zodat de maat van het object in de template klopt met het object in het frame.
        scale = 0.475
        frame = cv2.resize(frame, (int(frameWidth*scale), int(frameHeight*scale)))


        res = cv2.matchTemplate(frame, template, method)

        maxv = np.max(res)
        if maxv > 0.60:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(frame, top_left, bottom_right, 255, 2)

            template = frame[top_left[1]:top_left[1] + h, top_left[0]:top_left[0] + w]

        # Display the resulting frame
        cv2.imshow('Frame', frame)
        # cv2.imshow('Frame', template)
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
