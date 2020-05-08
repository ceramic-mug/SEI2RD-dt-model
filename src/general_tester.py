import model_v7
import general_grapher
import os

version = 7
initial_nta_betas = [1.16]
initial_borough_betas = [1.16]
initial_metro_betas = [0.5*2.9,1.5*2.9]
lockdown_factor = 0.2
time = 365
outdir = '../out/'

for metro_b in initial_metro_betas:
    for nta_b in initial_nta_betas:
        for borough_b in initial_borough_betas:
            print('Initial betas:')
            print('metro: '+str(metro_b))
            print('nta: '+str(nta_b))
            print('borough: '+str(borough_b))

            f = model_v7.main(time,metro_b,nta_b,borough_b,lockdown_factor)

            newdir = outdir + 'v'+str(version)+'/' + f
            os.makedirs(newdir)
            os.rename(outdir + f + '.csv', newdir + '/' + f + '.csv')
            os.rename(outdir + 'notes-' + f + '.txt', newdir + '/' + 'notes-' + f + '.txt')
            print('Graphing at ' + newdir)
            general_grapher.graph(newdir)
