# VARIABLES
import numpy as np
import cv2
import matplotlib.pyplot as plt

# CONSTANTS
# ============================================================================
AREA_COLOR = (66, 183, 42)
# ============================================================================

def calculate_capacity(frame, frame_number, area_mask, save_image, image_dir):
    # CONVERT TO GRAY IMAGE
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    # ADJUST THE CONTRAST OF THE IMAGE
    cl1 = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)).apply(frame)

    # DETECT AND INVERT THE EDGES
    edges = cv2.Canny(frame,50,70)
    edges = ~edges



    # BLUR AND THRESHOLD
    blur = cv2.blur(edges,(21,21), 100)
    _, threshold = cv2.threshold(blur,230, 255,cv2.THRESH_BINARY)
    
    capacity = [0.0,0.0]

    # - FOR EACH POINT ON THE AREA MASK 
    # - CALCULATE ALL THE NON-ZERO POINTS IN THAT MASK
    # - PERFORM BITWISE_AND TO MAKE ROAD VALUES 255, AND
    #   THE VEHICLES ZERO
    # - CAPACITY = 1 - TOTAL POINTS ON MASK/POINTS NOT COVERED BY VEHICLES
    _1 = None
    _2 = None
    for index, mask in enumerate(area_mask):
        # TOTAL POINTS ON MASK
        non_zero_points = np.count_nonzero(mask)
        # REMOVE VEHICLES FROM THE MASK
        area_mask_removed_vehicles = cv2.bitwise_and(threshold, threshold, mask = mask)

        if index == 0: _1 = area_mask_removed_vehicles
        else: _2 = area_mask_removed_vehicles

        # POINTS NOT COVERED BY VEHICLES
        free = np.count_nonzero(area_mask_removed_vehicles)
        # CALCULATE THE CAPACITY
        capacity[index] = 1 - float(free)/non_zero_points

    if save_image: cv2.imwrite(image_dir + '/processed_'+ str(frame_number) + '.png', _1 | _2)   
    return capacity

def capacity_counter(FRAME_STATS, area_mask, save_image=False, image_dir='./'):
    """
        CALCULATES AND STORES THE CAPACITY IN DICTIONARY
        INPUTS:
        AREA_MASK - THE AREA FOR WHICH CAPACITY IS PROCESSED
    """
    frame = FRAME_STATS['frame'].copy()
    frame_number = FRAME_STATS['frame_number']
    FRAME_STATS['capacity'] = calculate_capacity(frame, frame_number, area_mask, save_image, image_dir)