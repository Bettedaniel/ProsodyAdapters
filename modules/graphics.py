from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
import os.path as op
import warnings

def saveFigure(name="figure", overwrite=False):
	if not overwrite:
		version = 1
		while op.isfile(name+str(version)+'.png'):
			version += 1
		plt.savefig(name+str(version)+'.png')
	else:
		plt.savefig(name+'.png')

def blockDiagram(ratios, names=None, graphName='figure', overwrite=False, yLimit=1.0, show=False):
	ratios = np.array(ratios)
	warnings.filterwarnings("ignore", module="matplotlib")
	fig = plt.figure()
	width = 1
	ind = np.arange(len(ratios))
	plt.bar(ind, ratios, color='black', width=width)
	if names is None:
		plt.xticks(ind + width / 2, ind)
	else:
		plt.xticks(ind + width / 2, names)
	
	fig.autofmt_xdate()
	plt.xlim([0, len(ratios)])
	plt.ylim([0, yLimit])
	plt.axhline(ratios.mean(), color='blue', linewidth=2)
	saveFigure(graphName, overwrite)
	if show:
		plt.show()
#	plt.savefig("figure.png")

if __name__ == "__main__":
	blockDiagram([0.05, 0.02, 0.5, 0.09, 0.4, 0.45, 0.9, 0.1, 0.5, 0.85, 0.89, 0.88, 0.87, 0.54, 0.23, 0.12, 0.46, 0.2456, 0.687, 0.23, 0.366], overwrite=True)
