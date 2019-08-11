# IMPORTS
import os
import logging
import csv
import numpy as np
import cv2

# CONSTANTS
# ============================================================================
LEARNING_RATE = 0.001
centroid = lambda x,y,w,h:(x+int(w/2), y+int(h/2))
# ============================================================================

def morph_mask(mask):
    """
        1) GENERATE THE KERNEL FOR MORPHOLOGICAL OPERATIONS
        2) MORPHOLOGYEX CLOSING - DILATION FOLLOWED BY EROSION TO FILL HOLES IN RELEVANT OBJECT
        3) MORPHOLOGYEX OPENING - EROSION FOLLOWED BY DILATION TO REMOVE NOISE
        4) DILATION
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    opening = cv2.morphologyEx(closing, cv2.MORPH_OPEN, kernel)
    dilation = cv2.dilate(opening, kernel, iterations=2)
    return dilation

def detect_vehicles(frame_mask, FRAME_STATS, minimum_width, minimum_height):
    """
        1) FIND EXTERNAL CONTOURS ON FRAME_MASK
        2) FOR EACH CONTOUR CHECK IF THEY ARE VALID AND PUT COORDINATES AND
            CENTROID IN THE VEHICLES ARRAY
    """
    vehicles = []
    # FIND OUTER CONTOURS USING CV2.RETR_EXTERNAL AS RETREIVAL MODE
    # AND CV2.CHAIN_APPROX_TC89_L1 MODE
    _, contours, hierarchy = cv2.findContours(frame_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_TC89_L1)

    # PUT VALID CONTOURS IN THE VEHICLES ARRAY
    for (i, contour) in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(contour)
        if not ((w >= minimum_width) and (h >= minimum_height)):
            continue
        centroid_ = centroid(x, y, w, h)
        vehicles.append(((x, y, w, h), centroid_))

    return vehicles

def contour_detection(FRAME_STATS, background_subtractor, minimum_width=25, \
    minimum_height=25, save_image=False, image_dir='images'):
    """
        FOR EACH FRAME GENERATE FRAME_MASK AND FILTER THE MASKS TO GET
        APPROPRIATE CONTOURS AND DETECT THE VEHICLES SAVE THE DETECTED 
        VEHICLES IN DICTIONARY AND RETURN THE UPDATED DICTIONARY
    """
    # GET VALUES FROM FRAME_STATS DICTIONARY
    frame = FRAME_STATS['frame'].copy()
    frame_number = FRAME_STATS['frame_number']

    # PERFORM MORE TRAINING ON THE BACKGROUND SUBTRACTOR AND THRESHOLD
    frame_mask = background_subtractor.apply(frame, None, LEARNING_RATE)


    frame_mask[frame_mask < 175] = 0

    # PERFORM MORPHOLOGICAL OPERATIONS ON THE FRAME TO FILTER THE NOISE
    frame_mask = morph_mask(frame_mask)

    # STORE THE VEHICLES ARRAY IN THE FRAME_STATS DICTIONARY
    FRAME_STATS['vehicles'] = detect_vehicles(frame_mask, FRAME_STATS, minimum_width, minimum_height)

    # SAVE THE FRAME MASK
    if save_image: cv2.imwrite(image_dir + '/processed_'+ str(frame_number) + '.png', frame_mask)
    