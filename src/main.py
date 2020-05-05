import numpy as np
import pandas as pd
import re
# import fiona
# from shapely.geometry import shape,mapping, Point, Polygon, MultiPolygon

##### Useful regular expressions

color_getter = re.compile('#.*')

###### Reference lists and dictionaries ######

boroughs = [
'Bronx',
'Manhattan',
'Brooklyn',
'Staten Island',
'Queens'
]

county_to_borough = {
    'Bronx County': 'Bronx',
    'New York County': 'Manhattan',
    'Kings County': 'Brooklyn',
    'Richmond County': 'Staten Island',
    'Queens County': 'Queens',
    'out':'out'
}

###### functions ######

# convert feet to kilometers
def ft_to_m(_d_):
    return 0.3048 * _d_

###### import data ######

# import commuter flows data
commuting_flows_by_borough = pd.read_csv('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/dat/pertinent_commute.csv')
# change names to common names
commuting_flows_by_borough['from'] = [county_to_borough[i] for i in commuting_flows_by_borough['from']]
commuting_flows_by_borough['to'] = [county_to_borough[i] for i in commuting_flows_by_borough['to']]

# import nta population data
nta_populations = pd.read_csv('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/dat/New_York_City_Population_By_Neighborhood_Tabulation_Areas.csv')
nta_populations.head()
nta_populations = nta_populations[nta_populations['Year']==2010].sort_values(by=['NTA Code'])

# import nta distances to nearest subway stop
nta_distances_to_subway = pd.read_csv('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/dat/nta_subway_stop_distances_to_closest.csv')
# sort by NTA index
nta_distances_to_subway = nta_distances_to_subway.sort_values(by=['nta_code'])

# import subways per Borough
borough_subways = pd.read_csv('/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/dat/borough_subways.csv')

# get a list of NTAs for iteration
ntas = [i for i in nta_distances_to_subway['nta_code'].values.tolist()]

##### END IMPORT DATA #####

##### Compute Paramaters ######

#### PARAM 1: NTA sub_boxes populations

# sum population data by borough
borough_populations = {}

# use NTA populations to create borough populations for proportional commuter flow
for borough in nta_populations.Borough.unique():
    borough_populations[borough] = sum([i for i in nta_populations[nta_populations['Borough']==borough]['Population']])

# of those who commute, what proportion commutes where?
commuting_flows_by_borough['proportion'] = [row['n']/sum([i for i in commuting_flows_by_borough[commuting_flows_by_borough['from']==row['from']]['n']]) for index, row in commuting_flows_by_borough.iterrows()]

# from research, what percentage of the population commutes/works?
prop_commute = 0.648 # 1NYC and vital statistics of NY state, 2007

# then the number who stays at home/doesn't work is
prop_home = 1 - prop_commute

# create a dictionary to hold the sums of proportion of people who commute into other boroughs per borough
inter_borough_commuter_proportions = {}
for borough in boroughs:
    inter_borough_commuter_proportions[borough] = sum([i for i in commuting_flows_by_borough.loc[((commuting_flows_by_borough['from']==borough) & (commuting_flows_by_borough['to']!='out') & (commuting_flows_by_borough['to']!=borough))]['proportion']])

# add a column to the subway distances dataset that is the distance in kilometers
nta_distances_to_subway['distance(m)'] = [ft_to_m(i) for i in nta_distances_to_subway['distance(ft)']]

# function for subway ridership per population (_dist_ in meters, _borough_ string)
def subway_prop_population(_dist_,_borough_):

    a =  inter_borough_commuter_proportions[_borough_] * prop_commute * (-0.0004 * _dist_ + 0.53) # from Gutierrez et al, 2011

    # can't have a negative proportion
    if a <= 0:
        a = 0

    return a

# function for car ridership per population (_dist_ in meters)
def car_prop_population(_dist_,_borough_):
    return inter_borough_commuter_proportions[_borough_] * prop_commute - subway_prop_population(_dist_,_borough_)

# function for those who work within the borough
def in_commute_prop_population(_dist_,_borough_):
    return prop_commute * commuting_flows_by_borough.loc[((commuting_flows_by_borough['from']==_borough_) & (commuting_flows_by_borough['to']==_borough_))]['proportion'].values[0]

# Each NTA will have 4 sub-boxes:
#   - inter-borough commuters by subway
#   - inter-borough commuters by car
#   - home borough commuters
#   - stay-at-home or commute out of city
# The populations for each of these boxes will be computed for each NTA by the following function:

def partition(_dist_,_borough_,_pop_):
    s_ = subway_prop_population(_dist_,_borough_)*_pop_
    c_ = car_prop_population(_dist_,_borough_)*_pop_
    i_ = in_commute_prop_population(_dist_,_borough_)*_pop_
    h_ = _pop_ - (s+c+i)
    return [s_,c_,i_,h_]

#### PARAM 2: Computing effective population coefficients for subway lines, NTAs, and Boroughs

# find the proportion of each metro, car box goes to the borough in question (first nesting) from each other borough (second nesting)
borough_propto = {}
for _borough_ in boroughs:
    borough_propto[_borough_] = {}
    _other_boroughs_ = [i for i in boroughs if i!=_borough_]
    for b in _other_boroughs_:
        borough_propto[_borough_][b] = commuting_flows_by_borough.loc[((commuting_flows_by_borough['from']==b)&(commuting_flows_by_borough['to']==_borough_))]['proportion'].values[0]/inter_borough_commuter_proportions[b]

# compute the effective borough I/N at each timestep
def effective_borough(_borough_,_nta_dict_,_model_,_timestep_):
    # which NTAs send people into this borough
    _outer_ntas_ = nta_populations.loc[nta_populations['Borough']!=_borough_].values
    _n_ = 0
    _i_ = 0

    # add from people commuting in from the outside
    for _nta_ in _outer_ntas_:
        _n_ += borough_propto[_borough_][nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]]*sum(sum([_model_[_timestep_,_nta_dict_[_nta_],:2,:-1]))
        _i_ += borough_propto[_borough_][nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]]*sum(sum([_model_[_timestep_,_nta_dict_[_nta_],:2,2:4]))
    _inner_ntas_ = nta_populations.loc[nta_populations['Borough']==_borough_].values

    # add from people commuting internally
    for _nta in _inner_ntas_:
        _n_ += sum([_model_[_timestep_,_nta_dict_[_nta_],2,:-1])
        _n_ += sum([_model_[_timestep_,_nta_dict_[_nta_],2,2:4])
    return _i_/_n_

# compute the effective NTA I/N at each timestep
def effective_nta(_nta_,_nta_dict_,_model_,_timestep_):
    return sum(sum([_model_[_timestep_,_nta_dict_[_nta_],:,2:4]))/sum(sum([_model_[_timestep_,_nta_dict_[_nta_],:,:-1]))

# compute the number of distinct subway lines (colors) an NTA subway rider population rides
def nta_colors(_nta_code_):
    _colors_ = [i for i in nta_distances_to_subway[nta_distances_to_subway['nta_code']==_nta_code_][['color1','color2','color3','color4']].values[0].tolist() if not pd.isnull(i)]
    _unique_ = [i for i in np.unique(np.array(_colors_))]
    _n_ = len(_unique_)
    return (_n_, _unique_)

# compute the effective train line I/N at each timestep
def effective_train(_train_color_,_model_,_timestep_):
    _n_ = 0
    _i_ = 0

    for _nta_ in ntas:
        a = nta_colors(_nta_)

        # if the nta's subway population rides this subways
        if _color_ in a[1]:
            _n_ += sum(_model_[_timestep_,_nta_dict_[_nta_],0,:-1])/a[0]
            _i_ += sum(_model_[_timestep_,_nta_dict_[_nta_],0,2:4])/a[0]

        # otherwise, use the commuter influxes
        else:
            for _borough_ in borough_subways[borough_subways['color']==_color_].values:
                if _nta_ not in nta_populations[nta_populations['Borough']==_borough_].values:
                    _n_ += borough_propto[_borough_][nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]]*sum(_model_[_timestep_,_nta_dict_[_nta_],0,:-1])/len(borough_subways[borough_subways['borough']==_borough_].values)
                    _i_ += borough_propto[_borough_][nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]]*sum(_model_[_timestep_,_nta_dict_[_nta_],0,2:4])/len(borough_subways[borough_subways['borough']==_borough_].values)

    return _i_/_n_
