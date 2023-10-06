import cv2
import numpy as np

def callback(res):
	return

def createSlider(R_THRES, G_THRES, B_THRES):
	# create a window
	cv2.namedWindow('Threshold Sliders')
	# create a slider
	cv2.createTrackbar('R', 'Threshold Sliders', R_THRES, 255, callback)
	cv2.createTrackbar('G', 'Threshold Sliders', G_THRES, 255, callback)
	cv2.createTrackbar('B', 'Threshold Sliders', B_THRES, 255, callback)