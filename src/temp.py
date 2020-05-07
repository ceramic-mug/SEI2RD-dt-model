import os
import general_grapher

newdir = outdir + 'v5/' + f
os.makedirs(newdir)
os.rename(outdir + f + '.csv', newdir + f + '.csv')
os.rename(outdir + 'notes-' + f + '.txt', newdir + 'notes-' + f + '.txt')
print('Graphing at ' + newdir)
general_grapher.graph(newdir)
