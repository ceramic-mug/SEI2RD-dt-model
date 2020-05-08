import pandas as pd
import geopandas as gpd

dat = pd.read_csv('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/out/v7/2020-05-07_20-03-12/2020-05-07_20-03-12.csv')

boxes = ['s','e','i','r','d']

days = [10,30,50,70]

ntas = dat['nta'].unique()

shape = gpd.read_file('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/gis /nynta_19d/nynta.shp')
for day in days:
    for box in boxes:
        i = str(day)+'_'+box
        a = []
        for index, row in shape.iterrows():
            nta = row['NTACode']

            if nta in ntas:
                if box == 'i':
                    a.append(sum(dat.loc[((dat.step == day) & (dat.nta == nta))]['is'].values)+sum(dat.loc[((dat.step == day) & (dat.nta == nta))]['ia'].values))
                else:
                    a.append(sum(dat.loc[((dat.step == day) & (dat.nta == nta))][box].values))

            else:
                a.append(0)
                
        shape[i] = a

shape.to_file('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/out/v7/2020-05-07_20-03-12/gis/2020-05-07_20-03-12.shp')
