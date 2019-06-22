import csv
from datetime import datetime
import json
import logging

from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter, MaxNLocator
from mpl_toolkits.mplot3d import Axes3D

import utils
import W7_backtest
from W8_optimum_finder import ranges

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 


def make_3D_plot(x, y, z, labels, company, axes_ticks={'x_ticks':'default', 'y_ticks': 'default'}):
	fig = pyplot.figure()

	ax = Axes3D(fig)
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


def find_relation_between_each_2_parameters(all_strategies, best_params, company):
	x_list = []
	y_list = []
	z_list = []
	i = 1
	parameters = best_params[0]

	repeats = []
	axes_ticks={'x_ticks':'default', 'y_ticks': 'default'}
	
	all_parameters_combinations = []
	for x_index in range(len(parameters)):# range(2):	#
		repeats.append(x_index)
		for y_index in range(len(parameters)):	# range(2): #
			if x_index != y_index and y_index not in repeats:
					all_parameters_combinations.append(({parameters[x_index]:x_index}, {parameters[y_index]:y_index}))
	print(best_params[1])
	print(all_strategies[0])
	for combination in all_parameters_combinations:
		print(combination)
		
	parameters_vars = {}
	for x in range(0, len(parameters)):
		parameters_vars[parameters[x]] = set(row[x] for row in all_strategies)
	print(parameters_vars)
	
	x = 0
	y = 1
	
	viewing_strategies = set()
	strategy = best_params[1].copy()
	#for x in range(0, len(parameters)):
	for parameter_value in parameters_vars[parameters[0]]:
		strategy.pop(0)
		strategy.insert(0, parameter_value)
		viewing_strategies.add(tuple(strategy))

	for parameter_value in parameters_vars[parameters[1]]:
		strategy.pop(1)
		strategy.insert(1, parameter_value)
		viewing_strategies.add(tuple(strategy))	
	# for y in range(0, len(parameters)):
	# 	for parameter_value in parameters_vars[parameters[y]]:
	# 		strategy.pop(0)
	# 		strategy.insert(y, parameter_value)
	# 		viewing_strategies.add(tuple(strategy))
	for strat in viewing_strategies:
		print(strat)

	for strat in viewing_strategies:
		for strategy in all_strategies:
			print(tuple(strategy), strat)
			if tuple(strategy) == strat:
				print(strategy, all_strategies.index(strategy))
	


	# 			for x in x_vars:
	# 				strategy = best_params[1].copy()
	# 				strategy = list(strategy)
	# 				strategy.pop(x_index)
	# 				strategy.insert(x_index, x)
	# 				for y in y_vars:
	# 					strategy = list(strategy)
	# 					strategy.pop(y_index)
	# 					strategy.insert(y_index, y)
	# 					strategy = tuple(strategy)
	# 					viewing_strategies.add(strategy)


	# for relation in all_parameters_combinations:






	
	# print(x_vars)
	# print(y_vars)
				
	# 			x_vars = set()
	# 			y_vars = set()
	# 			for row in all_strategies:
	# 				x_vars.add(row[x_index])
	# 				y_vars.add(row[y_index])
				
	# 			viewing_strategies = set()
	# 			for x in x_vars:
	# 				strategy = best_params[1].copy()
	# 				strategy = list(strategy)
	# 				strategy.pop(x_index)
	# 				strategy.insert(x_index, x)
	# 				for y in y_vars:
	# 					strategy = list(strategy)
	# 					strategy.pop(y_index)
	# 					strategy.insert(y_index, y)
	# 					strategy = tuple(strategy)
	# 					viewing_strategies.add(strategy)
	

	# 			# print(best_params[1])
	# 			# print(viewing_strategies)
	# 			for strategy in viewing_strategies:
	# 				for row in all_strategies:
	# 					print('Stratege:', strategy)
	# 					print('Row:', row[4:-1])
	# 					if tuple(strategy) == row[4:-1]:
	# 						print('Found:', row[1])
	# 						z_list.append(float(row[1]))
	# 			# if x level
	# 						if 'level' in parameters[x_index]:
	# 							axes_ticks['x_ticks'] = 'stoch level'
	# 							if strategy[x_index] == '' or strategy[x_index] == '(1, 100)':
	# 								x_list.append(0)
	# 							if strategy[x_index] == '(1, 10)':
	# 								x_list.append(1)
	# 							if strategy[x_index] == '(10, 20)':
	# 								x_list.append(2)
	# 							if strategy[x_index] == '(20, 30)':
	# 								x_list.append(3)
	# 			# x KD
	# 						if 'KD_difference_to' in parameters[x_index]:
	# 							axes_ticks['x_ticks'] = 'stoch KD cross'
	# 							if strategy[x_index] == '':
	# 								x_list.append(-2)
	# 							else:
	# 								x_list.append(int(strategy[x_index]))
	# 						if 'stop_loss' in parameters[x_index] or 'take_profit' in parameters[x_index]:
	# 							#print('I want to add: ', strategy[x_index])
	# 							x_list.append(float(strategy[x_index]))
	# 			# if y level
	# 						if 'level' in parameters[y_index]:
	# 							axes_ticks['y_ticks'] = 'stoch level'
	# 							if strategy[y_index] == '' or strategy[y_index] == '(1, 100)':
	# 								y_list.append(0)
	# 							if strategy[y_index] == '(1, 10)':
	# 								y_list.append(1)
	# 							if strategy[y_index] == '(10, 20)':
	# 								y_list.append(2)
	# 							if strategy[y_index] == '(20, 30)':
	# 								y_list.append(3)
	# 			# y KD
	# 						if 'KD_difference_to' in parameters[y_index]:
	# 							axes_ticks['y_ticks'] = 'stoch KD cross'
	# 							if strategy[y_index] == '':
	# 								y_list.append(-2)
	# 							else:
	# 								y_list.append(int(strategy[y_index]))
	# 						if 'stop_loss' in parameters[y_index] or 'take_profit' in parameters[y_index]:
	# 							y_list.append(float(strategy[y_index]))
	# 			print(f'Graph #{i}: {parameters[x_index]} vs. {parameters[y_index]}')
	# 			i += 1
	# 			print('X-list:', len(x_list), x_list[:11])
	# 			print('Y-list:', len(y_list), y_list[:11])
	# 			print('Z-list:', len(z_list), z_list[:11],'\n')
				
	# 			labels = (parameters[x_index], parameters[y_index], 'Profit')
	# 			#make_3D_plot(x_list, y_list, z_list, labels, company, axes_ticks)
	# 			x_list = []
	# 			y_list = []
	# 			z_list = []


def list_of_lists_with_title_and_the_best_strategy_values():
	strategy = utils.the_best_known_strategy('TSLA')
	best_params = []
	best_params.append((
						#'K_level_to_buy',
						#'D_level_to_buy',
						#'KD_difference_to_buy'
						'stop_loss',
						'take_profit',
						#'K_level_to_sell',
						#'D_level_to_sell',
						#'KD_difference_to_sell',
						'Stoch period',
						'Stoch slow avg (D)',
						'Stoch fast avg (K)'
						))
	best_params.append([
						#strategy['K_level_to_buy'],
						#strategy['D_level_to_buy'],
						#strategy['KD_difference_to_buy'],
						strategy['stop_loss'],
						strategy['take_profit'],
						#strategy['K_level_to_sell'],
						#strategy['D_level_to_sell'],
						#strategy['KD_difference_to_sell'],
						strategy['Stoch_parameters'][0],
						strategy['Stoch_parameters'][1],
						strategy['Stoch_parameters'][2]
						])
	return best_params


def all_strategies_maker():
	all_strategies_raw = None
	with open(f'!Strategies_for_{company}.json', 'r', encoding='utf-8') as file:
		all_strategies_raw = json.load(file)



	# 	tuple(tuple(x) for x in csv.reader(file, delimiter=';'))
	


	# all_strategies = tuple([#row[4],
	# 						#row[5],
	# 						#row[6],
	# 						row[7],
	# 						row[8],
	# 						#row[9],
	# 						#row[10],
	# 						#row[11],
	# 						row[12][0],
	# 						row[12][1],
	# 						row[12][2]] for row in all_strategies_raw
	# 						)
		
	print(all_strategies_raw)
	# for row in all_strategies:
	# 	for n, i in enumerate(row):
	# 		if i == '':
	# 			row[n] = -10
	# 		# else:
	# 		# 	# try:
	# 		# 	row[n] = eval(i)
	# 		# 	# except:
	# 			# 	pass
	# 			# 	#print(i)



	return all_strategies_raw


def main(company):



	best_params = list_of_lists_with_title_and_the_best_strategy_values()
	all_strategies = all_strategies_maker()
	
	# print(best_params)
	# print(all_strategies[:11])
	


	#find_relation_between_each_2_parameters(all_strategies, best_params, company)


if __name__ == '__main__':
	company = 'TSLA'
	main(company)


