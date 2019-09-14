import csv
import os
import pickle

from indicators import stochastic, volume_profile, SMA, RS
from indicators import RS as RS_ind
import settings
import utils
import W7_backtest

# Мое понимание происходящего:
# Существует 2 типа индикаторов - сигнальные (основные) и фильтрующие
# Сигнальные:
#   - stochastic
#   - japanese_candlesticks
#   - SMA (у меня реализован как сигнальный - по пересечению бара open-close)
#
# Фильтрующие:
#   - weekday
#   - volume_profile
#
#
# Искать оптимум надо так:
# 1) Для каждого сигнального индикатора найти его лучший вариант
# 2) При SL и TP = None найти лучшие варианты комбинаций сигнальных индикаторов
# 3) Застолбить сигнальные индикаторы и их комбинации и при них найти лучшие варианты scores и фильтрующих индикаторов
# 4) Подобрать лучшие SL и TP
#


class Ranges:
	bar_size = ( '30 mins',)

# Major settings
	stop_loss = range(1,25)
	take_profit = range(1,25)

#INDICATORS:
# stochastic:
	_stochastic = []
	for K_level_to_buy in (None,):
		for D_level_to_buy in ((19, 29),):
			for KD_difference_to_buy in (1,):
				for K_level_to_sell in (None,):
					for D_level_to_sell in (None,):
						for KD_difference_to_sell in (0,):
							for stoch_period in (17,):
								for stoch_slow_avg in (13,):
									for stoch_fast_avg in (4,):
										indicator = {
													'K_level_to_buy': K_level_to_buy,
													'D_level_to_buy': D_level_to_buy,
													'KD_difference_to_buy': KD_difference_to_buy,
													'K_level_to_sell': K_level_to_sell,
													'D_level_to_sell': D_level_to_sell,
													'KD_difference_to_sell': KD_difference_to_sell,
													'stoch_period': stoch_period,
													'stoch_slow_avg': stoch_slow_avg,
													'stoch_fast_avg': stoch_fast_avg
													}
										_stochastic.append(indicator)

# weekday:
	weekday = []
	for Weekday_buy in (1,):#(None,1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,135,145,234,235,245,345,1234,2345,1235,1345,1245,12345):
		for Weekday_sell in (345,):#(None,1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,135,145,234,235,245,345,1234,2345,1235,1345,1245,12345):
			indicator = {
						'Weekday_buy': Weekday_buy,
						'Weekday_sell': Weekday_sell
						}
			weekday.append(indicator)

# japanese_candlesticks:
	japanese_candlesticks = []
	indicator = {
				}
	japanese_candlesticks.append(indicator)

# volume_profile:
	_volume_profile = []
	for locator in (14,):
		indicator = {
					'locator': locator
					}
		_volume_profile.append(indicator)

# SMA:
	_SMA = []
	for period in (25,):
		indicator = {
			'period': period
			}
		_SMA.append(indicator)

# RS:
	_RS = []
	for ZZ_movement in (1,):
		for close_index in (1,):
			indicator = {
				'ZZ_movement': ZZ_movement,
				'close_index': close_index
						}
			_RS.append(indicator)

# Scores:
	x1 = []
	x2 = []
	x3 = []
	x4 = []
	x5 = []
	x6 = []
# 	for score in range(max_a+1): # this is correct, but gives us huge massive of combinations
	scores = (0,1,2,3,4,5,6,10)
	for score in scores:
		for x in _stochastic:
			if score == 10:	#in scores:#
				x['weight'] = score
				x1.append(x.copy())
		for x in weekday:
			if score == 3: #in scores:#
				x['weight'] = score
				x2.append(x.copy())
		for x in japanese_candlesticks:
			if score == 5:  	#in scores:#
				x['weight'] = score
				x3.append(x.copy())
		for x in _volume_profile:
			if score == 4:	#in scores:#
				x['weight'] = score
				x4.append(x.copy())
		for x in _SMA:
			if score == 2:	#in scores:#
				x['weight'] = score
				x5.append(x.copy())
		for x in _RS:
			if score == 0:  #in scores:#
				x['weight'] = score
				x6.append(x.copy())
	_stochastic = x1
	weekday = x2
	japanese_candlesticks = x3
	_volume_profile = x4
	_SMA = x5
	_RS = x6

# {'company': 'TSLA', 'profit': 235.5, 'max_drawdown': None, 'buy_and_hold_profitability': -35.8, 'bar_size': '30 mins', 'stop_loss': None, 'take_profit': None, 'indicators': {'stochastic': {'K_level_to_buy': None, 'D_level_to_buy': (19, 29), 'KD_difference_to_buy': 1, 'K_level_to_sell': None, 'D_level_to_sell': None, 'KD_difference_to_sell': 0, 'stoch_period': 19, 'stoch_slow_avg': 12, 'stoch_fast_avg': 5, 'weight': 10}, 'weekday': {'Weekday_buy': 1, 'Weekday_sell': 345, 'weight': 3}, 'japanese_candlesticks': {'weight': 5}, 'volume_profile': {'locator': 14, 'weight': 4}, 'SMA': {'period': 32, 'weight': 4}, 'RS': {'ZZ_movement': 22, 'close_index': 9, 'weight': 0}}}

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






