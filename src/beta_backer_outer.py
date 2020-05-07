import model_with_government_restrictions

betas = [0.5,1,1.5,2,2.5]

for beta in betas:
    print('******************************************************************\n**************************** beta: '+str(beta)+' ***************************\n******************************************************************')
    model_with_government_restrictions.main(365,beta)
