import csv
from datetime import datetime
import logging

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from strategy import default_strategy as ds
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


def find_optimum_with_all_parameters(price_data, company):
	the_best_strategy = {}
	strategy = {}
	the_best_strategy['profit'] = 0

	parameters_1_list = []
	parameters_2_list = []
# open position conditions
	K_level_to_open = ds.K_level_to_open
	D_level_to_open = ds.D_level_to_open
	KD_difference_to_open = ds.KD_difference_to_open
# close position conditions
	stop_loss = ds.stop_loss
	take_profit = ds.take_profit
	K_level_to_close = ds.K_level_to_close
	D_level_to_close = ds.D_level_to_close
	KD_difference_to_close = ds.KD_difference_to_close
	try:
		for stop_loss in my_range(1, 3, 0.2):	# range(2,5):#my_range(0.5, 4, 0.5): # 5
			for take_profit in my_range(5, 9):	#my_range(1, 10, 1): # 9
				for K_level_to_close in (None, ):#(1,100), (1,20), (20,80), (80,100)): # 7
					for D_level_to_close in (None, ):# (1,100), (1,20), (20,80), (80,100)): # 7
						for KD_difference_to_close in (None, -1, 0, 1): # 4
							
							for K_level_to_open in (None, ): # (1,20), (20,80), (80,100)): # 6
								for D_level_to_open in (None, ): # (1,20), (20,80), (80,100)): # 6
									for KD_difference_to_open in (None, -1, 0, 1): # 4
										profit, history, buy_and_hold_profitability, capital_by_date = W7_backtest.main(price_data, 
																(K_level_to_open,
																D_level_to_open,
																KD_difference_to_open,
																stop_loss,
																take_profit,
																K_level_to_close,
																D_level_to_close,
																KD_difference_to_close
																))
										strategy['company'] = company
										strategy['profit'] = profit
										strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
										strategy['K_level_to_open'] = K_level_to_open
										strategy['D_level_to_open'] = D_level_to_open
										strategy['KD_difference_to_open'] = KD_difference_to_open
										strategy['stop_loss'] = stop_loss
										strategy['take_profit'] = take_profit
										strategy['K_level_to_close'] = K_level_to_close
										strategy['D_level_to_close'] = D_level_to_close
										strategy['KD_difference_to_close'] = KD_difference_to_close

										with open(f'!Strategies_for_{company}.csv', 'a', encoding='utf-8') as file:
											fieldnames = ['company', 'profit', 'buy_and_hold_profitability',
												'K_level_to_open', 'D_level_to_open', 'KD_difference_to_open',
												'stop_loss', 'take_profit', 'K_level_to_close', 'D_level_to_close', 'KD_difference_to_close']
											writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
											writer.writerow(strategy)
										
										if profit > the_best_strategy['profit']:
											the_best_strategy['profit'] = profit
											the_best_strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
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


def main(company):
	# try:
	price_data = utils.get_price_data(company)
	the_best_strategy = find_optimum_with_all_parameters(price_data, company)
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
	for x in ('TSLA', ):#{'SPY', 'F', 'MS', 'GM', 'TSLA', 'GE', 'AMD', 'MU'}:
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

