import os
import pickle
import glob

import settings
import utils
import W7_backtest


class Ranges:
	bar_size = ('30 mins',)
# TP/SL
	SL = range(15)
	TP = range(15)
#INDICATORS:
	stochastic = {
		'K_min': range(0, 100),
		'K_max': range(100, 0, -1),
		'D_min': range(0, 100),
		'D_max': range(100, 0, -1),
		'KD_difference': ('K>D', 'K<D', 'K=D', None),
		'stoch_period': range(2,101),
		'stoch_slow_avg': range(2,101),
		'stoch_fast_avg': range(1,101)
	}
	weekday = {
		'weekday': (1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,135,145,234,235,245,345,1234,2345,1235,1345,1245,12345)
	}
	japanese_candlesticks = {}
	volume_profile = {
		'locator': range(1,100)
	}
	SMA = {
		'period': range(1, 300)
	}
	RS = {
		'ZZ_movement': range(1, 40),
		'close_index': range(1, 20)
	}
# 	score = range(max_a+1): # this is correct, but gives us huge massive of combinations
# 	score = (0,1,2,3,4,5,6,10,15,20,25,40,80)
	score = range(13)


def save_the_best_strategy(the_best_strategy):
	file_with_the_best_strategies = f'tmp_data/!BestStrategies-2.pkl'
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
		if strategy['company'] == the_best_strategy['company']:
			del the_best_strategies[i]
			the_best_strategies.append(the_best_strategy)
	# Or write new entry:
	if the_best_strategies == []:
		the_best_strategies.append(the_best_strategy)
	# Rewrite file:
	open(file_with_the_best_strategies, 'w').close()
	for strategy in the_best_strategies:
		pickle.dump(strategy, open(file_with_the_best_strategies, 'ab'))


def main(company):
	i = 0
	profitability = None
	for bar_size in set(Ranges.bar_size):

		historical_data = utils.request_historical_data(company)
		price_data = utils.get_price_data(company, bar_size)

		modules = glob.glob(os.path.join(os.path.dirname(__file__), 'indicators', '*.py'))
		all_indicators = [os.path.basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]

		for action in ('buy', 'sell'):
			for indicator in all_indicators:
				parameteres = getattr(Ranges, indicator)
				strategy_4_indicator = get_the_best_strategy().copy()
				strategy_4_indicator[action][indicator]['weight'] = sum(Ranges.score) * len(Ranges.score)
				strategy_4_indicator[action]['TP'] = 0
				strategy_4_indicator[action]['SL'] = 0
				price_data_4_indicator = utils.put_indicators_to_price_data(price_data,
				                                                            strategy_4_indicator,
				                                                            historical_data)
				best_profit_4_indicator = do_backtest(price_data_4_indicator, strategy_4_indicator)
				for parameter in parameteres.keys():
					strategy = get_the_best_strategy()
					best_profit_ever = strategy['profit']
					for param_value in parameteres[parameter]:
						strategy[action][indicator][parameter] = param_value
						if not_absurd(strategy):
							price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
							strategy[action][indicator]['weight'] = sum(Ranges.score) * len(Ranges.score)
							strategy[action]['TP'] = 0
							strategy[action]['SL'] = 0
							profitability = do_backtest(price_data, strategy)
							i += 1

							if profitability > best_profit_4_indicator:
								best_profit_4_indicator = profitability
								modules = glob.glob(os.path.join(os.path.dirname(__file__), 'indicators', '*.py'))
								all_indicators = [os.path.basename(f)[:-3] for f in modules if
								                  f.endswith('.py') and not f.endswith('__init__.py')]
								# Find scores
								for indicator in all_indicators:
									strategy[action][indicator]['weight'] = 0
								for indicator in all_indicators:
									for score in Ranges.score:
										strategy[action][indicator]['weight'] = score
										do_backtest(price_data, strategy)
										i += 1
								strategy = get_the_best_strategy()
								# Find the best TP/SL
								for action in ('buy', 'sell'):
									for TP in Ranges.TP:
										strategy[action]['TP'] = TP
										for SL in Ranges.SL:
											strategy[action]['SL'] = SL
											do_backtest(price_data, strategy)
											i += 1

						string_to_print = f'{action}, {indicator}, {parameter}: {param_value}'
						print_status({
							'i': i,
							'strategy': string_to_print,
							'profit': profitability,
							'best_profit': best_profit_ever
						})


def not_absurd(strategy):
	for action in ('buy', 'sell'):
		if strategy[action]['stochastic']['K_min'] > strategy[action]['stochastic']['K_max']:
			return False
		if strategy[action]['stochastic']['D_min'] > strategy[action]['stochastic']['D_max']:
			return False
	return True


def get_the_best_strategy():
	modules = glob.glob(os.path.join(os.path.dirname(__file__), 'indicators', '*.py'))
	all_indicators = [os.path.basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]
	strategy = utils.the_best_known_strategy(company)
	if not strategy:
		strategy = {
			'profit': 0,
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


def do_backtest(price_data, strategy):
	profitability, history, capital_by_date = W7_backtest.main(price_data, strategy)
	profitability = round(profitability, 1)
	strategy['profit'] = profitability
	the_best_strategy = utils.the_best_known_strategy(company)
	try:
		max_profit = the_best_strategy['profit']
	except(TypeError):
		max_profit = 0
	if strategy['profit'] > max_profit:
		modules = glob.glob(os.path.join(os.path.dirname(__file__), 'indicators', '*.py'))
		all_indicators = [os.path.basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]

		the_best_strategy = strategy.copy()
		the_best_strategy['max_drawdown'] = round(utils.max_drawdown_calculate(capital_by_date), 1)
		save_the_best_strategy(the_best_strategy)
	return profitability


def print_status(info):
	print(f"""
Backtested: {info['i']} strategies        
Now tested: {info['strategy']}          
Profit now:  {info['profit']}%              
Best profit:    {info['best_profit']}%""")
	print('\033[F' * 6)


if __name__ == '__main__':
	company = settings.company
	try:
		utils.first_run()
		while True:
			main(company)
	except(KeyboardInterrupt):
		print('\n' * 4)
		print('\nBye!')






