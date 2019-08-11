# VARIABLES
import os
import logging
import csv
import numpy as np
import cv2

# CONSTANTS
# ============================================================================
BOUNDING_BOX_COLOUR = (255, 0, 0)
CENTROID_COLOUR = (0, 0, 255)
# ============================================================================

def draw_boxes(img, paths, exit_masks=[]):
    """
        DRAW BOXES ON THE VEHICLES THAT ARE DETECTED
    """
    for path in paths:
        contour, centroid = path[-1][:2]
        # DONT DRAW IF VEHICLE EXITS
        if vehicle_exits(centroid, exit_masks): continue
        x, y, w, h = contour

        # DRAW RECTANGLE AND CIRCLE DENOTING THE BOUNDARY AND CENTROID OF VEHICLE
        cv2.rectangle(img, (x, y), (x + w - 1, y + h - 1),BOUNDING_BOX_COLOUR, 1)
        cv2.circle(img, centroid, 2, CENTROID_COLOUR, -1)
    return img

def draw_ui(img, vehicle_count, capacity, exit_masks=[]):
    """
        DRAWS THE LINES DENOTING THE EXIT MASKS
        AND THE STATS PER FRAME
    """
    # EXIT MASKS
    cv2.line(img, (0,400),(645,400),(0,255,0),2)
    cv2.line(img, (732,590),(1280,500),(0,255,0),2)
    
    # STATS
    cv2.rectangle(img, (0, 0), (img.shape[1], 50), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, ("Density: {cur_left}%  Vehicles passed: {left}               \
        Density: {cur_right}%  Vehicles passed: {right}".format(\
        left=vehicle_count[0], right=vehicle_count[1], \
        cur_right=round(capacity[1]*100,3),\
        cur_left=round(capacity[0]*100,3))), (30, 30),\
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
    
    return img

def vehicle_exits(point, exit_masks=[]):
    """
        CHECK IF THE VEHICLE EXITS
    """
    for exit_mask in exit_masks:
        if exit_mask[point[1]][point[0]] == 255:
            return True
    return False

def visualizer(FRAME_STATS, save_image=True, image_dir='images'):
    """
        DRAWS THE VEHICLE BOXES, CENTROID, STATS AND EXIT MASKS
    """
    frame = FRAME_STATS['frame'].copy()
    frame_number = FRAME_STATS['frame_number']
    paths = FRAME_STATS['paths']
    exit_masks = FRAME_STATS['exit_masks']
    vehicle_count = FRAME_STATS['vehicle_count']
    capacity = FRAME_STATS['capacity']

    frame = draw_ui(frame, vehicle_count, capacity, exit_masks)
    frame = draw_boxes(frame, paths, exit_masks)
    
    if save_image: cv2.imwrite(image_dir + "/processed_%04d.png" % frame_number, np.flip(frame,2))
