import pandas as pd

# ----- EXTRACT FEATURES -----

import fastf1

# Load session
session = fastf1.get_session(2025, 'Belgium', 'R')
session.load(laps=True)

# Get all information of the corners for this circuit
# We will use Distance
corners = session.get_circuit_info().corners
print(corners)

# Get all the information on the laps by every driver
laps = session.laps
laps = laps.pick_accurate()
print(laps)

# ----- DETERMINE CORNER ZONES -----

"""
Data object in this class:

{
    "laps": [
        dataPoints: [          # for lap 1, 2, etc.
            {
                "speed": speed
                "throttle": throttle
                "gear": gear
                "brake": brake
                "distance": distance
            }, ...
        ], ...
    ]   
}

"""

class CornerZone:
    def __init__(self, start, apex, end, cornerNumber):
        self.cornerNumber = cornerNumber
        self.data = {
            "laps": []
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
        self.data["laps"].append(data)
cornerZones = []

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
cornerZones.append(CornerZone(start, apex, previousEnd + 20, corner["Number"]))

for i in cornerZones: i.print()

# ----- GET CORNER DATA -----

cornerIndex = 0

# Get the telemetry data for the McLaren team
# Iterate through each lap
for idx, lap in laps.pick_teams("McLaren").iterrows():
    dataPoint = {
        "speed": 0,
        "throttle": 0,
        "gear": 0,
        "brake": 0,
        "distance": 0
    }

    # Get the telemetry for this lap
    tel = lap.get_telemetry()
    print(len(tel), "len telemetry")
    lapDataPoints = [dataPoint for i in range(len(tel))]

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
    print(len(allDistance), "len distance")

    lowestDistance = None
    highestDistance = None

    # Goes through each speed reading and adds it to the lap's data
    for speed_idx, speed in enumerate(allSpeed):
        lapDataPoints[speed_idx]['speed'] = speed

    for gear_idx, gear in enumerate(allGear):
        lapDataPoints[gear_idx]['gear'] = gear

    for brake_idx, brake in enumerate(allBrake):
        lapDataPoints[brake_idx]['brake'] = brake

    for distance_idx, distance in enumerate(allDistance):
        if not lowestDistance: lowestDistance = distance
        if not highestDistance: highestDistance = distance

        if distance < lowestDistance: lowestDistance = distance
        elif distance > highestDistance: highestDistance = distance

        lapDataPoints[distance_idx]['distance'] = distance

    print(lapDataPoints)
