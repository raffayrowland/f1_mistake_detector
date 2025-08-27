import pandas as pd

# ----- EXTRACT FEATURES -----

import fastf1

# Load session
session = fastf1.get_session(2025, 'Belgium', 'R')
session.load(laps=True)

# Get all information of the corners for this circuit
# We will use X, Y, Distance, and
corners = session.get_circuit_info().corners
print(corners)

# Get all the information on the laps by every driver
laps = session.laps
laps = laps.pick_accurate()
print(laps)

# ----- DETERMINE CORNER ZONES -----

class CornerZone:
    def __init__(self, start, apex, end):
        self.start = start
        self.end = end
        self.apex = apex

    def print(self):
        print(f"Start: {self.start}\nApex: {self.apex}\nEnd: {self.end}\n")

cornerZones = []

for idx, corner in corners.iterrows():
    if idx == 0:
        start = 0
        apex = corner['Distance']

    else:
        previousEnd = apex + (corner['Distance'] - apex) / 2

        cornerZones.append(CornerZone(start, apex, previousEnd))

        start = previousEnd
        apex = corner['Distance']

previousEnd = apex + (corner['Distance'] - apex) / 2
cornerZones.append(CornerZone(start, apex, previousEnd + 20))

print(len(cornerZones))

for i in cornerZones:
    i.print()