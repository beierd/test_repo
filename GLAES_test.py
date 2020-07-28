import glaes as gl
import geokit as gk
from os.path import join
from matplotlib import pyplot as plt


# Choose a region to operate on (Here, a predefined region for Aachen, Germany is used)
regionPath = '/home/dbeier/git-projects/glaes/glaes/test/data/aachenShapefile.shp' #['aachenShapefile.shp']
# Initialize ExclusionCalculator object
ec = gl.ExclusionCalculator(regionPath, srs=3035, pixelSize=100)
# Visualize avilability
plot = ec.draw()

# Set a path to a local copy of the CLC raster dataset (Here, a small sample is provided around Aachen)
clcRasterPath = gl._test_data_["clc-aachen_clipped.tif"]
# Apply exclusion
ec.excludeRasterType(clcRasterPath, value=(12,22))
# Visualize
ec.draw()

# Apply exclusion
ec.excludeRasterType(clcRasterPath, value=(1,2), buffer=1000)
# Visualize
ec.draw()

# Set a path to a local copy of the OSM roads dataset (Here, a small sample is provided around Aachen)
roadwaysPath = gl._test_data_["aachenRoads.shp"]
# Apply Exclusion
whereStatement = "type='motorway' OR type='primary' OR type='trunk'"
ec.excludeVectorType(roadwaysPath, where=whereStatement, buffer=200)
# Visualize
ec.draw()

ec.save("/home/dbeier/git-projects/glaes/images/aachens_best_pv_spots.tif", overwrite=True)




# Placement Algorithm

ec.distributeItems(separation=1000)
ec.draw()

# Do placements
ec.distributeItems(1000, asArea=True, output="aachen_placement_areas.shp")
ec.draw()