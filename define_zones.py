import fastf1
import math

class MarshalSectorData:
    def __init__(self, sectorNumber, startDistance):
        self.start = startDistance
        self.length = 0
        self.end = 0
        self.sectorNumber = sectorNumber
        self.xyBounds = []
        self.data = {
            "dataPoints": []
        }

    def setEnd(self, end):
        self.end = end

    def addToBounds(self, bounds):
        self.xyBounds.append(bounds)

    def addToData(self, dataPoint):
        self.data["dataPoints"].append(dataPoint)

    def getClosestPoint(self, point):
        lowestDistance = None

        for pair in self.xyBounds:
            deltaX = abs(pair[0] - point[0])
            deltaY = abs(pair[1] - point[1])

            distance = math.sqrt((deltaX * deltaX) + (deltaY * deltaY))

            if lowestDistance is None:
                lowestDistance = distance

            if distance < lowestDistance:
                lowestDistance = distance

        return lowestDistance

    def print(self):
        try:
            print(f"Sector {self.sectorNumber}: \n"
                  f"{self.start} to {self.end}\n"
                  f"Bounds: {self.xyBounds[0], self.xyBounds[-1], len(self.xyBounds)}\n"
                  f"Len data points: {len(self.data['dataPoints'])}")

        except:
            print(f"Could not print Sector {self.sectorNumber}.\n"
                  f"Start: {self.start}, end: {self.end}\n")


def getSectors(session):
    fastestLapTel = session.laps.pick_fastest()
    marshalSectors = session.get_circuit_info().marshal_sectors

    sectors = []

    counter = 1
    for idx, sector in marshalSectors.iterrows():
        sectors.append(MarshalSectorData(counter, sector['Distance']))

        if counter > 1:
            sectors[counter - 2].setEnd(sector['Distance'])

        counter += 1

    trackLength = float(fastestLapTel.get_car_data().add_distance()['Distance'].max())
    sectors[-1].setEnd(trackLength)

    # calculate the length of a sector even if it crosses the start/finish line
    for sector in sectors:
        sector.length = (sector.end - sector.start) % trackLength

    for idx, point in fastestLapTel.get_telemetry().iterrows():
        # if point['Source'] == "interpolation":
        #     continue

        x = point['X']
        y = point['Y']
        distance = point['Distance']

        for sector in sectors:
            if (distance - sector.start) % trackLength < sector.length:
                sector.xyBounds.append([x, y])

    for sector in sectors:
        sector.print()

    return sectors

def addDataToSectors(session, sectors):
    """
    This function adds the telemetry data to the sector objects ready for plotting. The data is formatted like this:

    in sector object there is sector.data, which is a json containing a list "datapoints". This list contains these dictionaries:

    dataPoint = {
        "speed": 0,
        "throttle": 0,
        "gear": 0,
        "brake": 0,
        "x": 0,
        "y": 0
    }

    """

    laps = session.laps.pick_drivers("PIA").pick_accurate()

    for idx, reading in laps.get_telemetry().iterrows():
        if reading["Source"] == "interpolation":
            continue

        speed = reading['Speed']
        throttle = reading['Throttle']
        brake = reading['Brake']
        gear = reading['nGear']
        x = reading['X']
        y = reading['Y']

        dataPoint = {
            "speed": speed,
            "throttle": throttle,
            "gear": gear,
            "brake": brake,
            "x": x,
            "y": y
        }

        lowestDistance = None
        closestSector = None

        for sector in sectors:
            distance = sector.getClosestPoint([x, y])

            if lowestDistance is None:
                lowestDistance = distance
                closestSector = sector

            if distance < lowestDistance:
                closestSector = sector
                lowestDistance = distance

        closestSector.addToData(dataPoint)

    return sectors

# ----- VISUALISATION -----

def plotSectors(sectors):
    import matplotlib.pyplot as plt

    for sector in sectors:
        if not sector.xyBounds:
            continue

        xs, ys = zip(*sector.xyBounds)

        plt.figure()
        plt.scatter(xs, ys, s=6)
        plt.title(f"Sector {sector.sectorNumber}: {sector.start:.1f} m to {sector.end:.1f} m")
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.gca().set_aspect('equal', adjustable='box')
        plt.grid(True)

    plt.show()

def plotSectors3D(sectors, out_dir="plots"):
    import os
    import plotly.graph_objects as go

    os.makedirs(out_dir, exist_ok=True)
    saved = []

    for sector in sectors:
        dps = sector.data.get("dataPoints", [])
        if not dps:
            continue

        xs = [dp["x"] for dp in dps]
        ys = [dp["y"] for dp in dps]
        zs = [dp["speed"] for dp in dps]

        # Color rule:
        # - red if brake is True
        # - blue if throttle == 0
        # - otherwise green gradient: light at low throttle -> dark at high throttle
        colors = []
        for dp in dps:
            if bool(dp.get("brake", 0)):
                colors.append("red")
                continue

            t = float(dp.get("throttle", 0))
            t = max(0.0, min(100.0, t))  # clamp to [0,100]

            if t == 0:
                colors.append("blue")
            else:
                # HSL green with lightness from 85% (light) to 25% (dark) as throttle goes 0->100
                lightness = 85 - (t / 100.0) * (85 - 25)
                colors.append(f"hsl(120, 100%, {lightness:.1f}%)")

        fig = go.Figure(
            data=[go.Scatter3d(
                x=xs, y=ys, z=zs,
                mode="markers",
                marker=dict(size=2, color=colors)
            )]
        )
        fig.update_layout(
            title=f"Sector {sector.sectorNumber}: X, Y, Speed",
            scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Speed"),
            showlegend=False
        )

        filename = os.path.join(out_dir, f"sector_{sector.sectorNumber}_xyz_speed.html")
        fig.write_html(filename, include_plotlyjs="cdn", full_html=True)
        saved.append(filename)

    return saved