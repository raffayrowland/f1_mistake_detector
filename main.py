from define_zones import getSectors, plotSectors, MarshalSectorData, addDataToSectors, plotSectors3D
import fastf1

session = fastf1.get_session(2024, "Silverstone", "R")
session.load(laps=True)

sectors = getSectors(session)

# plotSectors(sectors)

sectors = addDataToSectors(session, sectors)

plotSectors3D(sectors)

# Next: write function that finds closest point in track definition -> work out what sector a data point is in