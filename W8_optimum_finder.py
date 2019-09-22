import glob
import os
import pickle
import random

import settings
import utils
import W7_backtest

POP_SIZE = 300
MAX_GENERATIONS = 1000
MUTATION_PROBABILITY = .25   # how many strategies in population will mutate

modules = glob.glob(os.path.join(os.path.dirname(__file__), 'indicators', '*.py'))
all_indicators = [os.path.basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]


class Ranges:
	bar_size = ('30 mins',)
	# TP/SL
	SL = range(21)
	TP = range(21)
	# INDICATORS:
	stochastic = {
		'K_min': range(0, 100),
		'K_max': range(100, 0, -1),
		'D_min': range(0, 100),
		'D_max': range(100, 0, -1),
		'KD_difference': ('K>D', 'K<D', 'K=D', None),
		'stoch_period': range(2, 101),
		'stoch_slow_avg': range(2, 101),
		'stoch_fast_avg': range(1, 51)
	}
	weekday = {
		'weekday': (
		1, 2, 3, 4, 5, 12, 13, 14, 15, 23, 24, 25, 34, 35, 45, 123, 124, 125, 134, 135, 145, 234, 235, 245, 345, 1234,
		2345, 1235, 1345, 1245, 12345)
	}
	japanese_candlesticks = {}
	volume_profile = {
		'locator': range(1, 100)
	}
	SMA = {
		'period': range(1, 301)
	}
	RS = {
		'ZZ_movement': (1,),     # range(1, 40),
		'close_index': (1,)     # range(1, 20)
	}
	# 	score = range(max_a+1): # this is correct, but gives us huge massive of combinations
	# 	score = (0,1,2,3,4,5,6,10,15,20,25,40,80)
	score = range(len(all_indicators) * 2 + 1)


def save_the_best_strategy(the_best_strategy):
	file_with_the_best_strategies = f'tmp_data/!BestStrategies-exp.pkl'
	# Get all of the best strategies in list
	the_best_strategies = []
	with open(file_with_the_best_strategies, 'rb') as file:
		while True:
			try:
				the_best_strategies.append(pickle.load(file))
			except EOFError:
				break
	# Replace ex-the_best_strategy to the new one:
	for i, strategy in enumerate(the_best_strategies):
		if strategy.get('company') == the_best_strategy['company']:
			del the_best_strategies[i]
			the_best_strategies.append(the_best_strategy)
	# Or write new entry:
	if the_best_strategies == []:
		the_best_strategies.append(the_best_strategy)
	# Rewrite file:
	open(file_with_the_best_strategies, 'w').close()
	for strategy in the_best_strategies:
		pickle.dump(strategy, open(file_with_the_best_strategies, 'ab'))


def random_strategy(company):
	strategy = {
		'company': company,
		'profit': None,
		'max_drawdown': None,
		'bar_size': random.choice(Ranges.bar_size)
	}
	for action in ('buy', 'sell'):
		strategy[action] = {}
		strategy[action]['TP'] = random.choice(Ranges.TP)
		strategy[action]['SL'] = random.choice(Ranges.SL)
		for indicator in all_indicators:
			strategy[action][indicator] = {'weight': random.choice(Ranges.score)}
			params = tuple(getattr(Ranges, indicator).keys())
			for j in range(len(params)):
				strategy[action][indicator][params[j]] = random.choice(getattr(Ranges, indicator)[params[j]])
		# check if strategy is normal
		if strategy[action]['stochastic']['K_min'] > strategy[action]['stochastic']['K_max']:
			return None
		if strategy[action]['stochastic']['D_min'] > strategy[action]['stochastic']['D_max']:
			return None
	return strategy


def fitness_function(strategy, historical_data):
	try:
		the_best_strategy = utils.the_best_known_strategy(strategy['company'])
	except:
		the_best_strategy = {'profit': 0}
	price_data = utils.get_price_data(strategy['company'], strategy['bar_size'])
	price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
	profitability, history, price_data = W7_backtest.main(strategy, price_data)
	profitability = round(profitability, 1)
	strategy['profit'] = profitability
	if strategy['profit'] > the_best_strategy['profit']:
		the_best_strategy = strategy.copy()
		strategy['max_drawdown'] = round(utils.max_drawdown_calculate(price_data), 1)
		save_the_best_strategy(strategy)
	return the_best_strategy


def chose_by_tournament(population):
	candidate1 = random.choice(population)
	candidate2 = random.choice(population)
	if candidate1['profit'] > candidate2['profit']:
		return candidate1
	else:
		return candidate2


def crossover(mother, father):
	baby1 = {
		'company': mother['company'],
		'profit': None,
		'max_drawdown': None,
		'bar_size': random.choice((mother['bar_size'], father['bar_size']))
	}
	baby2 = {
		'company': mother['company'],
		'profit': None,
		'max_drawdown': None,
		'bar_size': random.choice((mother['bar_size'], father['bar_size']))
	}
	for action in ('buy', 'sell'):
		baby1[action] = {}
		baby2[action] = {}
		baby1[action]['TP'] = random.choice((mother[action]['TP'], father[action]['TP']))
		baby2[action]['TP'] = random.choice((mother[action]['TP'], father[action]['TP']))
		baby1[action]['SL'] = random.choice((mother[action]['SL'], father[action]['SL']))
		baby2[action]['SL'] = random.choice((mother[action]['SL'], father[action]['SL']))
		for indicator in all_indicators:
			baby1[action][indicator] = {'weight': random.choice((mother[action][indicator]['weight'], father[action][indicator]['weight']))}
			baby2[action][indicator] = {'weight': random.choice((mother[action][indicator]['weight'], father[action][indicator]['weight']))}
			params = tuple(getattr(Ranges, indicator).keys())
			for j in range(len(params)):
				baby1[action][indicator][params[j]] = random.choice((mother[action][indicator][params[j]],
				                                                     father[action][indicator][params[j]]))
				baby2[action][indicator][params[j]] = random.choice((mother[action][indicator][params[j]],
				                                                     father[action][indicator][params[j]]))
	return baby1, baby2


def mutation(population, number_of_mutants):
	mutants = []
	# 1st half of mutations = reversed the worst strategies
	# find (number_of_mutations / 2) the worst strategies and pop them from population
	while len(mutants) < number_of_mutants / 2:
		the_worst_index = 0
		the_worst_strategy = population[the_worst_index]
		for i, strat in enumerate(population.copy()):
			if strat['profit'] < the_worst_strategy['profit']:
				the_worst_index = i
				the_worst_strategy = population[the_worst_index]
		# make reverse of the worst strategy
		the_worst_strategy = population.pop(the_worst_index)
		new_strategy = the_worst_strategy.copy()
		new_strategy['buy'] = the_worst_strategy['sell']
		new_strategy['sell'] = the_worst_strategy['buy']
		new_strategy['profit'] = None
		mutants.append(new_strategy)
	# 2nd half of mutations = random strategies
	while len(mutants) < number_of_mutants:
		random_strat = random_strategy(population[0]['company'])
		if random_strat:
			mutants.append(random_strat)
	return mutants



def genetic_algorithm(company):
	historical_data = utils.request_historical_data(company)
	monitoring = []
	the_best_strategy = None

	# Create 1st population
	population = []
	while len(population) < POP_SIZE:
		strategy = random_strategy(company)
		if strategy:
			population.append(strategy)


	for i in range(MAX_GENERATIONS):
		# Backtest the whole population and get the best result
		average_profit = 0
		for strategy in population:
			the_best_strategy = fitness_function(strategy, historical_data)
			average_profit += strategy['profit'] / POP_SIZE

		# Create new generation
		new_generation = []
		for j in range(int(POP_SIZE * (1 - MUTATION_PROBABILITY))):
			mother = chose_by_tournament(population)
			father = chose_by_tournament(population)
			baby1, baby2 = crossover(mother, father)
			new_generation.append(baby1)
			new_generation.append(baby2)

		# Mutation of the new population
		number_of_mutants = int(MUTATION_PROBABILITY * len(population))
		mutants = mutation(population, number_of_mutants)

		population = new_generation.extend(mutants)
		monitoring.append(f"Generation # {i + 1} is done! Avg.profit: {round(average_profit, 1)}%. Max profit: {the_best_strategy['profit']}%")
		print(monitoring[-1])


if __name__ == '__main__':
	company = settings.company
	# company = 'NFLX'
	print(company)
	try:
		utils.first_run()
		genetic_algorithm(company)
	except(KeyboardInterrupt):
		print('\n' * 10, 'Bye!')
