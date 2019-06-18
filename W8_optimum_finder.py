import csv
from datetime import datetime

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from strategy import test_strategy as t
import utils
import W7_backtest

import logging 
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 

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
# open position conditions
	K_level_to_open = t.K_level_to_open
	D_level_to_open = t.D_level_to_open
	KD_difference_to_open = t.KD_difference_to_open
# close position conditions
	stop_loss = t.stop_loss
	take_profit = t.take_profit
	K_level_to_close = t.K_level_to_close
	D_level_to_close = t.D_level_to_close
	KD_difference_to_close = t.KD_difference_to_close

	profit_list = []
	for param_1 in my_range(0, 2, 0.1):
		for param_2 in my_range(7, 8, 0.2):#my_range(5, 10, 0.5):
			print(f'  Calculating param_1: {param_1}, param_2: {param_2}    ', end='\r')
			parameters_1_list.append(param_1)
			parameters_2_list.append(param_2)

			stop_loss = param_1
			take_profit = param_2

			profit, history, buy_and_hold_profitability = W7_backtest.main(price_data, 
									stop_loss,
									take_profit,
									K_level_to_open,
									D_level_to_open,
									KD_difference_to_open,
									K_level_to_close,
									D_level_to_close,
									KD_difference_to_close
									)

			profit_list.append(profit)
#			print(f'param_1: {param_1}, param_2: {param_2}, profit: {profit}')
	return parameters_1_list, parameters_2_list, profit_list, buy_and_hold_profitability

def main(company):
	try:
		price_data = utils.get_price_data(company)
		x, y, z, buy_and_hold_profitability = find_optimum_with_2_parameters(price_data)
		print(x)
		print(y)
		print(z)
		make_3D_plot(x, y, z)
		print(f'\nBuy and hold profit: {buy_and_hold_profitability}%')
	except(IndexError):
		return 'no data yet'

company = 'AAPL'
main(company)

