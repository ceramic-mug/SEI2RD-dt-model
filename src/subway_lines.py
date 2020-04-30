# import gis packages
import fiona
from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon
# get the borough shapefile
borough = fiona.open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /boroughs/nybb.shp')
# get the subway line shapegile
subways = fiona.open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /routes_nyc_subway_may2019/routes_nyc_subway_may2019.shp')

# this code altered from https://gis.stackexchange.com/questions/208546/check-if-a-point-falls-within-a-multipolygon-with-python
lines = ([line for line in subways])

# begin writing to a new csv to hold the output
f = open("/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/dat/borough_subways.csv","w+")
f.write(','.join(['borough','route_id','color']))

# for every borough
for i, bo in enumerate(borough):

    # for every subway line
    for j, line in enumerate(lines):

        # get the line shape
        ln = shape(line['geometry'])

        # if the line is within the borough (completely) or intersects with the borough outline
        if ln.within(shape(bo['geometry'])) or ln.intersects(shape(bo['geometry'])):

            # add that line to the borough in a line of the csv
            f.write('\n'+','.join([bo['properties']['BoroName'],line['properties']['route_id'],line['properties']['color']]))

# close the csv file
f.close()
