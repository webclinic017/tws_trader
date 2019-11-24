import glob
import os
import pickle
import random

import settings
import utils
import W7_backtest

POP_SIZE = 100
MAX_GENERATIONS = 1000
MUTATION_PROBABILITY = .15  # how many strategies in population will mutate

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
			1, 2, 3, 4, 5, 12, 13, 14, 15, 23, 24, 25, 34, 35, 45, 123, 124, 125, 134, 135, 145, 234, 235, 245, 345,
			1234,
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
		'ZZ_movement': (1,),  # range(1, 40),
		'close_index': (1,)  # range(1, 20)
	}
	# 	score = range(max_a+1): # this is correct, but gives us huge massive of combinations
	# 	score = (0,1,2,3,4,5,6,10,15,20,25,40,80)
	weight = range(len(all_indicators) * 2 + 1)


def save_the_best_strategy(strategy_to_save):
	file_with_the_best_strategies = f'tmp_data/!BestStrategies.pkl'
	# Get all of the best strategies in list
	the_best_strategies = {}
	with open(file_with_the_best_strategies, 'rb') as file:
		while True:
			try:
				strategy = pickle.load(file)
				the_best_strategies[strategy['company']] = strategy
			except EOFError:
				break
	# If it is new empty file:
	if not the_best_strategies:
		the_best_strategies[strategy_to_save['company']] = strategy_to_save
	# Rewrite new the_best_strategy:
	the_best_strategies[strategy_to_save['company']] = strategy_to_save
	# Rewrite file:
	open(file_with_the_best_strategies, 'w').close()
	for strategy in list(the_best_strategies.values()):
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
			strategy[action][indicator] = {'weight': random.choice(Ranges.weight)}
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
	the_best_strategy = utils.the_best_known_strategy(strategy['company'])
	if not the_best_strategy:
		the_best_strategy = {'profit': 0}
	price_data = utils.get_price_data(strategy['company'], strategy['bar_size'])
	price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
	profitability, history, price_data = W7_backtest.main(strategy, price_data)
	profitability = round(profitability, 1)
	strategy['profit'] = profitability

	# 1 alternative backtest:
	strategy2 = strategy.copy()
	for action in ('buy', 'sell'):
		for indicator in all_indicators:
			strategy2[action][indicator]['weight'] = random.choice(Ranges.weight)
	profitability2, history2, price_data2 = W7_backtest.main(strategy2, price_data)
	profitability2 = round(profitability2, 1)
	strategy2['profit'] = profitability2
	if profitability2 > profitability:
		strategy['profit'] = profitability2
		strategy['buy'] = strategy2['buy'].copy()
		strategy['sell'] = strategy2['sell'].copy()

	print(f"    {strategy['profit']} %                 ")
	print('\033[F' * 2)
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
			baby1[action][indicator] = {
				'weight': random.choice((mother[action][indicator]['weight'], father[action][indicator]['weight']))}
			baby2[action][indicator] = {
				'weight': random.choice((mother[action][indicator]['weight'], father[action][indicator]['weight']))}
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
	population = sorted(population, key=lambda i: i['profit'])
	negative_strats = []
	for i in range(int(number_of_mutants / 2)):
		if population[i]['profit'] < 0.:
			negative_strats.append(population.pop(i))
	for strat in negative_strats:
		new_strategy = strat.copy()
		new_strategy['buy'] = strat['sell']
		new_strategy['sell'] = strat['buy']
		new_strategy['profit'] = None
		mutants.append(new_strategy)
	# Rest of mutations = strategies with random genes
	while len(mutants) < number_of_mutants:
		strategy = random.choice(population)
		for action in ('buy', 'sell'):
			strategy[action] = {}
			strategy[action]['TP'] = random.choice((random.choice(Ranges.TP), strategy[action]['TP']))
			strategy[action]['SL'] = random.choice((random.choice(Ranges.SL), strategy[action]['SL']))
			for indicator in all_indicators:
				strategy[action][indicator] = {'weight': random.choice((random.choice(Ranges.weight), strategy[action][indicator]['weight']))}
				params = tuple(getattr(Ranges, indicator).keys())
				for j in range(len(params)):
					strategy[action][indicator][params[j]] = random.choice((random.choice(
						getattr(Ranges, indicator)[params[j]]),
						strategy[action][indicator][params[j]]
					))
		if strategy[action]['stochastic']['K_min'] > strategy[action]['stochastic']['K_max']:
			if strategy[action]['stochastic']['D_min'] > strategy[action]['stochastic']['D_max']:
				mutants.append(strategy)
	return mutants


def genetic_algorithm(company):
	historical_data = utils.request_historical_data(company)
	monitoring = []
	the_best_strategy = None

	# Create 1st population
	population = []
	the_best_strategy = utils.the_best_known_strategy(company)
	if the_best_strategy:
		while len(population) < POP_SIZE:
			strategy = {
				'company': company,
				'profit': None,
				'max_drawdown': None,
				'bar_size': random.choice((random.choice(Ranges.bar_size), the_best_strategy['bar_size']))
			}
			for action in ('buy', 'sell'):
				strategy[action] = {}
				strategy[action]['TP'] = random.choice((random.choice(Ranges.TP), the_best_strategy[action]['TP']))
				strategy[action]['SL'] = random.choice((random.choice(Ranges.SL), the_best_strategy[action]['SL']))
				for indicator in all_indicators:
					strategy[action][indicator] = {'weight': random.choice((random.choice(Ranges.weight), the_best_strategy[action][indicator]['weight']))}
					params = tuple(getattr(Ranges, indicator).keys())
					for j in range(len(params)):
						strategy[action][indicator][params[j]] = random.choice((random.choice(
							getattr(Ranges, indicator)[params[j]]),
							the_best_strategy[action][indicator][params[j]]
						))
			if strategy[action]['stochastic']['K_min'] > strategy[action]['stochastic']['K_max']:
				if strategy[action]['stochastic']['D_min'] > strategy[action]['stochastic']['D_max']:
					population.append(strategy)
	if not the_best_strategy:
		while len(population) < POP_SIZE:
			strategy = random_strategy(company)
			if strategy:
				population.append(strategy)

	for i in range(MAX_GENERATIONS):
		# Backtest the whole population and get the best result
		average_profit = 0.
		max_profit_in_populaton = -10000000.
		x = 1
		for strategy in population:
			print(f'  {x}/{len(population)}', end=' ')
			x += 1
			the_best_strategy = fitness_function(strategy, historical_data)
			average_profit += strategy['profit'] / POP_SIZE
			if strategy['profit'] > max_profit_in_populaton:
				max_profit_in_populaton = strategy['profit']

		# Mutation of the new population
		number_of_mutants = int(POP_SIZE * MUTATION_PROBABILITY)
		mutants = mutation(population, number_of_mutants)

		# Create new generation
		new_generation = []
		for j in range(int((POP_SIZE * (1 - MUTATION_PROBABILITY)) / 2)):
			mother = chose_by_tournament(population)
			father = chose_by_tournament(population)
			baby1, baby2 = crossover(mother, father)
			new_generation.append(baby1)
			new_generation.append(baby2)

		new_generation.extend(mutants)
		population = new_generation
		monitoring.append(f"Generation #{i + 1} is done! Avg.profit:    {round(average_profit, 1)}%. Max profit in population:	{max_profit_in_populaton}%. Max profit ever:  {the_best_strategy['profit']}   %")
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
