import pandas as pd

# ----- EXTRACT FEATURES -----

import fastf1

# Load session
session = fastf1.get_session(2025, 'Hungary', 'R')
session.load(laps=True)

# Get all information of the corners for this circuit
# We will use Distance
corners = session.get_circuit_info().corners
print(corners)

# Get all the information on the laps by every driver
laps = session.laps
laps = laps.pick_accurate()  # Pick only laps under green or yellow flag, that are not an in or out lap
print(laps)

# ----- DETERMINE CORNER ZONES -----

"""
Data object in this class:

{
    "dataPoints" : [
        {
            "speed": 0,
            "throttle": 0,
            "gear": 0,
            "brake": 0,
            "distance": 0
        },
    ]
}

"""

# The object that contains all the data about a single corner
# Corner number, start of corner zone, end of corner zone, location of apex, data on car
class CornerZone:
    def __init__(self, start, apex, end, cornerNumber):
        self.cornerNumber = cornerNumber
        self.data = {
            "dataPoints": []
        }
        self.start = start
        self.apex = apex
        self.end = end

    def print(self):
        print(f"Corner: {self.cornerNumber}\nStart: {self.start}\nApex: {self.apex}\nEnd: {self.end}\n")

    def getLower(self):
        return self.start

    def getUpper(self):
        return self.end

    def addToData(self, data):
        self.data["dataPoints"].append(data)

    def getData(self):
        return self.data

# determine the length of the track
lap = session.laps.pick_fastest()
tel = lap.get_car_data().add_distance()
trackLength = float(tel['Distance'].max())

cornerZones = []

# Iterate through each corner to define the corner zones
for idx, corner in corners.iterrows():
    if idx == 0:
        start = 0
        apex = corner['Distance']

    else:
        previousEnd = apex + (corner['Distance'] - apex) / 2

        cornerZones.append(CornerZone(start, apex, previousEnd, corner["Number"] - 1))

        start = previousEnd
        apex = corner['Distance']

previousEnd = apex + (corner['Distance'] - apex) / 2
cornerZones.append(CornerZone(start, apex, trackLength, corner["Number"]))

for i in cornerZones: i.print()

# ----- GET CORNER DATA -----

dataPoint = {
        "speed": 0,
        "throttle": 0,
        "gear": 0,
        "brake": 0,
        "distance": 0
    }

# Get the telemetry data for the McLaren team
# Iterate through each lap
for idx, lap in laps.pick_teams("McLaren").iterrows():
    # Get the telemetry for this lap
    tel = lap.get_telemetry()
    print(len(tel), "len telemetry")

    # Array that holds all the data for a single lap
    lapDataPoints = [dataPoint.copy() for i in range(len(tel))]

    # Gets a series of all the data (so all the speed data over a single lap for example)
    allSpeed = tel['Speed']
    allGear = tel['nGear']
    allThrottle = tel['Throttle']
    allBrake = tel['Brake']
    allDistance = tel['Distance']

    print(len(allSpeed), "len speed")
    print(len(allGear), "len gear")
    print(len(allThrottle), "len throttle")
    print(len(allBrake), "len brake")
    print(len(allDistance), "len distance\n")

    # Goes through each speed reading and adds it to the lap's data
    for speed_idx, speed in enumerate(allSpeed):
        lapDataPoints[speed_idx]['speed'] = speed

    for gear_idx, gear in enumerate(allGear):
        lapDataPoints[gear_idx]['gear'] = gear

    for throttle_idx, throttle in enumerate(allThrottle):
        lapDataPoints[throttle_idx]['throttle'] = throttle

    for brake_idx, brake in enumerate(allBrake):
        lapDataPoints[brake_idx]['brake'] = brake

    # TODO: Convert to using x and y to stop the distance error
    for distance_idx, distance in enumerate(allDistance):
        lapDataPoints[distance_idx]['distance'] = distance

    cornerIndex = 0

    # move each data point to the corresponding corner object
    for dataPoint in lapDataPoints:
        distance = dataPoint['distance']
        currentCornerRange = [cornerZones[cornerIndex].getLower(), cornerZones[cornerIndex].getUpper()]  # get the bounds for the current corner

        # place the data point to the corresponding corner object
        if currentCornerRange[0] <= distance < currentCornerRange[1]:
            cornerZones[cornerIndex].addToData(dataPoint)
            continue

        if cornerIndex == len(cornerZones) - 1:
            print(f"No next corner {cornerIndex}")
            continue

        nextCornerRange = [cornerZones[cornerIndex + 1].getLower(), cornerZones[cornerIndex + 1].getUpper()]

        if nextCornerRange[0] <= distance < nextCornerRange[1]:
            cornerIndex += 1
            cornerZones[cornerIndex].addToData(dataPoint)

        else:
            print(f"Skipped data at corner {cornerIndex}")

for i in range(len(cornerZones)):
    cornerZones[i].print()
    print(len(cornerZones[i].getData()['dataPoints']))

# ----- PLOT SPEED/DISTANCE GRAPHS -----

import matplotlib.pyplot as plt

for corner in cornerZones:
    data = corner.getData()['dataPoints']

    xAxis = [dataPoint.get("distance") for dataPoint in data]
    yAxis = [dataPoint.get("speed") for dataPoint in data]

    pairs = sorted(zip(yAxis, xAxis))
    xAxis, yAxis = zip(*pairs)

    plt.figure()
    plt.scatter(yAxis, xAxis, s=8)
    plt.xlabel("Distance (m)")
    plt.ylabel("Speed (km/h)")
    plt.title(f"Corner {corner.cornerNumber}: Speed vs Distance")
    plt.grid(True)

plt.show()