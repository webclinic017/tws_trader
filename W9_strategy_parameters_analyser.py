import csv
from datetime import datetime
import logging

import matplotlib.pyplot as plt

import settings

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 

def main(company):
	fig = plt.figure()

	ax1 = fig.add_subplot(4, 3, 1)
	ax2 = fig.add_subplot(4, 3, 2)
	ax3 = fig.add_subplot(4, 3, 3)
	ax4 = fig.add_subplot(4, 3, 4)
	ax5 = fig.add_subplot(4, 3, 5)
	ax6 = fig.add_subplot(4, 3, 6)
	ax7 = fig.add_subplot(4, 3, 7)
	ax8 = fig.add_subplot(4, 3, 8)
	ax9 = fig.add_subplot(4, 3, 9)
	ax10 = fig.add_subplot(4, 3, 10)
	ax11 = fig.add_subplot(4, 3, 11)
	ax12 = fig.add_subplot(4, 3, 12)

	all_strategies = []
	with open(f'!Strategies_for_{company}.csv', 'r', encoding='utf-8') as file:
		for x in csv.DictReader(file, delimiter=';'):
			if float(x['profit']) >= 140:
				all_strategies.append(x)
	for strategy in all_strategies:
		for key, value in strategy.items():
			if value != '' and key != 'bar_size' and key != 'company':
				strategy[key] = eval(value)
			if value == '':
				strategy[key] = -3

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['bar_size'])
		y_vars.append(strategy['profit'])
	ax1.scatter(x_vars, y_vars, s=0.3)
	ax1.set_xlabel('bar_size')
	ax1.set_ylabel('Profit')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['K_level_to_buy'])
		y_vars.append(int(float(strategy['profit'])))
	ax2.scatter(x_vars, y_vars, s=0.3)
	ax2.set_xlabel('K_level_to_buy')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['D_level_to_buy'])
		y_vars.append(int(float(strategy['profit'])))
	ax3.scatter(x_vars, y_vars, s=0.3)
	ax3.set_xlabel('D_level_to_buy')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['KD_difference_to_buy'])
		y_vars.append(int(float(strategy['profit'])))
	ax4.scatter(x_vars, y_vars, s=0.3)
	ax4.set_xlabel('KD_difference_to_buy')
	ax4.set_ylabel('Profit')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['stop_loss'])
		y_vars.append(int(float(strategy['profit'])))
	ax5.scatter(x_vars, y_vars, s=0.3)
	ax5.set_xlabel('stop_loss')


	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['take_profit'])
		y_vars.append(int(float(strategy['profit'])))
	ax6.scatter(x_vars, y_vars, s=0.3)
	ax6.set_xlabel('take_profit')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['K_level_to_sell'])
		y_vars.append(int(float(strategy['profit'])))
	ax7.scatter(x_vars, y_vars, s=0.3)
	ax7.set_xlabel('K_level_to_sell')
	ax7.set_ylabel('Profit')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['D_level_to_sell'])
		y_vars.append(int(float(strategy['profit'])))
	ax8.scatter(x_vars, y_vars, s=0.3)
	ax8.set_xlabel('D_level_to_sell')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['KD_difference_to_sell'])
		y_vars.append(int(float(strategy['profit'])))
	ax9.scatter(x_vars, y_vars, s=0.3)
	ax9.set_xlabel('KD_difference_to_sell')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['Stoch_parameters'][0])
		y_vars.append(int(float(strategy['profit'])))
	ax10.scatter(x_vars, y_vars, s=0.3)
	ax10.set_xlabel('Stoch')
	ax10.set_ylabel('Profit')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['Stoch_parameters'][1])
		y_vars.append(int(float(strategy['profit'])))
	ax11.scatter(x_vars, y_vars, s=0.3)
	ax11.set_xlabel('Stoch_slow_D')

	x_vars = []
	y_vars = []
	for strategy in all_strategies:
		x_vars.append(strategy['Stoch_parameters'][2])
		y_vars.append(int(float(strategy['profit'])))
	ax12.scatter(x_vars, y_vars, s=0.3)
	ax12.set_xlabel('Stoch_fast_K')

	plt.show()


if __name__ == '__main__':
	company = settings.company
	main(company)

