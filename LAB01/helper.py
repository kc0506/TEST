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

