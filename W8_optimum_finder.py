import csv
from datetime import datetime
import logging
import time

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from indicators import stochastic, volume_profile
import settings
import utils
import W7_backtest
import W9_strategy_parameters_analyser

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 


def make_3D_plot(x, y, z):
	fig = pyplot.figure()
	ax = Axes3D(fig)
	ax.scatter(x, y, z)
	pyplot.show()

class ranges:
	bar_size = ( '30 mins',)
	combinations = []
	for a0 in range(2,8):
		for a1 in range(11):
			for a2 in range(11):
				for a3 in range(11):
					for a4 in range(11):
						combinations.append(f'{a0}-{a1}-{a2}-{a3}-{a4}')
	Indicators_combination = combinations
	K_level_to_buy = (None,)
	D_level_to_buy = ((19,29),)
	KD_difference_to_buy = (1,)
	stop_loss = (4,)
	take_profit = (10,)
	K_level_to_sell = (None,)
	D_level_to_sell = (None,)
	KD_difference_to_sell = (0,)
	stoch_period = (19,)
	slow_avg = (12,)
	fast_avg = (5,)
	Weekday_buy = (1,12,13,14,15)
	Weekday_sell = (None,)
	Volume_profile_locator = (10,12,14,54)
	Japanese_candlesticks = (1,)


def save_the_best_strategy(the_best_strategy, capital_by_date):
	previous_max_profit = None
	with open(f'!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				previous_max_profit = float(x[1])
			else:
				previous_max_profit = 0
	if the_best_strategy['profit'] > previous_max_profit:
		max_drawdown = utils.max_drawdown_calculate(capital_by_date)
		max_drawdown = round(max_drawdown, 1)
		the_best_strategy['max_drawdown'] = max_drawdown
		with open('!BestStrategies.csv', 'a', encoding='utf-8') as file:
			fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
							'bar_size', 'Indicators_combination',
							'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
							'stop_loss', 'take_profit',
							'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
							'Stoch_parameters',
							'Weekday_buy', 'Weekday_sell', 'Volume_profile_locator', 'Japanese_candlesticks']
			writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
			writer.writerow(the_best_strategy)


def print_status(info):
	a = len(ranges.K_level_to_buy)*len(ranges.D_level_to_buy)*len(ranges.KD_difference_to_buy)*len(ranges.stop_loss)
	b = len(ranges.take_profit)*len(ranges.K_level_to_sell)*len(ranges.D_level_to_sell)*len(ranges.KD_difference_to_sell)
	c = len(ranges.stoch_period)*len(ranges.slow_avg)*len(ranges.fast_avg)*len(ranges.bar_size)*len(ranges.Weekday_buy)
	d = len(ranges.Volume_profile_locator)*len(ranges.Weekday_sell)*len(ranges.Indicators_combination)*len(ranges.Japanese_candlesticks)
	total_number = a*b*c*d
	done_number = info[12]
	percentage = int((done_number/total_number)*30)

	def choosen_parameter(choosen_parameter, tuple_of_parameters):
		choosen_start = '\033[1m'+'\033[4m'+'\033[91m'
		choosen_end = '\033[0m'
		if len(tuple_of_parameters) > 1:
			slice_before_choosen = tuple_of_parameters[:tuple_of_parameters.index(choosen_parameter)]
			slice_after_choosen = tuple_of_parameters[tuple_of_parameters.index(choosen_parameter)+1:]
			before_choosen = '' if len(slice_before_choosen) == 0 else ', '.join(str(x) for x in slice_before_choosen)+', '
			after_choosen = '' if len(slice_after_choosen) == 0 else ', '+', '.join(str(x) for x in slice_after_choosen)
			if choosen_parameter == None:
				choosen_parameter = 'None'		
			choosen = choosen_start + str(choosen_parameter) + choosen_end
			return (before_choosen, choosen, after_choosen)
		else:
			return (str(choosen_parameter), ' ', ' ')
### + Если длина range > 10 то показываем один выбранные индикатор, подсвеченный

			# Indicators_combination:		{''.join(choosen_parameter(info[18], ranges.Indicators_combination))}
### Estimation time does not work!
	choosen_start = '\033[1m'+'\033[4m'+'\033[91m'
	choosen_end = '\033[0m'
	print(f"""  
Bar size:			{''.join(choosen_parameter(info[13], ranges.bar_size))}           
Indicators_combination:		{info[18]}            
K level to buy:			{''.join(choosen_parameter(info[3], ranges.K_level_to_buy))}                   
D level to buy:			{''.join(choosen_parameter(info[4], ranges.D_level_to_buy))}                
KD difference to buy:		{''.join(choosen_parameter(info[5], ranges.KD_difference_to_buy))}                
stop loss:			{''.join(choosen_parameter(info[6], ranges.stop_loss))}                 
take profit:			{''.join(choosen_parameter(info[7], ranges.take_profit))}                
K level to sell:		{''.join(choosen_parameter(info[8], ranges.K_level_to_sell))}                 
D level to sell:		{''.join(choosen_parameter(info[9], ranges.D_level_to_sell))}               
KD difference to sell:		{''.join(choosen_parameter(info[10], ranges.KD_difference_to_sell))}                
Stoch period:			{''.join(choosen_parameter(info[11][0], ranges.stoch_period))}                  
Stoch slow average:		{''.join(choosen_parameter(info[11][1], ranges.slow_avg))}                 
Stoch fast average:		{''.join(choosen_parameter(info[11][2], ranges.fast_avg))}                 
Weekdays to buy:		{''.join(choosen_parameter(info[15], ranges.Weekday_buy))}                 
Weekdays to sell:		{''.join(choosen_parameter(info[16], ranges.Weekday_sell))}              
Volume profile locator:		{''.join(choosen_parameter(info[17], ranges.Volume_profile_locator))}           
Japanese candlesticks:		{''.join(choosen_parameter(info[1], ranges.Japanese_candlesticks))}
=========================================================================
Best founded strategy's profitability:	{info[0]}%,	profit now: {info[14]}%        
Buy and hold profitability:		{info[2]}%       
=========================================================================
Calculated: {int(round(percentage*3.33, 0))}% |{"█"*percentage+' '*(30 - percentage)}| {done_number}/{total_number} combinations                   
Time left:	{info[19]*(total_number-done_number)} seconds         
""")
	print('\033[F'*26)


def find_optimum_with_all_parameters(company):
	existing_strategies = []
	capital_by_date_of_the_best_strategy = None
	cycle_executed_in_seconds = 0
	the_best_strategy = {}
	strategy = {}
	the_best_strategy['profit'] = 0
	the_best_strategy['max_drawdown'] = 0
	try:
		i = 1
		for bar_size in set(ranges.bar_size):
			with open(f'!Strategies_for_{company} {bar_size}.csv', 'r', encoding='utf-8') as file:
				reader = csv.reader(file, delimiter=';')
				for row in reader:
					existing_strategies.append(';'.join(row[4:]))
			price_data = utils.get_price_data(company, bar_size)
			first_date = price_data[0][0]
			end_date = [int(first_date[:4]), int(first_date[4:6]), int(first_date[6:8])]
			historical_volume_profile, step = volume_profile.historical_volumes(company, end_date)
			for Indicators_combination in set(ranges.Indicators_combination):
				for stoch_period in set(ranges.stoch_period):
					for slow_avg in set(ranges.slow_avg):
						for fast_avg in set(ranges.fast_avg):
							stoch_parameters = (stoch_period, slow_avg, fast_avg)
							price_data = stochastic.update(price_data, stoch_parameters)
							for stop_loss in set(ranges.stop_loss):
								for take_profit in set(ranges.take_profit):
									for K_level_to_sell in set(ranges.K_level_to_sell):
										for D_level_to_sell in set(ranges.D_level_to_sell):
											for KD_difference_to_sell in set(ranges.KD_difference_to_sell):
												for K_level_to_buy in set(ranges.K_level_to_buy):
													for D_level_to_buy in set(ranges.D_level_to_buy):
														for KD_difference_to_buy in set(ranges.KD_difference_to_buy):
															for Weekday_buy in set(ranges.Weekday_buy):
																for Weekday_sell in set(ranges.Weekday_sell):
																	for Volume_profile_locator in set(ranges.Volume_profile_locator):
																		for Japanese_candlesticks in set(ranges.Japanese_candlesticks):
																			strategy['company'] = company
																			strategy['bar_size'] = bar_size
																			strategy['Indicators_combination'] = Indicators_combination
																			strategy['K_level_to_buy'] = K_level_to_buy
																			strategy['D_level_to_buy'] = D_level_to_buy
																			strategy['KD_difference_to_buy'] = KD_difference_to_buy
																			strategy['stop_loss'] = stop_loss
																			strategy['take_profit'] = take_profit
																			strategy['K_level_to_sell'] = K_level_to_sell
																			strategy['D_level_to_sell'] = D_level_to_sell
																			strategy['KD_difference_to_sell'] = KD_difference_to_sell
																			strategy['Stoch_parameters'] = stoch_parameters
																			strategy['Weekday_buy'] = Weekday_buy
																			strategy['Weekday_sell'] = Weekday_sell
																			strategy['Volume_profile_locator'] = Volume_profile_locator
																			strategy['Japanese_candlesticks'] = Japanese_candlesticks
																			strting_strategy = ';'.join([str(bar_size), str(Indicators_combination), str(K_level_to_buy), str(D_level_to_buy), str(KD_difference_to_buy),
																										str(stop_loss), str(take_profit), str(K_level_to_sell), str(D_level_to_sell), str(KD_difference_to_sell),
																										str(stoch_parameters), str(Weekday_buy), str(Weekday_sell), str(Volume_profile_locator), str(Japanese_candlesticks)
																										])
																			strting_strategy = strting_strategy.replace('None', '')
																			profitability = None
																			buy_and_hold_profitability = None
																			if strting_strategy not in existing_strategies:
																				profitability, history, buy_and_hold_profitability, capital_by_date = W7_backtest.main(price_data, strategy, historical_volume_profile, step)
																				profitability = round(profitability,1)
																				buy_and_hold_profitability = round(buy_and_hold_profitability, 1)
																				strategy['profit'] = profitability
																				strategy['buy_and_hold_profitability'] = buy_and_hold_profitability

																				# if strategy['profit'] > 100.:
																				with open(f'!Strategies_for_{company} {bar_size}.csv', 'a', encoding='utf-8') as file:
																					fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
																									'bar_size', 'Indicators_combination',
																									'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
																									'stop_loss', 'take_profit',
																									'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
																									'Stoch_parameters',
																									'Weekday_buy', 'Weekday_sell', 'Volume_profile_locator',
																									'Japanese_candlesticks']
																					writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
																					writer.writerow(strategy)

																			if profitability != None and profitability > the_best_strategy['profit']:
																				the_best_strategy['company'] = company
																				the_best_strategy['profit'] = profitability
																				the_best_strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
																				the_best_strategy['bar_size'] = bar_size
																				the_best_strategy['Indicators_combination'] = Indicators_combination
																				the_best_strategy['K_level_to_buy'] = K_level_to_buy
																				the_best_strategy['D_level_to_buy'] = D_level_to_buy
																				the_best_strategy['KD_difference_to_buy'] = KD_difference_to_buy
																				the_best_strategy['stop_loss'] = stop_loss
																				the_best_strategy['take_profit'] = take_profit
																				the_best_strategy['K_level_to_sell'] = K_level_to_sell
																				the_best_strategy['D_level_to_sell'] = D_level_to_sell
																				the_best_strategy['KD_difference_to_sell'] = KD_difference_to_sell
																				the_best_strategy['Stoch_parameters'] = stoch_parameters
																				the_best_strategy['Weekday_buy'] = Weekday_buy
																				the_best_strategy['Weekday_sell'] = Weekday_sell
																				the_best_strategy['Volume_profile_locator'] = Volume_profile_locator
																				the_best_strategy['Japanese_candlesticks'] = Japanese_candlesticks	
																				capital_by_date_of_the_best_strategy = 	capital_by_date										

																			print_status((the_best_strategy['profit'],
																						Japanese_candlesticks,
																						buy_and_hold_profitability,
																						K_level_to_buy,
																						D_level_to_buy,
																						KD_difference_to_buy,
																						stop_loss,
																						take_profit,
																						K_level_to_sell,
																						D_level_to_sell,
																						KD_difference_to_sell,
																						stoch_parameters,
																						i,
																						bar_size,
																						profitability,
																						Weekday_buy,
																						Weekday_sell,
																						Volume_profile_locator,
																						Indicators_combination,
																						cycle_executed_in_seconds
																						))
																			i += 1
																			strategy = {}
																			
	except(KeyboardInterrupt):
		print('\n'*5)
	save_the_best_strategy(the_best_strategy, capital_by_date_of_the_best_strategy)				
	return the_best_strategy, capital_by_date_of_the_best_strategy


def main(company):
	the_best_strategy, capital_by_date = find_optimum_with_all_parameters(company)
	save_the_best_strategy(the_best_strategy, capital_by_date)
	print('\n'*23)
	# view_plots = input('Do you want to see plots? (y/n):')
	# if view_plots == 'y':
	# 	W9_strategy_parameters_analyser.main(company, '30 mins')


if __name__ == '__main__':
	company = settings.company
	print(company)
	main(company)


