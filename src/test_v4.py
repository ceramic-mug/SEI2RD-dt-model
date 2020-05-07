import model_v4
import general_grapher
import os

metro_beta = 2.5
nta_beta_factors = 0.5
time = 365

for beta in nta_beta_factors:
    print('******************************************************************\n********************* nta beta factor: '+str(beta)+' ********************\n******************************************************************')
    model_v4.main(time,metro_beta,beta)
