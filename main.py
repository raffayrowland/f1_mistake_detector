from define_zones import getSectors, plotSectors, MarshalSectorData

sectors = getSectors(2025, "Silverstone", "R")

plotSectors(sectors)

# Next: write function that finds closest point in track definition -> work out what sector a data point is in