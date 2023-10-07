import cv2
import numpy as np


#######################  Slider  #######################

def callback(res):
	return

def createSlider(R_THRES:int, G_THRES:int, B_THRES:int):
	# create a window
	cv2.namedWindow('Threshold Sliders')
	# create a slider
	cv2.createTrackbar('R', 'Threshold Sliders', R_THRES, 255, callback)
	cv2.createTrackbar('G', 'Threshold Sliders', G_THRES, 255, callback)
	cv2.createTrackbar('B', 'Threshold Sliders', B_THRES, 255, callback)


#######################  Utility  #######################

def put_digit(display, digit:int):
	if(digit == None):
		cv2.putText(display, f"Current Digit: None", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
	else:
		cv2.putText(display, f"Current Digit: {digit}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)



# frame: your frame
# path : your save location path
# mode : 0-> No crop, 1-> Crop
# return the cropped screenshot
def screenshot(frame, path:str, mode:int):
	crop_frame = frame[50:480, 0:640]
	cv2.imwrite(path, crop_frame)				# Screenshot current display
	img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
	if(mode == 1): # Crop
		ret, thresh = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY)
		# Find contours in the binary mask
		contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# Iterate through the contours and find the largest one (assuming the white line is the largest contour)
		largest_contour = max(contours, key=cv2.contourArea)

		# Get the bounding box of the largest contour
		x, y, w, h = cv2.boundingRect(largest_contour)
		center_x = (x + x + w) / 2
		center_y = (y + y + h) / 2
		r = max(w/2, h/2) + 30
		s_x = int(max(0, center_x - r))
		e_x = int(min(480, center_x + r))
		s_y = int(max(50, center_y - r))
		e_y = int(min(640, center_y + r))
		cropped_image = img[s_y:e_y, s_x:e_x]
		cv2.imwrite('./img/cropped_image.jpg', cropped_image)
	return img
