import glob
import itertools
import os
import pickle

import settings
import utils
import W7_backtest


modules = glob.glob(os.path.join(os.path.dirname(__file__), 'indicators', '*.py'))
all_indicators = [os.path.basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]


class Ranges:
	bar_size = ('30 mins',)
	# TP/SL
	SL = range(16)
	TP = range(16)
	# INDICATORS:
	stochastic = {
		'stoch_period': range(2, 101),
		'stoch_slow_avg': range(2, 101),
		'stoch_fast_avg': range(1, 101),
		'K_min': range(0, 100),
		'K_max': range(100, 0, -1),
		'D_min': range(0, 100),
		'D_max': range(100, 0, -1),
		'KD_difference': ('K>D', 'K<D', 'K=D', None)
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
Best founded strategy's profitability:  {info['best_profit']}%              
Profit now:                             {info['profit']}%       
Calculated:                             {info['i']} combinations  
{info['strategy']}                                
""")
	print('\033[F' * 11)


def not_absurd(strategy):
	for action in ('buy', 'sell'):
		if strategy[action]['stochastic']['K_min'] > strategy[action]['stochastic']['K_max']:
			return False
		if strategy[action]['stochastic']['D_min'] > strategy[action]['stochastic']['D_max']:
			return False
		# if scores ok:
		scores_buy = 0
		scores_sell = 0
		for indicator in all_indicators:
			scores_buy += strategy['buy'][indicator]['weight']
			scores_sell += strategy['sell'][indicator]['weight']
		if scores_buy < len(all_indicators) and scores_sell < len(all_indicators):
			return False
	return True


def get_the_strategy(company, bar_size):
	strategy = utils.the_best_known_strategy(company)
	if not strategy:
		strategy = {
			'company': company,
			'profit': -100000000,
			'bar_size': bar_size,
			'buy': {'TP': 0, 'SL': 0},
		    'sell': {'TP': 0, 'SL': 0}
		}
		for action in ('buy', 'sell'):
			for indicator in all_indicators:
				strategy[action][indicator] = {}
				parameteres = getattr(Ranges, indicator)
				for parameter in parameteres.keys():
					strategy[action][indicator][parameter] = parameteres[parameter][0]
				strategy[action][indicator]['weight'] = 0
	return strategy


def main(company):
	i = 1
	for bar_size in Ranges.bar_size:
		historical_data = utils.request_historical_data(company)
		price_data = utils.get_price_data(company, bar_size)
		for indicator in set(all_indicators):
			params = tuple(getattr(Ranges, indicator).keys())
			params_values = tuple(x for x in (getattr(Ranges, indicator)[y] for y in params))
			for action in set(('buy', 'sell')):
				strategy = get_the_strategy(company, bar_size)
				for values in itertools.product(*params_values):
					for j in range(len(params)):
						strategy[action][indicator][params[j]] = values[j]
					if i == 1:
						best_profit_ever = strategy['profit']
					if indicator in ('stochastic', 'RS', 'SMA', 'volume_profile') or i == 1:
						price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
					strategy[action][indicator]['weight'] = Ranges.score[-1]
					strategy[action]['TP'] = 0
					strategy[action]['SL'] = 0
					if not_absurd(strategy):
						profitability, history, capital_by_date = W7_backtest.main(price_data, strategy)
						profitability = round(profitability, 1)
						strategy['profit'] = profitability
						if profitability > best_profit_ever:
							if profitability > .0:
								strategy['max_drawdown'] = round(utils.max_drawdown_calculate(capital_by_date), 1)
								save_the_best_strategy(strategy)

								# Try different weights:
								for action1 in set(('buy', 'sell')):
									for score in Ranges.score:
										for indicator1 in set(all_indicators):
											strategy = get_the_strategy(company, bar_size)
											strategy[action1][indicator1]['weight'] = score
											profitability1, history, capital_by_date = W7_backtest.main(price_data, strategy)
											profitability1 = round(profitability1, 1)
											strategy['profit'] = profitability1
											if profitability1 > best_profit_ever:
												best_profit_ever = profitability1
												strategy['max_drawdown'] = round(
													utils.max_drawdown_calculate(capital_by_date), 1)
												save_the_best_strategy(strategy)
											i += 1
											print_status({
												'i': i,
												'profit': profitability1,
												'best_profit': best_profit_ever,
												'strategy': strategy
											})
								# Try different TP/SL:
								for action2 in set(('buy', 'sell')):
									strategy = get_the_strategy(company, bar_size)
									for TP, SL in itertools.product(Ranges.TP, Ranges.SL):
										strategy[action2]['TP'] = TP
										strategy[action2]['SL'] = SL
										profitability2, history, capital_by_date = W7_backtest.main(price_data, strategy)
										profitability2 = round(profitability2, 1)
										strategy['profit'] = profitability2
										if profitability2 > best_profit_ever:
											best_profit_ever = profitability2
											strategy['max_drawdown'] = round(
												utils.max_drawdown_calculate(capital_by_date), 1)
											save_the_best_strategy(strategy)
										i += 1
										print_status({
											'i': i,
											'profit': profitability2,
											'best_profit': best_profit_ever,
											'strategy': strategy
										})
								strategy = get_the_strategy(company, bar_size)

						print_status({
							'i': i,
							'profit': profitability,
							'best_profit': best_profit_ever,
							'strategy': strategy
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
