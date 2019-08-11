# VARIABLES
import os
import csv

# CONSTANTS
# ============================================================================
fp = open('report.csv', 'w')
writer = csv.DictWriter(fp, fieldnames=['time', 'cumm_vehicles_left', 'cumm_vehicles_right','density_left','density_right', 'vehicles_left', 'vehicles_right'])
writer.writeheader()
previous_count = [0,0]
start_time=0
fps=25
# ============================================================================

def csv_writer(FRAME_STATS):
	# GLOBALS
	global previous_count, start_time, fps
	frame_number = FRAME_STATS['frame_number']
	vehicle_count = FRAME_STATS['vehicle_count']
	capacity = FRAME_STATS['capacity']

	# COUNT VEHICLES DETECTED IN CURRENT FRAME
	count = _count = vehicle_count[:]
	
	# _COUNT STORES CURRENT FRAME VALUES
	if previous_count:
	    _count[0] = count[0] - previous_count[0]
	    _count[1] = count[1] - previous_count[1]

	# WRITE TO THE CSV FILE
	time = (start_time + (frame_number) * (1.0/fps))
	writer.writerow({'time': time, 'cumm_vehicles_left': vehicle_count[0], 'cumm_vehicles_right':vehicle_count[1], 'density_left':capacity[0], 'density_right':capacity[1], 'vehicles_left':_count[0], 'vehicles_right':_count[1]})
	previous_count = count

