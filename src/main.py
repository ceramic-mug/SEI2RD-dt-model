import numpy as np
import pandas as pd
import re
import random
from datetime import date

##### Useful regular expressions

color_getter = re.compile('#.*')

###### Reference lists and dictionaries ######

categories = [
'm',
'c',
'i',
'h'
]

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
subways = np.unique(borough_subways['color'].values)
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

######################## END PARAMS

##### MATRICES #######

beta_metro = 0.5944
beta_borough = 0.5944
beta_nta = 0.5944
mean_latent_period = 3
proportion_symptomatic = 0.5
mean_infectious_period = 5
proportion_severe_cases = 0.05

nta_populations.head()
borough_subways.head()


def commuter_term(_nta_,_effective_dict_):

    term = 0
    home_borough = nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]
    for _borough_ in borough_propto[home_borough].keys():
        term += borough_propto[home_borough][_borough_] * beta_borough * _effective_dict_['borough']

    return term

def metro_term(_nta_,_effective_dict_):

    term = 0
    home_borough = nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]
    # add all the various possible interactions with various subways by weight of travel
    for _borough_ in borough_propto[home_borough].keys():
        term += beta_metro * borough_propto[home_borough][_borough_] * np.average(np.array([_effective_dict_['metro'][i] for i in borough_subways[borough_subways['borough']==_borough_]['color'].values]))
    return term

def home_term(_nta_,_effective_dict_):
    return beta_nta*_effective_dict_['nta'][_nta_]

def inborough_term(_nta_,_effective_dict_):
    return beta_borough*_effective_dict_['borough'][nta_populations[nta_populations['NTA Code']==_nta_]['Borough'].values[0]]

def matrices(_effective_dict_,_nta_):

    home_matrix = np.array([[-(home_term(_nta_,_effective_dict_)),0,0,0,0,0],
                            [home_term(_nta_,_effective_dict_),-mean_latent_period**(-1),0,0,0,0],
                            [0,(1-proportion_symptomatic)*mean_latent_period**(-1),-mean_infectious_period**(-1),0,0,0],
                            [0,proportion_symptomatic*mean_latent_period**(-1),0,-mean_infectious_period**(-1)(proportion_severe_cases+1),0,0],
                            [0,0,mean_infectious_period**(-1),mean_infectious_period**(-1),0,0],
                            [0,0,0,mean_infectious_period**(-1)*proportion_severe_cases,0,0]])

    subway_matrix = np.array([[-(home_term(_nta_,_effective_dict_)+commuter_term(_nta_,_effective_dict_)+metro_term(_nta_,_effective_dict_)),0,0,0,0,0],
                            [home_term(_nta_,_effective_dict_)+commuter_term(_nta_,_effective_dict_)+metro_term(_nta_,_effective_dict_),-mean_latent_period**(-1),0,0,0,0],
                            [0,(1-proportion_symptomatic)*mean_latent_period**(-1),-mean_infectious_period**(-1),0,0,0],
                            [0,proportion_symptomatic*mean_latent_period**(-1),0,-mean_infectious_period**(-1)(proportion_severe_cases+1),0,0],
                            [0,0,mean_infectious_period**(-1),mean_infectious_period**(-1),0,0],
                            [0,0,0,mean_infectious_period**(-1)*proportion_severe_cases,0,0]])

    car_matrix = np.array([[-(home_term(_nta_,_effective_dict_)+commuter_term(_nta_,_effective_dict_)),0,0,0,0,0],
                            [home_term(_nta_,_effective_dict_)+commuter_term(_nta_,_effective_dict_),-mean_latent_period**(-1),0,0,0,0],
                            [0,(1-proportion_symptomatic)*mean_latent_period**(-1),-mean_infectious_period**(-1),0,0,0],
                            [0,proportion_symptomatic*mean_latent_period**(-1),0,-mean_infectious_period**(-1)(proportion_severe_cases+1),0,0],
                            [0,0,mean_infectious_period**(-1),mean_infectious_period**(-1),0,0],
                            [0,0,0,mean_infectious_period**(-1)*proportion_severe_cases,0,0]])

    inborough_matrix = np.array([[-(home_term(_nta_,_effective_dict_)+inborough_term(_nta_,_effective_dict_)),0,0,0,0,0],
                            [home_term(_nta_,_effective_dict_)+inborough_term(_nta_,_effective_dict_),-mean_latent_period**(-1),0,0,0,0],
                            [0,(1-proportion_symptomatic)*mean_latent_period**(-1),-mean_infectious_period**(-1),0,0,0],
                            [0,proportion_symptomatic*mean_latent_period**(-1),0,-mean_infectious_period**(-1)(proportion_severe_cases+1),0,0],
                            [0,0,mean_infectious_period**(-1),mean_infectious_period**(-1),0,0],
                            [0,0,0,mean_infectious_period**(-1)*proportion_severe_cases,0,0]])
subways
    return (subway_matrix,car_matrix,inborough_matrix,home_matrix)

# compute the effectvie I/N coefficients for each thing in each category
def compute_effectives(_nta_dict_,_model_,_timestep_):
    effective_dict = {'borough':{},'nta':{},'metro'{}}

    for _borough_ in boroughs:
        effective_dict['borough'][_borough_] = effective_borough(_borough_,_nta_dict_,_model_,_timestep_)
    for _nta_ in ntas:
        effective_dict['nta'][_nta_] = effective_nta(_nta_,_nta_dict_,_model_,_timestep_)
    for _line_ in subways:
        effective_dict['metro'][_line_] = effective_dict(_line_,_model_,_timestep_)

    return effective_dict

def main(time):

    model = np.zeros([time,len(ntas),4,6])

    nta_dict = {}
    for i in range(len(ntas)):
        nta_dict[ntas[i]] = i
        model[0,i,:,0] = partition(nta_distances_to_subway[nta_distances_to_subway['nta_code']==ntas[i]]['distance(m)'].values[0],nta_populations[nta_populations['NTA Code']==ntas[i]]['Borough'].values[0],nta_populations[nta_populations['NTA Code']==ntas[i]]['Population'].values[0])

    # which NTA starts with an infected person?
    starter_nta = random.randint(0,len(ntas))
    model[0,starter_nta,0,0] -= 1
    model[0,starter_nta,0,4] += 1

    f = open("/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/out/"+date.today()+'.csv',"w+")
    f.write(','.join(['step','nta','cat','s','e','is','ia','r','d']))
    for nta in ntas:
        for i in range(len(categories)):
            f.write('\n'+','.join([str(0),nta,categories[i],','.join(model[0,nta_dict[nta],i,:])]))

    for step in range(time-1):
        effectives = compute_effectives(nta_dict,model,step)
        for nta in ntas:
            m = matrices(effectives,nta)
            for i in range(len(categories)):
                model[step+1,nta_dict[nta],i,:] = m[i].dot(model[step,nta_dict[nta],i,:].transpose()).transpose()
                f.write('\n'+','.join([str(step+1),nta,categories[i],','.join(model[step+1,nta_dict[nta],i,:])]))

    f.close()

main(365)
