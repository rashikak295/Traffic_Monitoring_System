# IMPORTS
import os
import random
import numpy as np
import skvideo.io
import cv2
import matplotlib.pyplot as plt
from contour_detection import *
from vehicle_counter import *
from visualizer import *
from capacity_counter import *
from csv_writer import *
import time

# VARIABLES
cv2.ocl.setUseOpenCL(False)
random.seed(123)

# CONSTANTS
# ============================================================================
IMAGE_DIR = "./out"
CAPACITY_DIR = "./capacity"
COUNT_DIR = "./traffic-count"
VIDEO_SOURCE = "input.mp4"
SHAPE = (720, 1280)
EXIT_PTS = np.array([[[732, 720], [732, 590], [1280, 500], [1280, 720]], \
                     [[0, 400],[645, 400], [645, 0], [0, 0]]])
EXIT_COLOR = (66, 183, 42)
AREA_PTS = [np.array([[0, 720], [0, 613], [422, 353], [591, 372], [495, 720]]),\
            np.array([[780, 716], [686, 373], [883, 383], [1280, 636], [1280, 720]])] 
# ============================================================================

def background_sub_training(background_subtractor, frames_generator, number_of_frames=500):
   """
     USE FIRST 500 FRAMES TO COMPUTE THE BACKGROUND IMAGE
     BACKGROUND_SUBTRACTOR OBJECT IS USED TO DO THAT        
   """
   print ('Training Background Subtractor...')
   i = 0
   for frame in frames_generator:
      out = background_subtractor.apply(frame, None, LEARNING_RATE)
      i += 1
      if i >= number_of_frames:
         return frames_generator

def main():
	"""
	FOR EACH FRAME, 
	CALL CONTOUR DETECTION, VEHICLE COUNTER, COUNTOR DETECTION, VISUALIZER AND 
	CSV WRITER

	BEFORE PROCESSING FRAMES,
	1) GENERATE THE EXITS_MASKS FOR COUNTING VEHICLES
	2) GENERATE THE AREA_MASKS FOR COUNTING DENSITIES
	3) TRAIN THE BACKGROUND SUBTRACTOR AND GET THE BACKGROUND IMAGE
	"""
	# GENERATE A BASE NUMPY ARRAY WITH SIZE (720,1280)
	# GENERATE EXIT MASK USING THE BASE SKELETON FOR COUNTING VEHICELS
	base = np.zeros(SHAPE, dtype='uint8')
	exit_mask = cv2.fillPoly(base, EXIT_PTS, (255, 255))

	# GENERATE A BASE NUMPY ARRAY WITH SIZE (720,1280)
	# GENERATE AREA MASKS USING THE BASE SKELETON FOR COUNTING DENSITY
	base = np.zeros(SHAPE, dtype='uint8')
	area_mask_i = cv2.fillPoly(base, [AREA_PTS[0]], (255, 255))
	base = np.zeros(SHAPE, dtype='uint8')
	area_mask_ii = cv2.fillPoly(base, [AREA_PTS[1]], (255, 255))
	area_mask = [area_mask_i,area_mask_ii]

	# USE THE CV2 MODULE TO GENERATE BACKGROUND_SUBTRACTOR OBJECT
	background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, detectShadows=True)

	# USE SCIKIT-VIDEO PACKAGE TO CAPTURE THE FRAMES AND GENERATE A
	# GENERATOR OBJECT
	frames_generator = skvideo.io.vreader(VIDEO_SOURCE)
	# TRAIN THE BACKGROUND_SUBTRACTOR OBJECT ON 500 FRAMES
	background_sub_training(background_subtractor, frames_generator, number_of_frames=500)
	# GETS THE BACKGROUND IMAGE TRAINED BY BACKGORUND SUBSTRACTOR
	background_subtractor_img = background_subtractor.getBackgroundImage()

	# GENERATE THE FRAME_STATS DICTIONARY THAT STORES THE VALUES ACROSS 
	# ALL THE FRAMES
	FRAME_STATS ={
				'vehicle_count': [0,0],\
				'frame_vehicle_count': [0,0],\
				'frame': None,\
				'frame_number': None,\
				'paths':[],\
				'vehicles':[]
				}

	# FRAME NUMBER COUNTS
	# frame_number_i is used for skipping even frames
	# frame_number_ii stores the total processed frames
	frame_number_i = -1 
	frame_number_ii = -1


	for frame in frames_generator:
		if not frame.any():
			print("Frame capture failed, stopping...")
			break
		# SKIP EVEN FRAMES
		frame_number_i += 1
		if frame_number_i % 2 != 0:
			continue
		frame_number_ii += 1

		# UPDATE THE FRAME_STATS DICTIONARY
		FRAME_STATS['frame'] = frame

		FRAME_STATS['frame_number'] = frame_number_ii
		FRAME_STATS['frame_vehicle_count'] = [0,0]
		contour_detection(FRAME_STATS, background_subtractor=background_subtractor,\
		                         save_image=True, image_dir=COUNT_DIR)
		vehicle_counter(FRAME_STATS, exit_masks=[exit_mask], y_weight=2.0)
		capacity_counter(FRAME_STATS, area_mask, save_image=True, image_dir=CAPACITY_DIR)
		visualizer(FRAME_STATS, image_dir=IMAGE_DIR)
		csv_writer(FRAME_STATS)

		print(time.asctime(time.localtime(time.time())))
		print("Frame number: "+str(frame_number_i))


if __name__ == "__main__":
   if not os.path.exists(IMAGE_DIR):
      print("Creating image directory `%s`...", IMAGE_DIR)
      os.makedirs(IMAGE_DIR)
   main()