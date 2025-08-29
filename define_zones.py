import fastf1

class MarshalSectorData:
    def __init__(self, sectorNumber, startDistance):
        self.start = startDistance
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

    def print(self):
        try:
            print(f"Sector {self.sectorNumber}: \n"
                  f"{self.start} to {self.end}\n"
                  f"Bounds: {self.xyBounds[0], self.xyBounds[-1], len(self.xyBounds)}\n")

        except:
            print(f"Could not print Sector {self.sectorNumber}.\n"
                  f"Start: {self.start}, end: {self.end}\n")


def getSectors(year, gp, identifier):
    session = fastf1.get_session(year, gp, identifier)
    session.load(laps=True)

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

    for idx, point in fastestLapTel.get_telemetry().iterrows():
        # if point['Source'] == "interpolation":
        #     continue

        x = point['X']
        y = point['Y']
        distance = point['Distance']

        for sector in sectors:
            if sector.start <= distance < sector.end:
                sector.addToBounds([x, y])

            elif sector is sectors[-1] and distance == sector.end:
                sector.addToBounds([x, y])

    for sector in sectors:
        sector.print()

    return sectors

# ----- EXPERIMENTATION -----

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