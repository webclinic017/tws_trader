import csv
from datetime import datetime
import logging

from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter, MaxNLocator
from mpl_toolkits.mplot3d import Axes3D

import settings

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 


def make_3D_plot(x, y, z, labels, company):
	fig = pyplot.figure()

	ax = Axes3D(fig)
	if 'level' in labels[0] or 'level' in labels[1]:
		scatter_x_list = []
		scatter_y_list = []
		scatter_z_list = []
		plot_x_list = []
		plot_y_list = []
		plot_z_list = []
		for i, val in enumerate(x):
			if val == -3:
				scatter_x_list.append(x[i])
				scatter_y_list.append(y[i])
				scatter_z_list.append(z[i])
		for i, val in enumerate(y):
			if val == -3:
				scatter_x_list.append(x[i])
				scatter_y_list.append(y[i])
				scatter_z_list.append(z[i])
		for i, val in enumerate(x):
			if val != -3 and y[i] != -3:
				plot_x_list.append(x[i])
				plot_y_list.append(y[i])
				plot_z_list.append(z[i])
		# print(scatter_x_list)
		# print(scatter_y_list)
		# print(scatter_z_list)
		# print(plot_x_list)
		# print(plot_y_list)
		# print(plot_z_list)
		ax.scatter(scatter_x_list, scatter_y_list, scatter_z_list)
		if len(plot_x_list) >=4:
			for i in range(0, len(plot_x_list)-1, 2):
				ax.plot([plot_x_list[i], plot_x_list[i+1]], [plot_y_list[i], plot_y_list[i+1]], [plot_z_list[i], plot_z_list[i+1]], '#1f77b4')
		else:
			ax.plot([plot_x_list[0], plot_x_list[1]], [plot_y_list[0], plot_y_list[1]], [plot_z_list[0], plot_z_list[1]], '#1f77b4')
	if 'level' not in labels[0] and 'level' not in labels[1]: # Why 'else:' does not work?!!
	 	ax.scatter(x, y, z)

	ax.set_xlabel(labels[0])
	ax.set_ylabel(labels[1])
	ax.set_zlabel(labels[2])

	title = f'{company}: Relation between {labels[0]} and {labels[1]}'
	fig.suptitle(title)

# Create beauty ticks
	# if axes_ticks['x_ticks'] != 'default':
	# 	if axes_ticks['x_ticks'] == 'stoch level':
	# 		labels = ['no matters', '1-20', '20-80', '80-100']	# for levels
	# 	if axes_ticks['x_ticks'] == 'stoch KD cross':
	# 		labels = ['no matters', 'K<D', 'K=D', 'K>D']	# for KD crosses
	# 	def format_fn(tick_val, tick_pos):
	# 		if int(tick_val) in x:
	# 			return labels[int(tick_val)]
	# 	ax.xaxis.set_major_formatter(FuncFormatter(format_fn))
	# 	ax.xaxis.set_major_locator(MaxNLocator(integer=True))
	# if axes_ticks['y_ticks'] != 'default':
	# 	if axes_ticks['y_ticks'] == 'stoch level':
	# 		labels = ['no matters', '1-20', '20-80', '80-100']	# for levels
	# 	if axes_ticks['y_ticks'] == 'stoch KD cross':
	# 		labels = ['no matters', 'K<D', 'K=D', 'K>D']	# for KD crosses
	# 	def format_fn(tick_val, tick_pos):
	# 		if int(tick_val) in y:
	# 			return labels[int(tick_val)]
	# 	ax.yaxis.set_major_formatter(FuncFormatter(format_fn))
	# 	ax.yaxis.set_major_locator(MaxNLocator(integer=True))
	
	pyplot.show()


def find_relation_between_each_2_parameters(all_strategies, best_strategy, company):
	x_list = []
	y_list = []
	z_list = []
	i = 1
	
	all_parameters_combinations = []
	repeats = []
	for key_x in best_strategy.keys():
		repeats.append(key_x)
		for key_y in best_strategy.keys():
			if key_y not in repeats:
				all_parameters_combinations.append((key_x, key_y))
	# for combination in all_parameters_combinations:
	# 	print(combination)
		
	parameters_vars = {}
	for parameter in best_strategy.keys():
		set_of_vars = set()
		for strategy in all_strategies:
			set_of_vars.add(strategy[0][parameter])
		parameters_vars[parameter] = set_of_vars
	# print(parameters_vars)
	
	for combination in all_parameters_combinations:
		for x_var in parameters_vars[combination[0]]:
			for y_var in parameters_vars[combination[1]]:
				strategy = best_strategy.copy()
				strategy[combination[0]] = x_var
				strategy[combination[1]] = y_var
				for strategy_and_profit in all_strategies:
					if strategy == strategy_and_profit[0]:
						x_list.append(x_var)
						y_list.append(y_var)
						z_list.append(strategy_and_profit[1])
						#print(strategy, combination2[0])

						#print('Combination:', combination, 'x:', x_var, 'y:', y_var, 'z:', strategy_and_profit[1])
		print(f'Graph #{i}: {combination[0]} vs. {combination[1]}')
		i += 1
		# print('X-list:', len(x_list), x_list[:11])
		# print('Y-list:', len(y_list), y_list[:11])
		# print('Z-list:', len(z_list), z_list[:11],'\n')
	
		labels = (combination[0], combination[1], 'Profit')
		# if level is X axe
		if 'level' in labels[0] and 'level' not in labels[1]:
			new_x_list = []
			new_y_list = []
			new_z_list = []
			for i in range(0, len(x_list)):
				if x_list[i] == -3:
					new_x_list.append(x_list[i])
					new_y_list.append(y_list[i])
					new_z_list.append(z_list[i])
			for i in range(0, len(x_list)):
				if x_list[i] != -3:
					new_x_list.append(x_list[i][0])
					new_x_list.append(x_list[i][1])
					new_y_list.append(y_list[i])
					new_y_list.append(y_list[i])
					new_z_list.append(z_list[i])
					new_z_list.append(z_list[i])
			x_list = new_x_list
			y_list = new_y_list
			z_list = new_z_list

		# if level is Y axe
		if 'level' not in labels[0] and 'level' in labels[1]:
			new_x_list = []
			new_y_list = []
			new_z_list = []
			for i in range(0, len(y_list)):
				if y_list[i] == -3:
					new_x_list.append(x_list[i])
					new_y_list.append(y_list[i])
					new_z_list.append(z_list[i])
			for i in range(0, len(y_list)):
				if y_list[i] != -3:
					new_x_list.append(x_list[i])
					new_x_list.append(x_list[i])
					new_y_list.append(y_list[i][0])
					new_y_list.append(y_list[i][1])
					new_z_list.append(z_list[i])
					new_z_list.append(z_list[i])
			x_list = new_x_list
			y_list = new_y_list
			z_list = new_z_list

		# if level are X and Y axes
		if 'level' in labels[0] and 'level' in labels[1]:
			new_x_list = []
			new_y_list = []
			new_z_list = []
			for i in range(0, len(x_list)):
				if x_list[i] != -3 and y_list[i] != -3:
					new_x_list.append(x_list[i][0])
					new_x_list.append(x_list[i][1])
					new_y_list.append(y_list[i][0])
					new_y_list.append(y_list[i][1])
					new_z_list.append(z_list[i])
					new_z_list.append(z_list[i])
			for i, val in enumerate(x_list):
				if val == -3:
					if y_list[i] != -3:
						new_x_list.append(x_list[i])
						new_x_list.append(x_list[i])
						new_y_list.append(y_list[i][0])
						new_y_list.append(y_list[i][1])
						new_z_list.append(z_list[i])
						new_z_list.append(z_list[i])
					else:
						new_x_list.append(x_list[i])
						new_y_list.append(y_list[i])
						new_z_list.append(z_list[i])
			for i, val in enumerate(y_list):
				if val == -3:
					if x_list[i] != -3:
						new_x_list.append(x_list[i][0])
						new_x_list.append(x_list[i][1])
						new_y_list.append(y_list[i])
						new_y_list.append(y_list[i])
						new_z_list.append(z_list[i])
						new_z_list.append(z_list[i])
			x_list = new_x_list
			y_list = new_y_list
			z_list = new_z_list

		# print(x_list)
		# print(y_list)
		# print(z_list)


		make_3D_plot(x_list, y_list, z_list, labels, company)
		x_list = []
		y_list = []
		z_list = []


def all_strategies_maker(company):
	all_strategies = []
	with open(f'!Strategies_for_{company}.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			strategy = {}
			for parameter in choosen.parameters:
				if parameter:
					strategy[parameter[0]] = x[parameter[1]]
			for key, value in strategy.items():
				if value != '':
					strategy[key] = eval(value)
				else:
					strategy[key] = -3
			for key, value in strategy.items():
				if key == 'Stoch_period':
					strategy['Stoch_period'] = value[0]
				if key == 'Stoch_slow_D':
					strategy['Stoch_slow_D'] = value[1]
				if key == 'Stoch_fast_K':
					strategy['Stoch_fast_K'] = value[2]
			all_strategies.append((strategy, float(x[1])))
	return all_strategies


def the_best_known_strategy(company):
	the_best_strategy = {}
	with open(f'!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				for parameter in choosen.parameters:
					if parameter:
						the_best_strategy[parameter[0]] = x[parameter[1]]
	for key, value in the_best_strategy.items():
		if value != '':
			the_best_strategy[key] = eval(value)
		else:
			the_best_strategy[key] = -3
	for key, value in the_best_strategy.items():
		if key == 'Stoch_period':
			the_best_strategy['Stoch_period'] = value[0]
		if key == 'Stoch_slow_D':
			the_best_strategy['Stoch_slow_D'] = value[1]
		if key == 'Stoch_fast_K':
			the_best_strategy['Stoch_fast_K'] = value[2]

	return the_best_strategy


class choosen:
	K_level_to_buy = False	# ('K_level_to_buy', 4)
	D_level_to_buy = False	# ('D_level_to_buy', 5)	# False	# 
	KD_difference_to_buy = False 	#	('KD_difference_to_buy', 6)
	stop_loss = 	('stop_loss', 7)
	take_profit = ('take_profit', 8)
	K_level_to_sell = False	# ('K_level_to_sell', 9)
	D_level_to_sell = False	#('D_level_to_sell', 10)	#False	# 
	KD_difference_to_sell = False	# ('KD_difference_to_sell', 11)	#False		#
	Stoch_period =  False	#	('Stoch_period', 12)
	Stoch_slow_D = False	#	(('Stoch_slow_D', 12)
	Stoch_fast_K = False	#	('Stoch_fast_K', 12)
	parameters = (K_level_to_buy, D_level_to_buy, KD_difference_to_buy,
				stop_loss, take_profit, K_level_to_sell, D_level_to_sell, KD_difference_to_sell,
				Stoch_period, Stoch_slow_D, Stoch_fast_K)


def main(company):
	the_best_strategy = the_best_known_strategy(company)
	all_strategies = all_strategies_maker(company)
	#print(all_strategies[0])
	#print(the_best_strategy)
	find_relation_between_each_2_parameters(all_strategies, the_best_strategy, company)


if __name__ == '__main__':
	company = settings.company
	main(company)

