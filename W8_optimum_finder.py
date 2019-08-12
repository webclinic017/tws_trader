import csv
from datetime import datetime
import logging
import os
import time

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd

from indicators import stochastic, volume_profile, SMA
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
	Indicators_combination = []
	a0 = 5 # a0 = quantity of indicators
	for a1 in range(a0+1): # Stoch
		for a2 in range(1): # Weekdays OFF
			for a3 in range(1+a0): # Japanese candlesticks
				for a4 in range(1+a0): # Volume profile
					for a5 in range(1+a0): # SMA
						if sum((a1, a2, a3, a4, a5)) >= a0:
							Indicators_combination.append(f'{a0}-{a1}-{a2}-{a3}-{a4}-{a5}')
	# Indicators_combination = ['5-3-0-0-0-3']
	K_level_to_buy = (None,)
	D_level_to_buy = (None,)
	KD_difference_to_buy = (None,)
	stop_loss = (2, 5, 15)
	take_profit = (None,10)
	K_level_to_sell = (None,)
	D_level_to_sell = (None,)
	KD_difference_to_sell = (None,)
	stoch_period = range(25, 50)
	slow_avg = range(15, 65)
	fast_avg = range(5, 11)
	Weekday_buy = (None,)#1,5,2345,1234)#(1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,135,145,234,235,245,345,1234,2345)
	Weekday_sell = (None,)#1,5,2345,1234)#(None,1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,135,145,234,235,245,345,1234,2345)
	Volume_profile_locator = (10,50)
	SMA_period = range(70, 120)

# TSLA;0.0;;-29.7;30 mins;5-5-0-0-0-0;;;;5;;;;;(100, 40, 3);;;10;100
def save_the_best_strategy(the_best_strategy, capital_by_date):
	file_with_best_strategies = 'tmp_data/!BestStrategies.csv'
	best_strategies = pd.read_csv(file_with_best_strategies, index_col=0, sep=';')
	try:
		previous_max_profit = best_strategies.loc[the_best_strategy['company'], 'profit']
	except(KeyError):
		previous_max_profit = 0
	if the_best_strategy['profit'] > previous_max_profit:
		the_best_strategy['max_drawdown'] = round(utils.max_drawdown_calculate(capital_by_date), 1)
		a = list(the_best_strategy.values())[1:]
		best_strategies.loc[the_best_strategy['company']] = list(the_best_strategy.values())[1:]
		b = best_strategies
		best_strategies.to_csv(file_with_best_strategies, sep=';', na_rep='')


def print_status(info):
	a = len(ranges.K_level_to_buy)*len(ranges.D_level_to_buy)*len(ranges.KD_difference_to_buy)*len(ranges.stop_loss)
	b = len(ranges.take_profit)*len(ranges.K_level_to_sell)*len(ranges.D_level_to_sell)*len(ranges.KD_difference_to_sell)
	c = len(ranges.stoch_period)*len(ranges.slow_avg)*len(ranges.fast_avg)*len(ranges.bar_size)*len(ranges.Weekday_buy)
	d = len(ranges.Volume_profile_locator)*len(ranges.Weekday_sell)*len(ranges.Indicators_combination)*len(ranges.SMA_period)
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
SMA period:			{''.join(choosen_parameter(info[1], ranges.SMA_period))}
=========================================================================
Best founded strategy's profitability:	{info[0]}%,	profit now: {info[14]}%        
Buy and hold profitability:		{info[2]}%       
=========================================================================
Calculated: {int(round(percentage*3.33, 0))}% |{"█"*percentage+' '*(30 - percentage)}| {done_number}/{total_number} combinations                         
""")
	print('\033[F'*25)


def find_optimum_with_all_parameters(company):
	existing_strategies = []
	capital_by_date_of_the_best_strategy = None
	cycle_executed_in_seconds = 0
	the_best_strategy = {}
	strategy = {}
	the_best_strategy['company'] = company
	the_best_strategy['profit'] = -1000
	the_best_strategy['max_drawdown'] = 0
	try:
		i = 1
		for bar_size in set(ranges.bar_size):
			file_with_all_strategies = f'tmp_data/!Strategies_for_{company} {bar_size}.csv'
			if not os.path.isfile(file_with_all_strategies):
				with open(file_with_all_strategies, 'w+', encoding='utf-8') as file:
					fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
								'bar_size', 'Indicators_combination', 'K_level_to_buy', 'D_level_to_buy',
								'KD_difference_to_buy', 'stop_loss', 'take_profit', 'K_level_to_sell', 
								'D_level_to_sell', 'KD_difference_to_sell', 'Stoch_parameters', 'Weekday_buy',
								'Weekday_sell', 'Volume_profile_locator', 'SMA_period'
								]
					writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
					writer.writeheader()
			with open(file_with_all_strategies, 'r', encoding='utf-8') as file:
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
																		for SMA_period in set(ranges.SMA_period):
																			strategy['company'] = company
																			strategy['profit'] = None
																			strategy['max_drawdown'] = None
																			strategy['buy_and_hold_profitability'] = None
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
																			strategy['SMA_period'] = SMA_period
																			strting_strategy = ';'.join([str(bar_size), str(Indicators_combination), str(K_level_to_buy), str(D_level_to_buy), str(KD_difference_to_buy),
																										str(stop_loss), str(take_profit), str(K_level_to_sell), str(D_level_to_sell), str(KD_difference_to_sell),
																										str(stoch_parameters), str(Weekday_buy), str(Weekday_sell), str(Volume_profile_locator), str(SMA_period)
																										])
																			strting_strategy = strting_strategy.replace('None', '')
																			profitability = None
																			buy_and_hold_profitability = None
																			if strting_strategy not in existing_strategies:

																				price_data = stochastic.update(price_data, stoch_parameters)
																				price_data = SMA.update(price_data,SMA_period)

																				profitability, history, buy_and_hold_profitability, capital_by_date = W7_backtest.main(price_data, strategy, historical_volume_profile, step)
																				profitability = round(profitability,1)
																				buy_and_hold_profitability = round(buy_and_hold_profitability, 1)
																				strategy['profit'] = profitability
																				strategy['buy_and_hold_profitability'] = buy_and_hold_profitability

																				with open(file_with_all_strategies, 'a', encoding='utf-8') as file:
																					fieldnames = strategy.keys()
																					writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
																					writer.writerow(strategy)

																			if profitability != None and profitability > the_best_strategy['profit']:
																				the_best_strategy['company'] = company
																				the_best_strategy['profit'] = profitability
																				the_best_strategy['max_drawdown'] = None
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
																				the_best_strategy['SMA_period'] = SMA_period
																				capital_by_date_of_the_best_strategy =	capital_by_date
																				save_the_best_strategy(the_best_strategy, capital_by_date_of_the_best_strategy)									

																			print_status((the_best_strategy['profit'],
																						SMA_period,
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
																			new_price_data = []
																			for row in price_data:
																				new_price_data.append(row[:7])
																			price_data = new_price_data
																			
	except(KeyboardInterrupt):
		print('\n'*5)			
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


