import cv2
import numpy as np

from helper import *
from digit_recognization import *


#######################  Constant  #######################

CAMERA = 0

# FILEPATH
DIGIT_IMG = "./img/digit.png"

# List to store positions
positions = []

# BOOLEAN
FLIP_HORIZONTAL = True 		# Flag to control horizontal flip


# THRESHOLD
AREA_THRES  = 100
R_THRES 	= 200
G_THRES		= 0
B_THRES		= 130

# FINGER RECOGNIZATION
VANISH_COOLDOWN = 20         	# If no contour has been detected within cooldown, input is finished
IS_DRAWING      = False      	# Determine the trail is availale or not 
COLOR = [(255,0,0), (0,255,0)]
finger_pos = [
	(-1, -1),			# Finger 1 pos
	(-1, -1),			# Finger 2 pos
]
trails = {				# Store 2 fingers' tracks respectively
	0: [],
	1: []
}

#######################  Function  #######################





#######################  Main      #######################

if __name__ == "__main__":

	cap = cv2.VideoCapture(CAMERA)
	createSlider(R_THRES, G_THRES, B_THRES)
	CLF_MODEL = train_model()					# Get Model

	cooldown = VANISH_COOLDOWN

	while(True):
		# Get one frame from the camera
		ret, frame = cap.read()

		#print(f"cooldown: {cooldown}, len(pos):{len(positions)}")

		# Check if horizontal flip is enabled
		if FLIP_HORIZONTAL:
			frame = cv2.flip(frame, 1)

		# Split RGB channels
		try:
			# Split RGB channels
			b, g, r = cv2.split(frame)
		except:
			continue

		# Perform thresholding to each channel
		r_thres = cv2.getTrackbarPos('R', 'Threshold Sliders')
		g_thres = cv2.getTrackbarPos('G', 'Threshold Sliders')
		b_thres = cv2.getTrackbarPos('B', 'Threshold Sliders')
		_, r = cv2.threshold(r, r_thres, 255, cv2.THRESH_BINARY)
		_, g = cv2.threshold(g, g_thres, 255, cv2.THRESH_BINARY)
		_, b = cv2.threshold(b, b_thres, 255, cv2.THRESH_BINARY)

		# Get the final result using bitwise operation
		not_b = cv2.bitwise_not(b, mask=None)
		result = cv2.bitwise_and(r, not_b, mask = None)

		# Find and draw contours
		contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		display = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
		cv2.drawContours(display, contours, -1, (0,0,255))


		# Iterate through each contour, check the area and find the center
		# Get Valid Contours
		valid_contours = []
		for cnt in contours:
			area = cv2.contourArea(cnt)
			if area > AREA_THRES:
				valid_contours.append(cnt)

		if len(valid_contours) == 0:		# No input
			cooldown -= 1
		else:
			cooldown = VANISH_COOLDOWN
			for cnt in valid_contours:
				# Calculate the area of the contour
				# Find the centroid
				(x,y), radius = cv2.minEnclosingCircle(cnt)
				center = (int(x), int(y))
				radius = int(radius)

				# Determine which finger id is this contour depend on the distance to to prev location
				print(f"finger 0: {finger_pos[0]}")
				print(f"finger 1: {finger_pos[1]}")
				if IS_DRAWING == False:
					if finger_pos[0][0] != -1 and finger_pos[1][0] != -1:
						print(f"2 finger ready !")
						IS_DRAWING = True
						continue
					elif finger_pos[0][0] == -1:
						id = 0
						finger_pos[0] = center
						trails[0].append(center)
					else:
						dist = get_euclidean_distance(center, finger_pos[0])   		# Heuristic : locate only if 2nd finger is far enough
						print(f"2nd finger dist: {dist}")
						if dist >= 200:
							id = 1
							finger_pos[1] = center
							trails[1].append(center)
				else:
					id = -1
					min_dist = 99999999
					for idx, pos in enumerate(finger_pos):
						dist = get_euclidean_distance(center, pos)
						if dist < min_dist:
							min_dist = dist
							id = idx

 
				cv2.circle(display, center, radius, COLOR[id], 2)
				cv2.circle(display, center, 2, COLOR[id], -1)
				cv2.putText(display, f"Finger {id}", (center[0]+radius, center[1]+radius), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR[id], 2)

				# Add the object's position to the history list
				if(IS_DRAWING):
					trails[id].append(center)
				# Update prev finger position
				finger_pos[id] = center


		# Draw the object's trajectory
		if IS_DRAWING:
			for i in range(2):
				trail = trails[i]
				for j in range(1, len(trail)):
					cv2.line(display, trail[j - 1], trail[j], COLOR[i], 20)

		# Show the frame
		cv2.imshow('frame', frame)
		cv2.imshow("display", display)
		
		# Input is ready
		if cooldown <= 0:
			if len(trails[0]) != 0 or len(trails[1]) != 0:
				IS_DRAWING = False						# Set Flag
				trails[0] = []							# Clear the trail
				trails[1] = []							
				finger_pos[0] = (-1, -1)                # Clear the position
				finger_pos[1] = (-1, -1)
			cooldown = VANISH_COOLDOWN					# Reset CoolDown

		#* Press h to toggle horizontal flip
		#* Press c to clear
		#* Press q to quit
		key = cv2.waitKey(1) & 0xFF
		if key == ord('h'):
			FLIP_HORIZONTAL = not FLIP_HORIZONTAL
		elif key == ord('c'):
			IS_DRAWING = False
			trails[0] = []							# Clear the position
			trails[1] = []							# Clear the position
			finger_pos[0] = (-1, -1)                # Clear the position
			finger_pos[1] = (-1, -1)
		elif key == ord('q'):
			break

	cap.release()
	cv2.destroyAllWindows()