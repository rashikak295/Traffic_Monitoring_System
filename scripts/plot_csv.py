# VARIABLES
import matplotlib.pyplot as plt
import csv

# CONSTANTS
# ============================================================================
time=[]
cumm_vehicles_left=[]
cumm_vehicles_right=[]
density_left=[]
density_right=[]
vehicles_left=[]
vehicles_right=[]
header = True
increment = 100
# ============================================================================

with open('report.csv', 'r') as csvfile:
    # OPEN CSV READER
    plots= csv.reader(csvfile, delimiter=',')

    # FOR EVERY ROW WE APPEND ALL THE VALUES IN
    # RESPECTIVE LIST AND CREATE THE LISTS
    for row in plots:
        if(header):
            header = False
            continue
        time.append(float(row[0]))
        cumm_vehicles_left.append(int(row[1]))
        cumm_vehicles_right.append(int(row[2]))
        density_left.append(float(row[3])*100)
        density_right.append(float(row[4])*100)
        vehicles_left.append(int(row[5]))
        vehicles_right.append(int(row[6]))

# PLOTTING ALL THE STATS
plt.plot(time[::increment],cumm_vehicles_left[::increment])
plt.plot(time[::increment],cumm_vehicles_right[::increment])
plt.legend(['vehicles_passed_left', 'vehicles_passed_right'], loc='lower right')
plt.title('Vehicles Passed')

plt.xlabel('Time(s)')
plt.ylabel('Vehicles passed(count)')

plt.savefig("vehicles_count.png")

plt.figure()
plt.plot(time[::increment],density_left[::increment])
plt.plot(time[::increment],density_right[::increment])
plt.legend(['density_left', 'density_right'], loc='lower right')
plt.title('Vehicle Density')

plt.xlabel('Time(s)')
plt.ylabel('Density(%)')

plt.savefig("vehicles_density.png")

plt.figure()
plt.plot(time[::increment],vehicles_left[::increment])
plt.plot(time[::increment],vehicles_right[::increment])
plt.legend(['vehicles_left', 'vehicles_right'], loc='lower right')
plt.title('Vehicle Count Per Frame')

plt.xlabel('Time(s)')
plt.ylabel('Vehicle(count)')

plt.savefig("vehicles_framecount.png")
