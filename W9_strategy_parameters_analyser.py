import csv
from datetime import datetime
import logging

import matplotlib.pyplot as plt

import settings

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 


def get_all_strategies(company, bar_size):
	all_strategies = []
	with open(f'!Strategies_for_{company} {bar_size}.csv', 'r', encoding='utf-8') as file:
		for x in csv.DictReader(file, delimiter=';'):
			if float(x['profit']) >= 0:
				x['Stoch_period'] = str(eval(x['Stoch_parameters'])[0])
				x['Stoch_slow_D'] = str(eval(x['Stoch_parameters'])[1])
				x['Stoch_fast_K'] = str(eval(x['Stoch_parameters'])[2])
				x.pop('Stoch_parameters')
				if x['bar_size'] == bar_size:
					all_strategies.append(x)
	for strategy in all_strategies:
		for key, value in strategy.items():
			if value != '' and key != 'bar_size' and key != 'company' and 'Weekday' not in key and key != 'Indicators_combination':
				strategy[key] = eval(value)
			if value == '':
				strategy[key] = -3
	return all_strategies


def draw_scatter(x_y_param_tuple, index, fig):
	ax = fig.add_subplot(4, 4, index)
	ax.scatter(x_y_param_tuple[0], x_y_param_tuple[1], s=0.3)
	ax.set_xlabel(x_y_param_tuple[2])
	ax.set_ylabel('Profit')
	ax.grid(True)
	return ax


def draw_plot(x_y_param_tuple, index, fig):
	ax = fig.add_subplot(4, 4, index)
	ax.plot(x_y_param_tuple[0], x_y_param_tuple[1], linewidth=0.7)
	ax.set_xlabel(x_y_param_tuple[2])
	ax.set_ylabel('Profit')
	ax.grid(True)
	return ax


def make_scatters(parameter, all_strategies):
	if 'level' not in parameter:
		x_vars = []
		y_vars = []
		for strategy in all_strategies:
			x_vars.append(strategy.get(parameter))
			y_vars.append(int(strategy.get('profit')))
		return (x_vars, y_vars, parameter)
	if 'level' in parameter:
		x_vars = []
		y_vars = []
		for strategy in all_strategies:
			x_vars.append(strategy[parameter])
			y_vars.append(int(strategy['profit']))
		new_x_vars = []
		new_y_vars = []
		for i, val in enumerate(x_vars):
			if val == -3:
				new_x_vars.append(val)
				new_y_vars.append(y_vars[i])
			if 	val != -3:
				j = 0
				while val[0]+j <= val[1]:
					new_x_vars.append(val[0]+j)
					new_y_vars.append(y_vars[i])
					j += 1
		return (new_x_vars, new_y_vars, parameter)


def make_points_for_plot(parameter, all_strategies):
	x_vars = []
	y_vars = []
	scatters = {}
	for strategy in all_strategies:
		x = scatters.get(strategy[parameter], None)
		if x == None:
			scatters[strategy[parameter]] = int(strategy['profit'])
		else:
			if scatters[strategy[parameter]] < int(strategy['profit']):
				scatters[strategy[parameter]] = int(strategy['profit'])
	for x, y in sorted(scatters.items(), key=lambda item:item[0]):
		x_vars.append(x)
		y_vars.append(y)
	return (x_vars, y_vars, parameter)


def main(company, bar_size):
	all_strategies = get_all_strategies(company, bar_size)
	fig = plt.figure()

	ax1 = draw_scatter(make_scatters('Indicators_combination', all_strategies), 1, fig)
	ax2 = draw_scatter(make_scatters('K_level_to_buy', all_strategies), 2, fig)
	ax3 = draw_scatter(make_scatters('D_level_to_buy', all_strategies), 3, fig)
	ax4 = draw_scatter(make_scatters('KD_difference_to_buy', all_strategies), 4, fig)
	ax5 = draw_scatter(make_scatters('stop_loss', all_strategies), 5, fig)
	ax6 = draw_scatter(make_scatters('take_profit', all_strategies), 6, fig)
	ax7 = draw_scatter(make_scatters('K_level_to_sell', all_strategies), 7, fig)
	ax8 = draw_scatter(make_scatters('D_level_to_sell', all_strategies), 8, fig)
	ax9 = draw_scatter(make_scatters('KD_difference_to_sell', all_strategies), 9, fig)
	ax10 = draw_scatter(make_scatters('Stoch_period', all_strategies), 10, fig)
	ax11 = draw_scatter(make_scatters('Stoch_slow_D', all_strategies), 11, fig)
	ax12 = draw_scatter(make_scatters('Stoch_fast_K', all_strategies), 12, fig)
	ax13 = draw_scatter(make_scatters('Weekday_buy', all_strategies), 13, fig)
	ax14 = draw_scatter(make_scatters('Weekday_sell', all_strategies), 14, fig)
	ax15 = draw_scatter(make_scatters('Volume_profile_locator', all_strategies), 15, fig)
	ax16 = draw_scatter(make_scatters('Japanese_candlesticks', all_strategies), 16, fig)
	plt.show()


if __name__ == '__main__':
	company = settings.company
	bar_size = '30 mins'
	main(company, bar_size)

