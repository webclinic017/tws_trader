import csv
from datetime import datetime
import logging

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from strategy import test_strategy as ts
import utils
import W7_backtest

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 


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


def find_optimum_with_all_parameters(price_data):
	the_best_strategy = {}
	the_best_strategy['profit'] = 0

	parameters_1_list = []
	parameters_2_list = []
# open position conditions
	K_level_to_open = ts.K_level_to_open
	D_level_to_open = ts.D_level_to_open
	KD_difference_to_open = ts.KD_difference_to_open
# close position conditions
	stop_loss = ts.stop_loss
	take_profit = ts.take_profit
	K_level_to_close = ts.K_level_to_close
	D_level_to_close = ts.D_level_to_close
	KD_difference_to_close = ts.KD_difference_to_close
	try:
		for stop_loss in range(2,5):#my_range(0.5, 4, 0.5): # 5
			for take_profit in range(6,9):	#my_range(1, 10, 1): # 9
				for K_level_to_close in (None, (1,100), (1,20), (20,80), (80,100)): # 7
					for D_level_to_close in (None, (1,100), (1,20), (20,80), (80,100)): # 7
						for KD_difference_to_close in (None, -1, 0, 1): # 4
							
							for K_level_to_open in (None, (1,20), (20,80), (80,100)): # 6
								for D_level_to_open in (None, (1,20), (20,80), (80,100)): # 6
									for KD_difference_to_open in (None, -1, 0, 1): # 4
										profit, history, buy_and_hold_profitability, capital_by_date = W7_backtest.main(price_data, 
																K_level_to_open,
																D_level_to_open,
																KD_difference_to_open,
																stop_loss,
																take_profit,
																K_level_to_close,
																D_level_to_close,
																KD_difference_to_close
																)
										if profit > the_best_strategy['profit']:
											the_best_strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
											the_best_strategy['profit'] = profit
											the_best_strategy['K_level_to_open'] = K_level_to_open
											the_best_strategy['D_level_to_open'] = D_level_to_open
											the_best_strategy['KD_difference_to_open'] = KD_difference_to_open
											the_best_strategy['stop_loss'] = stop_loss
											the_best_strategy['take_profit'] = take_profit
											the_best_strategy['K_level_to_close'] = K_level_to_close
											the_best_strategy['D_level_to_close'] = D_level_to_close
											the_best_strategy['KD_difference_to_close'] = KD_difference_to_close
										print(f"  {the_best_strategy['profit']}% vs. {buy_and_hold_profitability}%. Calculating: {stop_loss}, {take_profit}, {K_level_to_close}, {D_level_to_close}, {KD_difference_to_close}, {K_level_to_open}, {D_level_to_open}, {KD_difference_to_open}     ", end='\r')
		print('\n')
	except(KeyboardInterrupt):
		print(the_best_strategy)
											
	return the_best_strategy


def find_optimum_with_2_parameters(price_data):
	parameters_1_list = []
	parameters_2_list = []
# open position conditions
	K_level_to_open = ts.K_level_to_open
	D_level_to_open = ts.D_level_to_open
	KD_difference_to_open = ts.KD_difference_to_open
# close position conditions
	stop_loss = ts.stop_loss
	take_profit = ts.take_profit
	K_level_to_close = ts.K_level_to_close
	D_level_to_close = ts.D_level_to_close
	KD_difference_to_close = ts.KD_difference_to_close

	profit_list = []
	for param_1 in my_range(0, 2, 0.1):
		for param_2 in my_range(7, 8, 0.2):#my_range(5, 10, 0.5):
			print(f'  Calculating param_1: {param_1}, param_2: {param_2}    ', end='\r')
			parameters_1_list.append(param_1)
			parameters_2_list.append(param_2)

			stop_loss = param_1
			take_profit = param_2

			profit, history, buy_and_hold_profitability = W7_backtest.main(price_data, 
									K_level_to_open,
									D_level_to_open,
									KD_difference_to_open,
									stop_loss,
									take_profit,
									K_level_to_close,
									D_level_to_close,
									KD_difference_to_close
									)

			profit_list.append(profit)
	make_3D_plot(parameters_1_list, parameters_2_list, profit_list)
	return parameters_1_list, parameters_2_list, profit_list, buy_and_hold_profitability


def main(company):
	# try:
	price_data = utils.get_price_data(company)
	the_best_strategy = find_optimum_with_all_parameters(price_data)
	the_best_strategy['company'] = company
	with open('!BestStrategies.csv', 'a', encoding='utf-8') as file:
		fieldnames = ['company', 'profit', 'buy_and_hold_profitability', 
			'K_level_to_open', 'D_level_to_open', 'KD_difference_to_open',
			'stop_loss', 'take_profit', 'K_level_to_close', 'D_level_to_close', 'KD_difference_to_close']
		writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
		writer.writerow(the_best_strategy)
	print(the_best_strategy, '\n')

	# except(IndexError):
	# 	print('no data yet')


if __name__ == '__main__':
	for x in {'AMZN', 'AMD', 'NVDA', 'TWTR', 'WMT', 'C', 'BA', 'EBAY', 'F', 'FB', 'GE', 
				'GM', 'GS', 'IBM', 'KO', 'MS', 'QQQ', 'AAPL'
				}:# utils.set_with_my_companies():
		try:
			print(x)
			# with open('!BestStrategies.csv', 'w', encoding='utf-8') as file:
			# 	fieldnames = ['company', 'profit', 'buy_and_hold_profitability', 
			# 				'K_level_to_open', 'D_level_to_open', 'KD_difference_to_open',
			# 				'stop_loss', 'take_profit', 'K_level_to_close', 'D_level_to_close', 'KD_difference_to_close']
			# 	writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
			# 	writer.writeheader()
			main(x)
		except(ValueError):
			print('incorrect data                         \n')
