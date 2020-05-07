import model_v5
import general_grapher
import os

metro_beta = [2.5]
nta_beta_factors = [0.25]
time = 100
outdir = '../out/'

for m_b in metro_beta:
    for n_b in nta_beta_factors:
        print('******************************************************************\n********************* nta beta factor: '+str(n_b)+' ********************\n******************************************************************')
        f = model_v5.main(time,m_b,n_b)

        newdir = outdir + 'v5/' + f
        os.makedirs(newdir)
        os.rename(outdir + f + '.csv', newdir + '/' + f + '.csv')
        os.rename(outdir + 'notes-' + f + '.txt', newdir + '/' + 'notes-' + f + '.txt')
        print('Graphing at ' + newdir)
        general_grapher.graph(newdir)
