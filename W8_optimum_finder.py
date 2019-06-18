import csv
from datetime import datetime

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

import strategy
import utils
import W7_backtest

# Variables:

# OPEN:
	# K in 0-100
	# D in 0-100
	# K >=< D
	# simultaneous conditions

# CLOSE:
	# TP in 1-20
	# SL in 1-10

	# K in 0-100
	# D in 0-100
	# K >=< D
	# simultaneous conditions	

def make_3D_plot(x, y, z):
	fig = pyplot.figure()
	ax = Axes3D(fig)
	ax.scatter(x, y, z)
	pyplot.show()

def my_range(start, stop, step=0.5):	# stop is included
	float_list = []
	x = start
	while x <= stop:
		float_list.append(round(x, 1))
		x += step
	return float_list

def find_optimum_with_2_parameters(price_data):
	parameters_1_list = []
	parameters_2_list = []

	sl = 1	# for AAPL the best is: 1
	tp = 7.5	# for AAPL the best is: 7.5
	
	K_min = 0
	K_max = 100
	K_level = (K_min, K_max)
	D_min = 0
	D_max = 100
	D_level = (D_min, D_max)
	KD_difference = None	# K > D: 1; K == D: 0; K < D: -1; None

	profit_list = []
	for param_1 in my_range(0.5, 5, 0.5):
		for param_2 in (-1,0,1):#my_range(5, 10, 0.5):
			print(f'  Calculating param_1: {param_1}, param_2: {param_2}    ', end='\r')
			parameters_1_list.append(param_1)
			parameters_2_list.append(param_2)

			sl = param_1
			KD_difference = param_2
			profit = W7_backtest.main(price_data, sl, tp, (K_min,K_max), (D_min,D_max), KD_difference)[0]

			profit_list.append(profit)
#			print(f'param_1: {param_1}, param_2: {param_2}, profit: {profit}')
	return parameters_1_list, parameters_2_list, profit_list

def main(company):
	try:
		price_data = utils.get_price_data(company)
		x, y, z = find_optimum_with_2_parameters(price_data)
		print(x)
		print(y)
		print(z)
		make_3D_plot(x, y, z)
	except(IndexError):
		return 'no data yet'

company = 'AAPL'
main(company)

