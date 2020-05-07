import model_v4

metro_beta = 2.5
nta_beta_factors = [0.3,0.5,0.8,1]

for beta in nta_beta_factors:
    print('******************************************************************\n**************************** nta beta factor: '+str(beta)+' ***************************\n******************************************************************')
    model_v4.main(100,metro_beta,beta)
