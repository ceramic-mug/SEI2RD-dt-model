import fiona

nta_bus = fiona.open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /bus_stops_NTA/bus_stops_NTA.shp')

counts = {}

for i, stop in enumerate(nta_bus):
    if stop['properties']['nta'] in counts.keys():
        counts[stop['properties']['nta']] += 1
    else:
        counts[stop['properties']['nta']] = 1

f = open('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/dat/nta_bus_stop_counts.csv','w+')
f.write(','.join(['nta','bus_stops']))

for key, value in counts.items():
    f.write('\n'+','.join([key,str(value)]))

f.close()
