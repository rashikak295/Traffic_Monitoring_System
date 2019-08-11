# IMPORTS
import math
import numpy as np

# CONSTANTS
# ============================================================================
# CALCULATE THE EUCLIDEAN DISTANCE 
distance = lambda x,y,x_weight=1.0,y_weight=1.0: math.sqrt(float((x[0] - y[0])**2) \
            / x_weight + float((x[1] - y[1])**2) / y_weight)
# ============================================================================

def vehicle_exits(exit_masks, point):
    """
        - IF VEHICLE'S POINT FALLS IN THE EXIT ZONE RETURN TRUE
        - EXIT MASK HAS A VALUE 255 ON THAT POINT THEN THE VEHICLE EXITS
        - CHECK IN BOTH THE MASKS (COULD FALL IN LEFT OR RIGHT SIDE OF ROAD)
    """
    for exit_mask in exit_masks:
        try:
            if exit_mask[point[1]][point[0]] == 255:
                return True
        except:
            return True
    return False

# TODO - CAN INCLUDE WHILE GLOABAL VEHICLE_COUNT IS UPDATED
def count_vehicles(paths, exit_masks):
    """
        COUNT NUMBER OF EXITING VEHICLES IN CURRENT FRAME
    """
    frame_vehicle_count = [0,0]

    for path in paths:
        contour, centroid = path[-1][:2]
        # CHECK WHICH SIDE THE VEHICLE BELONGS TO
        if centroid[0] <= 645:
            frame_vehicle_count[0] += 1
        elif centroid[0] > 645:
            frame_vehicle_count[1] += 1

    return frame_vehicle_count

def vehicle_counter(FRAME_STATS, exit_masks=[], max_path=10, max_distance=30, x_weight=1.0, y_weight=1.0):
    """
        COUNT THE VEHICLES THAT ENTERTED THE EXIT ZONE BASED ON EXIT MASKS
        AND THE VEHICLES ARRAY DETECTED IN THE CONTOUR DETECTION MODULE
        
        INPUTS:
        MAX_PATH - MAX NUMBER OF POINTS ON A PATH
        MAX_DISTACE - MAX DISTANCE BETWEEN POINTS
    """
    # GET THE FRAME_STATS DICTIONARY VALUES
    vehicles = FRAME_STATS['vehicles']
    FRAME_STATS['exit_masks'] = exit_masks
    paths = FRAME_STATS['paths'] 
    vehicle_count = FRAME_STATS['vehicle_count']

    # SKIP IF NO VEHICLES
    if not vehicles:
        return FRAME_STATS

    # GET THE POINTS
    points = np.array(vehicles)
    points = points.tolist()

    # INITIALLY PATHS IS EMPTY THUS SAVE THE POINTS DIRECTLY
    if not paths:
        for point in points:
            paths.append([point])
    else:
        # CREATE A ARRAY UPDATED_PATHS FOR NEW PATHS BASED ON OLD PATHS
        updated_paths = []

        for path in paths:
            # INITIALIZE THE MIN DISTANCE AND MATCH VALUE
            min_distance = float('inf')
            value = None
    
            for point in points:
                # CALCULATE THE DISTANCE BETWEEN CURRENT POINT 
                # AND THE POINTS ON PREVIOUS PATHS
                # IF THE DISTANCE IS LESS THAN MINIMUM DISTANCE
                # THEN THE POINT BELONGS TO THAT PATH
                if len(path) == 1:    
                    distance_ = distance(point[0], path[-1][0])
                else:
                    xn = 2 * path[-1][0][0] - path[-2][0][0]
                    yn = 2 * path[-1][0][1] - path[-2][0][1]
                    distance_ = distance(point[0], (xn, yn),x_weight=x_weight,y_weight=y_weight)
                # UPDATE MIN_DISTANCE
                if distance_ < min_distance:
                    min_distance = distance_
                    value = point
            # CHECK IF THE MIN_DISTANCE IS LESS THAN THE
            # MAXIMUM THRESHOLD SET
            if value and min_distance <= max_distance:
                points.remove(value)
                path.append(value)
                updated_paths.append(path)
            
            # IF NO PATH IS FOUND IN CURRENT FRAME KEEP IN THE PATHS ARRAY
            if value is None:
                updated_paths.append(path)

        # UPDATE THE NEW PATHS
        paths = updated_paths
        
        # CHECK IF ANY VEHICLES EXIT THE EXIT ZONE IN THE REMAINING POINTS
        if len(points):
            for point in points:
                if not vehicle_exits(exit_masks, point[1]): 
                    paths.append([point])

    # FOR EACH PATH REMOVE THE EXTRA POINTS
    # THAT MAKE THE PATH LENGTH GREATER THAN THE MAX_PATH LENGTH
    for index, _ in enumerate(paths):
        paths[index] = paths[index][max_path*-1:]

    updated_paths = []

    for path in paths:
        path_ = path[-2:]

        # IF PATH_ LENGTH IS ATLEAST TWO AND VEHICLE MARKED BY PREVIOUS
        # POINT DOES NOT EXITS BUT VEHICLE MARKED BY CURRENT POINT EXITS
        if (len(path_) >= 2 and not vehicle_exits(exit_masks, path_[0][1]) and \
            vehicle_exits(exit_masks, path_[1][1]) and max_path <= len(path)):
            # CHECK WHICH SIDE DOES THE VEHICLE BELONG TO
            if path_[1][1][0] <= 645:
                vehicle_count[0] += 1
            elif path_[1][1][0] >= 732:
                vehicle_count[1] += 1      
        else:
            # CHECK IF THE PATH IS ALREADY IN EXIT ZONE
            # ELSE ADD TO NEW PATHS
            FLAG = True
            for p in path:
                if vehicle_exits(exit_masks, p[1]):
                    FLAG = False
                    break
            if FLAG: updated_paths.append(path)

    # UPDATE THE FRAME_STATS DICTIONARY
    FRAME_STATS['paths'] = updated_paths
    FRAME_STATS['vehicles'] = vehicles
    FRAME_STATS['vehicle_count'] = vehicle_count
    FRAME_STATS['frame_vehicle_count'] = count_vehicles(updated_paths, exit_masks)