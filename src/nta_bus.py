# import modules
import fiona
from shapely.geometry import shape, mapping

ntas = fiona.open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /nynta_19d/nynta.shp')

# adapted from https://gis.stackexchange.com/questions/215963/adding-column-to-shapefile-with-fiona

with fiona.open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /bus_stops_nyc_dec2019/bus_stops_nyc_dec2019.shp', 'r') as input:
    schema = input.schema.copy()
    input_crs = input.crs
    schema['properties']['nta'] = 'str'
    with fiona.open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /bus_stops_NTA/bus_stops_NTA.shp', 'w', 'ESRI Shapefile', schema, input_crs) as output:
         for elem in input:

             # get the stop point
             stop = shape(elem['geometry'])

             for i, nta in enumerate(ntas):

                 # if the stop is within the NTA
                 if stop.within(shape(nta['geometry'])):

                     elem['properties']['nta']=nta['properties']['NTACode']

                     break

                 else:

                     elem['properties']['nta']='null'

             output.write({'properties':elem['properties'],'geometry': mapping(shape(elem['geometry']))})
