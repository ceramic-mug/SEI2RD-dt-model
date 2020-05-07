import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# where will I find the input file
in_folder = '/Users/joshua/Documents/School/Princeton/Sophomore Classes/Spring 2020/CEE302/term_project/SEI2RD-dt-model/out/'

# what's the name of the input file we currently care about
in_file = '2020-05-05'

# create a new output folder for graphics we produce
out_dir = in_folder+in_file+'/'

if not os.path.exists(out_dir):
    os.makedirs(out_dir)

# Read in the data
if os.path.exists(in_folder+in_file+'.csv'):
    filename = in_folder+in_file+'.csv'
else:
    filename = out_dir+in_file+'.csv'
dat = pd.read_csv(filename)

# Move the file to the newly created folder
os.rename(filename, out_dir+in_file+'.csv')

dat.head()

# let's make an infected over time plot
timesteps = dat.step.values[-1]
timesteps

total_seird = np.zeros([timesteps+1,5])

for step in range(timesteps+1):
    total_seird[step,0] = sum(dat[dat.step==step].s)
    total_seird[step,1] = sum(dat[dat.step==step].e)
    total_seird[step,2] = sum(dat[dat.step==step]['is'])+sum(dat[dat.step==step].ia)
    total_seird[step,3] = sum(dat[dat.step==step].r)
    total_seird[step,4] = sum(dat[dat.step==step].d)

plt.plot(range(timesteps),-(np.diff(total_seird[:,1])+np.diff(total_seird[:,0])))
