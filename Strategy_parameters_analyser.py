import csv
from datetime import datetime
import logging

from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter, MaxNLocator
from mpl_toolkits.mplot3d import Axes3D

from strategy import test_strategy as ts
import utils
import W7_backtest

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
	for x_index in range(len(parameters)):# range(2):	#
		repeats.append(x_index)
		for y_index in range(len(parameters)):	# range(2): #
			if x_index != y_index and y_index not in repeats:
				labels = (parameters[x_index], parameters[y_index], 'Profit')
				x_vars = set()
				y_vars = set()
				for row in all_strategies:
					x_vars.add(row[x_index+3])
					y_vars.add(row[y_index+3])
				viewing_strategies = set()
				for x in x_vars:
					strategy = best_params[1].copy()
					strategy = list(strategy)
					strategy.pop(x_index)
					strategy.insert(x_index, x)
					for y in y_vars:
						strategy = list(strategy)
						strategy.pop(y_index)
						strategy.insert(y_index, y)
						strategy = tuple(strategy)
						viewing_strategies.add(strategy)

				for strategy in viewing_strategies:
					for row in all_strategies:
						if tuple(strategy) == row[3:]:
							z_list.append(float(row[1]))
				# if x level
							if 'level' in parameters[x_index]:
								axes_ticks['x_ticks'] = 'stoch level'
								if strategy[x_index] == '' or strategy[x_index] == '(1, 100)':
									x_list.append(0)
								if strategy[x_index] == '(1, 20)':
									x_list.append(1)
								if strategy[x_index] == '(20, 80)':
									x_list.append(2)
								if strategy[x_index] == '(80, 100)':
									x_list.append(3)
				# x KD
							if 'KD difference to' in parameters[x_index]:
								axes_ticks['x_ticks'] = 'stoch KD cross'
								if strategy[x_index] == '':
									x_list.append(-2)
								else:
									x_list.append(int(strategy[x_index]))
							if 'Stop' in parameters[x_index] or 'Take' in parameters[x_index]:
								x_list.append(float(strategy[x_index]))
				# if y level
							if 'level' in parameters[y_index]:
								axes_ticks['y_ticks'] = 'stoch level'
								if strategy[y_index] == '' or strategy[y_index] == '(1, 100)':
									y_list.append(0)
								if strategy[y_index] == '(1, 20)':
									y_list.append(1)
								if strategy[y_index] == '(20, 80)':
									y_list.append(2)
								if strategy[y_index] == '(80, 100)':
									y_list.append(3)
				# y KD
							if 'KD difference to' in parameters[y_index]:
								axes_ticks['y_ticks'] = 'stoch KD cross'
								if strategy[y_index] == '':
									y_list.append(-2)
								else:
									y_list.append(int(strategy[y_index]))
							if 'Stop' in parameters[y_index] or 'Take' in parameters[y_index]:
								y_list.append(float(strategy[y_index]))
				print(f'Graph #{i}: {parameters[x_index]} vs. {parameters[y_index]}')
				i += 1
				# print('X-list:', len(x_list), x_list)
				# print('Y-list:', len(y_list), y_list)
				# print('Z-list:', len(z_list), z_list,'\n')

				make_3D_plot(x_list, y_list, z_list, labels, company, axes_ticks)
				x_list = []
				y_list = []
				z_list = []

def main(company):
	
	all_strategies = None
	with open(f'!Strategies_for_{company}.csv', 'r', encoding='utf-8') as file:
		all_strategies = tuple(tuple(x) for x in csv.reader(file, delimiter=';'))
	
	best_params = None
	with open('!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				best_params = (('K level to open',
								'D level to open',
								'KD difference to open',
								'Stop loss',
								'Take profit',
								'K level to close',
								'D level to close',
								'KD difference to close'),
								[x[3], x[4], x[5], x[6], x[7], x[8], x[9], x[10]
								])

	find_relation_between_each_2_parameters(all_strategies, best_params, company)


if __name__ == '__main__':
	company = 'TSLA'
	main(company)


