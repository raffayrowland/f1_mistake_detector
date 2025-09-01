from define_zones import getSectors, plotSectors, MarshalSectorData, addDataToSectors, plotSectors3D, plotSectors3DByTyre
import fastf1

session = fastf1.get_session(2025, "Miami", "R")
session.load(laps=True)

sectors = getSectors(session)

# plotSectors(sectors)

sectors = addDataToSectors(session, sectors)

plotSectors3D(sectors)
