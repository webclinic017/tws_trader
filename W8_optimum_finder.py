import os
import pickle

from indicators import stochastic, volume_profile, SMA, RS
from indicators import RS as RS_ind
import settings
import utils
import W7_backtest


class Ranges:
	bar_size = ('30 mins',)
	# TP/SL
	SL = range(15)
	TP = range(15)
	# INDICATORS:
	stochastic = {
		'K_min': range(0, 100),
		'K_max': range(100, 0, -1),
		'D_min': range(0, 100),
		'D_max': range(100, 0, -1),
		'KD_difference': ('K>D', 'K<D', 'K=D', None),
		'stoch_period': range(2, 101),
		'stoch_slow_avg': range(2, 101),
		'stoch_fast_avg': range(1, 101)
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
	file_with_the_best_strategies = f'tmp_data/!BestStrategies.pkl'
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


def print_status(info):
	percentage = int((info['i'] / info['total'])*30)
	total = str(info['total'])
	if len(total) > 7:
		total = total[:7]+'...'
	print(f"""  
Best founded strategy's profitability:  {info['better_profit']}%            
Profit now:                             {info['now_profit']}%       
Calculated: {int(round(percentage*3.33, 0))}% |{"█"*percentage+' '*(30 - percentage)}| {info['i']}/{total} combinations                         
""")
	print('\033[F' * 6)


def main(company):
	existing_strategies = []
	better_strategy = {}
	strategy = {}
	better_strategy['company'] = company
	better_strategy['profit'] = 0
	better_strategy['max_drawdown'] = 0
	the_best_strategy = utils.the_best_known_strategy(company)
	if the_best_strategy == None:
		the_best_strategy = {'profit': 0.}
	i = 1
	total = (len(Ranges.bar_size) * len(Ranges.stop_loss) * len(Ranges.take_profit) *
	         len(Ranges._stochastic) * len(Ranges.weekday) * len(Ranges.japanese_candlesticks) *
	         len(Ranges._SMA) * len(Ranges._volume_profile) * len(Ranges._RS))
	for bar_size in set(Ranges.bar_size):
	# load strategies, we've already tested
		file_with_all_strategies = f'tmp_data/!Strategies_for_{company} {bar_size}.pkl'
		if not os.path.isfile(file_with_all_strategies):
			open(file_with_all_strategies, 'w+').close()
		with open(file_with_all_strategies, 'rb') as file:
			while True:
				try:
					existing_strategies.append(pickle.load(file)['indicators'])
				except EOFError:
					break

		historical_data = utils.request_historical_data(company)
		price_data = utils.get_price_data(company, bar_size)
		locator =  None
		stoch_params = None
		SMA_period = None
		RS_params = None
		for stop_loss in set(Ranges.stop_loss):
			for take_profit in set(Ranges.take_profit):
				for _stochastic in Ranges._stochastic:
					new_stoch_params = (_stochastic['stoch_period'],
										_stochastic['stoch_slow_avg'],
										_stochastic['stoch_fast_avg'])
					if  new_stoch_params != stoch_params:
						price_data = stochastic.update(price_data,
						                               _stochastic['stoch_period'],
						                               _stochastic['stoch_slow_avg'],
						                               _stochastic['stoch_fast_avg'])
					for weekday in Ranges.weekday:
						for japanese_candlesticks in Ranges.japanese_candlesticks:
							for _SMA in Ranges._SMA:
								new_SMA_period = _SMA['period']
								if new_SMA_period != SMA_period:
									price_data = SMA.update(price_data, _SMA['period'])
								for _volume_profile in Ranges._volume_profile:
									new_locator = _volume_profile['locator']
									if new_locator != locator:
										locator = new_locator
										price_data = volume_profile.update(price_data, locator, historical_data)
									for RS in Ranges._RS:
										new_RS_params = (RS['ZZ_movement'], RS['close_index'])
										if new_RS_params != RS_params:
											price_data = RS_ind.update(price_data, RS, historical_data)
										weight_sum = _stochastic['weight'] + weekday['weight'] + japanese_candlesticks['weight'] + _volume_profile['weight'] + _SMA['weight'] + RS['weight']
										if weight_sum >= 5: # quantity of indicators

											strategy['company'] = company
											strategy['profit'] = None
											strategy['max_drawdown'] = None
											strategy['buy_and_hold_profitability'] = None
											strategy['bar_size'] = bar_size
											strategy['stop_loss'] = stop_loss
											strategy['take_profit'] = take_profit
										# Indicators:
											strategy['indicators'] = {}
											strategy['indicators']['stochastic'] = _stochastic
											strategy['indicators']['weekday'] = weekday
											strategy['indicators']['japanese_candlesticks'] = japanese_candlesticks
											strategy['indicators']['volume_profile'] = _volume_profile
											strategy['indicators']['SMA'] = _SMA
											strategy['indicators']['RS'] = RS

																		# DOES NOT WORK CORRECTLY:
											if strategy['indicators']:# not in existing_strategies:
												# BACKTEST:
												profitability, history, capital_by_date = W7_backtest.main(price_data, strategy)
												profitability = round(profitability,1)
												buy_and_hold_profitability = ((price_data[-1]['Close'] - price_data[0]['Open']) / price_data[0]['Open']) * 100
												buy_and_hold_profitability = round(buy_and_hold_profitability, 1)
												strategy['profit'] = profitability
												strategy['buy_and_hold_profitability'] = buy_and_hold_profitability

												with open(file_with_all_strategies, 'ab') as file:
													pickle.dump(strategy, file, pickle.HIGHEST_PROTOCOL)

												if strategy['profit'] > better_strategy['profit']:
													better_strategy = strategy.copy()
													if better_strategy['profit'] > the_best_strategy['profit']:
														the_best_strategy = better_strategy.copy()
														the_best_strategy['max_drawdown'] = round(utils.max_drawdown_calculate(capital_by_date), 1)
														save_the_best_strategy(the_best_strategy)

											print_status({
												'i': i,
												'total': total,
												'now_profit': strategy['profit'],
												'better_profit': better_strategy['profit']
											})
											i += 1
											strategy = {}

										# Reset price data
										# 	new_price_data = []
										# 	for row in price_data:
										# 		new_price_data.append(row[:6])
										# 	price_data = new_price_data


if __name__ == '__main__':
	company = settings.company
	print(company)
	try:
		utils.first_run()
		main(company)
		print('\n\n\n\n\n')
	except(KeyboardInterrupt):
		print('\n\n\n\n\nBye!')






