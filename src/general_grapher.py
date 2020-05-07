import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
import math as m


def graph(rootdir):

    dat = pd.read_csv(glob.glob(rootdir+'/*.csv')[0])

    time = [i for i in np.unique(dat['step'].values)]

    total_has_been_infected = np.zeros(len(time))
    total_has_been_symptomatic = np.zeros(len(time))
    daily_new_infected = np.zeros(len(time))
    daily_new_symptomatic = np.zeros(len(time))

    boxes = ['s','e','is','ia','r','d']

    # summative seird
    seird = np.zeros([len(time),len(boxes)])
    for timestep in time:
        for box in range(len(boxes)):
            seird[timestep,box] = sum(dat[dat['step']==timestep][boxes[box]])

    # differentials
    diffs = {}
    for index, box in enumerate(boxes):
        diffs[box] = np.diff(seird[:,index])

    ######## total has been infected, symptomatic, asymptomatic by each timestep ############
    # calculating total has been infected at every timestep
    flux_into_infected_boxes = -diffs['e']-diffs['s']
    total_has_been_infected[0] = sum((seird[0,2],seird[0,3]))
    for timestep in np.array(time[1:]):
        total_has_been_infected[timestep] = total_has_been_infected[timestep-1]+flux_into_infected_boxes[timestep-1]

    flux_into_symptomatic_boxes = flux_into_infected_boxes*(diffs['is']/(diffs['is']+diffs['ia']))
    total_has_been_symptomatic[0] = seird[0,2]
    for timestep in np.array(time[1:]):
        total_has_been_symptomatic[timestep] = total_has_been_symptomatic[timestep-1]+flux_into_symptomatic_boxes[timestep-1]

    flux_into_asymptomatic_boxes = flux_into_infected_boxes*(diffs['ia']/(diffs['is']+diffs['ia']))
    total_has_been_asymptomatic = np.zeros(len(time))
    total_has_been_symptomatic[0] = seird[0,3]
    for timestep in np.array(time[1:]):
        total_has_been_asymptomatic[timestep] = total_has_been_asymptomatic[timestep-1]+flux_into_asymptomatic_boxes[timestep-1]

    ############## daily new infected, symptomatic, and asymptomatic

    daily_new_infected[0] = sum((seird[0,2],seird[0,3]))
    for timestep in np.array(time[1:]):
        daily_new_infected[timestep] = flux_into_infected_boxes[timestep-1]

    daily_new_symptomatic[0] = seird[0,2]
    for timestep in np.array(time[1:]):
        daily_new_symptomatic[timestep] = flux_into_symptomatic_boxes[timestep-1]

    ####### Create and save figures #######

    outdir = rootdir + '/graphs/'
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    ##### total has been infected
    tot_infected = plt.figure(figsize=[7,4],dpi=300)

    plt.plot(time,total_has_been_infected,
            label='Total Cases',
            linewidth = 2,
            color = '#B22222',
            figure=tot_infected)

    plt.xlabel('Time (days)')
    plt.ylabel('Total Cases')
    plt.title('Total Cases (I)')

    plt.legend()
    tot_infected.savefig(outdir+'total_cases_v_time.png')
    plt.close()

    ##### total symptomatic,asymptomatic,dead
    tot_sad = plt.figure(figsize=[7,4],dpi=300)

    plt.plot(time,total_has_been_symptomatic,
            label='Total symptomatic cases',
            linewidth = 2,
            color = '#B22222',
            figure=tot_sad)

    plt.plot(time,total_has_been_asymptomatic,
            label='Total asymptomatic cases',
            linewidth = 2,
            color = '#4682B4',
            figure=tot_sad)

    plt.xlabel('Time (days)')
    plt.ylabel('Total Cases')
    plt.title('Total Symptomatic and Asymptomatic (Is, Ia)')

    plt.legend()
    tot_sad.savefig(outdir+'symptomatic_asymptomatic.png')
    plt.close()

    ##### daily new infected

    di = plt.figure(figsize=[7,4],dpi=300)

    plt.bar(time,daily_new_infected,
            label='Daily New Cases',
            fc = '#B22222',
            figure=di)

    plt.xlabel('Time (days)')
    plt.ylabel('New Cases')
    plt.title('Daily New Cases (I)')

    plt.legend()
    di.savefig(outdir+'daily_cases.png')
    plt.close()

    ##### LOG daily new infected

    di = plt.figure(figsize=[7,4],dpi=300)

    plt.bar(time,daily_new_infected,
            label='Daily New Cases',
            fc = '#B22222',
            figure=di)

    plt.xlabel('Time (days)')
    plt.ylabel('New Cases')
    plt.title('Log Daily New Cases (I)')
    plt.yscale('log')

    plt.legend()
    di.savefig(outdir+'log_daily_cases.png')
    plt.close()
    ##### daily new symptomatic

    ds = plt.figure(figsize=[7,4],dpi=300)

    plt.bar(time,daily_new_symptomatic,
            label='Daily New Symptomatic',
            fc = '#800000',
            figure=ds)

    plt.xlabel('Time (days)')
    plt.ylabel('New Cases')
    plt.title('Daily New Symptomatic Cases (Is)')

    plt.legend()
    ds.savefig(outdir+'daily_symptomatic.png')
    plt.close()
