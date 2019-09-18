import glob
import itertools
import os
import pickle
import random
import threading
import time

import settings
import utils
import W7_backtest


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


def print_status(info):
	print(f"""            
Max profit: {info['max']}%               
Profit now: {info['profit']}%       
Attempt #:  {info['i']}          
{info['strategy']}                                
""")
	print('\033[F' * 12)


def is_normal(strategy):
	for action in ('buy', 'sell'):
		if strategy[action]['stochastic']['K_min'] > strategy[action]['stochastic']['K_max']:
			return False
		if strategy[action]['stochastic']['D_min'] > strategy[action]['stochastic']['D_max']:
			return False
	return True


# def get_empty_strategy(company, bar_size):
# 	strategy = {
# 		'company': company,
# 		'profit': None,
# 		'max_drawdown': None,
# 		'bar_size': bar_size,
# 		'buy': {'TP': 0, 'SL': 0},
# 	    'sell': {'TP': 0, 'SL': 0}
# 	}
# 	for action in ('buy', 'sell'):
# 		for indicator in all_indicators:
# 			strategy[action][indicator] = {}
# 			parameteres = getattr(Ranges, indicator)
# 			for parameter in parameteres.keys():
# 				strategy[action][indicator][parameter] = parameteres[parameter][0]
# 			strategy[action][indicator]['weight'] = 0
# 	return strategy
#
#
# def main(company):
# 	the_best_strategy = None
# 	historical_data = utils.request_historical_data(company)
#
# 	def find_the_bests_for_indicators():
# 		for bar_size in Ranges.bar_size:
# 			the_best_strategy = get_empty_strategy(company, bar_size)
# 			for indicator in set(all_indicators):
# 				params = tuple(getattr(Ranges, indicator).keys())
# 				params_values = tuple(x for x in (getattr(Ranges, indicator)[y] for y in params))
# 				for action in set(('buy', 'sell')):
# 					variants = []
# 					for values in itertools.product(*params_values):
# 						strategy = get_empty_strategy(company, bar_size)
# 						strategy[action][indicator]['weight'] = Ranges.score[-1]
# 						for j in range(len(params)):
# 							if params[j] not in ('K_min', 'K_max', 'D_min', 'D_max'):
# 								strategy[action][indicator][params[j]] = values[j]
# 							else:
# 								strategy[action][indicator][params[j]] = values[0]
# 						if not_absurd(strategy):
# 							variants.append(strategy)
# 							total = f'{len(variants):,}'
# 							print(f'  Action: {action}, indicator: {indicator}. We\'ve already got {total} strategies        ')
# 							print('\033[F' * 2)
#
# 					the_best_strategy[action][indicator] = backtesting_indicators_variants(historical_data, variants)[action][indicator].copy()
#
#
# 	def backtesting_indicators_variants(historical_data, variants):
# 		the_best_profit_for_action_indicator = 0
# 		the_best_strat_for_ind = variants[0]
# 		for i in range(1, len(list(variants).copy()) + 1):
# 			if i <= 10:
# 				try:
# 					strategy = variants.pop(random.randint(0, len(variants) - 1))
# 				except(ValueError):
# 					return the_best_strat_for_ind
# 				price_data = utils.get_price_data(company, strategy['bar_size'])
# 				price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
# 				for TP in range(5):
# 					strategy['buy']['TP'] = Ranges.TP[random.randint(0, len(Ranges.TP) - 1)]
# 					strategy['sell']['TP'] = Ranges.TP[random.randint(0, len(Ranges.TP) - 1)]
# 					for SL in range(5):
# 						strategy['buy']['SL'] = Ranges.SL[random.randint(0, len(Ranges.SL) - 1)]
# 						strategy['sell']['SL'] = Ranges.SL[random.randint(0, len(Ranges.SL) - 1)]
# 						profitability, history, capital_by_date = W7_backtest.main(price_data, strategy)
# 						profitability = round(profitability, 1)
# 						if strategy and profitability > the_best_profit_for_action_indicator:
# 							the_best_profit_for_action_indicator = profitability
# 							the_best_strat_for_ind = strategy.copy()
# 						print_status({
# 							'done': i,
# 							'remains': f'{len(variants.copy())}',
# 							'profit': profitability,
# 							'max': the_best_profit_for_action_indicator,
# 							'strategy': strategy
# 						})
# 		return the_best_strat_for_ind
#
#
#
#
#
#
# 		# # Try different TP/SL:
# 		# for action2 in set(('buy', 'sell')):
# 		# 	for TP, SL in itertools.product(Ranges.TP, Ranges.SL):
# 		# 		strategy[action2]['TP'] = TP
# 		# 		strategy[action2]['SL'] = SL
#
# 		# if not_absurd(strategy):
#
#
# 		the_best_strat_for_ind = None
# 		for i in range(1, len(list(variants).copy()) + 1):
# 			try:
# 				strategy = variants.pop(random.randint(0, len(variants) - 1))
# 			except(ValueError):
# 				return None
# 			price_data = utils.get_price_data(company, strategy['bar_size'])
# 			price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
# 			profitability, history, capital_by_date = W7_backtest.main(price_data, strategy)
# 			profitability = round(profitability, 1)
# 			if strategy and profitability > the_best_profit_for_action_indicator:
# 				the_best_profit_for_action_indicator = profitability
# 				the_best_strat_for_ind = strategy.copy()
# 			print_status({
# 				'i': f'{i}/{len(variants.copy())}',
# 				'profit': profitability,
# 				'strategy': strategy
# 			})
#
# 	find_the_bests_for_indicators()
# 	print('\n\n\n\n\n\n', 'THE BEST INDICATORS ARE:\n', the_best_strategy)
# 	find_the_best_weights()

def main(company):

	def random_strategy():
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
				params_values = tuple(x for x in (getattr(Ranges, indicator)[y] for y in params))
				for j in range(len(params)):
					strategy[action][indicator][params[j]] = random.choice(params_values[j])
		if not is_normal(strategy):
			random_strategy()
		return strategy


	def random_backtest(strategy, historical_data):
		try:
			the_best_profit_ever = utils.the_best_known_strategy(strategy['company'])['profit']
		except:
			the_best_profit_ever = 0
		price_data = utils.get_price_data(company, strategy['bar_size'])
		price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
		profitability, history, capital_by_date = W7_backtest.main(price_data, strategy)
		profitability = round(profitability, 1)
		if profitability > the_best_profit_ever:
			the_best_profit_ever = profitability
			strategy['profit'] = profitability
			strategy['max_drawdown'] = round(utils.max_drawdown_calculate(capital_by_date), 1)
			save_the_best_strategy(strategy)
		return profitability, the_best_profit_ever


	historical_data = utils.request_historical_data(company)
	i = 1
	while True:
		strategy = random_strategy()
		profitability, the_best_profit_ever = random_backtest(strategy, historical_data)
		print_status({
			'i': f'{i:,}',
			'profit': profitability,
			'strategy': strategy,
			'max': the_best_profit_ever
		})
		i += 1









if __name__ == '__main__':
	company = settings.company
	# company = 'NFLX'
	print(company)
	try:
		utils.first_run()
		main(company)
	except(KeyboardInterrupt):
		print('\n' * 10, 'Bye!')
