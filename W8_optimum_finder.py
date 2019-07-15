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

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING) 


def make_3D_plot(x, y, z):
	fig = pyplot.figure()
	ax = Axes3D(fig)
	ax.scatter(x, y, z)
	pyplot.show()




#TSLA;203.89400549999928;12.0595401895667;-28.706049999999994;;(19, 29);1;4;8.5;;;0;(19, 12, 5)
class ranges:
	# bar_size = ('10 mins',) 	# '10 mins', '20 mins', '1 hour', '1 day') 	# 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
	# K_level_to_buy = (None,(10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))	#(1,20),(20,60), (40,80),(80,100))
	# D_level_to_buy = (None,(10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))	#(19,28),(20,28),(18,29),(20,29),(18,30))	#None, )
	# KD_difference_to_buy = (0,-1)	# -1, 0, None)
	# stop_loss = (6,8,9,11)	#3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5)	#my_range(4, 7)
	# take_profit = (6,8,9,11)	#(None, 8.5, 8.6, 8.7, 8.8, 8.9, 9, 10.1, 10.2, 10.3, 10.4, 10.5)	#my_range(6.5, 8.5)
	# K_level_to_sell = (None,(10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))	#(1,20),(20,60), (40,80),(80,100))
	# D_level_to_sell = (None,(10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))	#(80,100),(60,80))	# (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	# KD_difference_to_sell = (1,)	#1, -1, 0, None)	# -1, 1, None)
	# stoch_period = (1,2,16,17,18,19,21,22,23,24)#range(7, 50, 7)	#range(3,101, 10)
	# slow_avg = (1,2,3,4,6,7,8,9,11,12,13,14)#range(7,50,7)	#range(3,101, 10)
	# fast_avg = (7,8,9,30,25,40,45) # range(2,32,5)#range(3,13,3)	#range(3,51, 5)
	
	# 1st iteration:
	# bar_size = ('10 mins', '20 mins', '1 hour', '3 hours', '1 day', '5 mins')
	# K_level_to_buy = (None,)
	# D_level_to_buy = (None,)
	# KD_difference_to_buy = (None, 0, -1, 1)
	# stop_loss = (None, 2, 5, 7, 10, 15)
	# take_profit = (None, 2, 5, 7, 10, 15)
	# K_level_to_sell = (None,)
	# D_level_to_sell = (None,)
	# KD_difference_to_sell = (None, 0, -1, 1)
	# stoch_period = (5,10,15,20,25,50,75,100)
	# slow_avg = (5,10,15,20,25,50,75,100)
	# fast_avg = (5,10,15,20,25,50,75,100)

	# 2nd iteration:
	# bar_size = ('10 mins',) 	# '10 mins', '20 mins', '1 hour', '1 day') 	# 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
	# K_level_to_buy = (None,) 	#(1,20),(20,60), (40,80),(80,100))
	# D_level_to_buy = (None,)	#(19,28),(20,28),(18,29),(20,29),(18,30))	#None, )
	# KD_difference_to_buy = (0,-1)	# -1, 0, None)
	# stop_loss = (6,8,9,11)	#3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5)	#my_range(4, 7)
	# take_profit = (6,8,9,11)	#(None, 8.5, 8.6, 8.7, 8.8, 8.9, 9, 10.1, 10.2, 10.3, 10.4, 10.5)	#my_range(6.5, 8.5)
	# K_level_to_sell = (None,)	#(1,20),(20,60), (40,80),(80,100))
	# D_level_to_sell = (None,)	#(80,100),(60,80))	# (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	# KD_difference_to_sell = (1,)	#1, -1, 0, None)	# -1, 1, None)
	# stoch_period = (1,2,16,17,18,19,21,22,23,24)#range(7, 50, 7)	#range(3,101, 10)
	# slow_avg = (1,2,3,4,6,7,8,9,11,12,13,14)#range(7,50,7)	#range(3,101, 10)
	# fast_avg = (7,8,9,30,25,40,45) # range(2,32,5)#range(3,13,3)	#range(3,51, 5)

# TSLA;212.72672575999977;;-28.84544;30 mins;;(19, 29);;4;8.1;;;0;(19, 12, 5);124;

	# 3rd iteration:
	bar_size = ('30 mins',) #	,'5 mins', 'hour', '1 day') 	# '10 mins', '20 mins', '1 hour', '1 day') 	# 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
	K_level_to_buy = (None,) 	#(1,20),(20,60), (40,80),(80,100))
	D_level_to_buy = ((19,29),)	#(19,28),(20,28),(18,29),(20,29),(18,30))	#None, )
	KD_difference_to_buy = (1, -1, 0, None)
	stop_loss = (4,)	#3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5)	#my_range(4, 7)
	take_profit = (8.5,)	#(None, 8.5, 8.6, 8.7, 8.8, 8.9, 9, 10.1, 10.2, 10.3, 10.4, 10.5)	#my_range(6.5, 8.5)
	K_level_to_sell = (None,)	#(1,20),(20,60), (40,80),(80,100))
	D_level_to_sell = (None,)	#(80,100),(60,80))	# (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	KD_difference_to_sell = (0,1, -1, None)	# -1, 1, None)
	stoch_period = (5, 19,10,30)#range(7, 50, 7)	#range(3,101, 10)
	slow_avg = (5, 12,20,30)#range(7,50,7)	#range(3,101, 10)
	fast_avg = (5,10,20) # range(2,32,5)#range(3,13,3)	#range(3,51, 5)
	Weekday_buy = (None,)	#(1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,145,234,235,245,345,1234,1235,1245,1345,2345,12345)
	Weekday_sell = (None,)	#1234,2345, 234)	#(1,2,3,4,5,12,13,14,15,23,24,25,34,35,45,123,124,125,134,145,234,235,245,345,1234,1235,1245,1345,2345,12345)
	Volume_profile_locator = (None, 2,6,10,12,16,20,24,30,40,50,80,100)


def print_status(info):
	a = len(ranges.K_level_to_buy)*len(ranges.D_level_to_buy)*len(ranges.KD_difference_to_buy)*len(ranges.stop_loss)
	b = len(ranges.take_profit)*len(ranges.K_level_to_sell)*len(ranges.D_level_to_sell)*len(ranges.KD_difference_to_sell)
	c = len(ranges.stoch_period)*len(ranges.slow_avg)*len(ranges.fast_avg)*len(ranges.bar_size)*len(ranges.Weekday_buy)
	d = len(ranges.Volume_profile_locator)*len(ranges.Weekday_sell)
	total_number = a*b*c*d
	done_number = info[12]
	percentage = int((done_number/total_number)*30)
	# if done_number < total_number:
	# 	print(f'  Calculating: {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number}', ' '*5, end='\r')
	# else:
	# 	time_now = time.strftime("%m/%d/%Y %I:%M %p", time.gmtime())
	# 	print(f'  Calculating: {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number}')
	
	def choosen_parameter(choosen_parameter, tuple_of_parameters):
		choosen_start = '\033[1m'+'\033[4m'+'\033[91m'
		choosen_end = '\033[0m'
		if len(tuple_of_parameters) > 1:
			# print(choosen_parameter, tuple_of_parameters)
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
### + Estimation time
	print(f"""  
Bar size:			{''.join(choosen_parameter(info[13], ranges.bar_size))}           
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
=========================================================================
Best founded strategy's profitability:	{round(info[0],1)}%,	profit now: {round(info[14],1)}%        
Buy and hold profitability:		{round(info[2],1)}%       
=========================================================================
Calculated: {int(round(percentage*3.33, 0))}% |{"█"*percentage+' '*(30 - percentage)}| {done_number}/{total_number} combinations                   
""")
	print('\033[F'*23)

def find_optimum_with_all_parameters(company):
	existing_strategies = []
	with open(f'!Strategies_for_{company}.csv', 'r', encoding='utf-8') as file:
		reader = csv.reader(file, delimiter=';')
		for row in reader:
			existing_strategies.append(';'.join(row[4:]))
	the_best_strategy = {}
	strategy = {}
	the_best_strategy['profit'] = 0
	the_best_strategy['max_drawdown'] = 0
	try:
		i = 1
		for bar_size in ranges.bar_size:
			price_data = utils.get_price_data(company, bar_size)
			first_date = price_data[1][0]
			end_date = [int(first_date[:4]), int(first_date[4:6]), int(first_date[6:8])]
			historical_volume_profile, step = volume_profile.historical_volumes(end_date)
			for stoch_period in ranges.stoch_period:
				for slow_avg in ranges.slow_avg:
					for fast_avg in ranges.fast_avg:
						stoch_parameters = (stoch_period, slow_avg, fast_avg)
						price_data = stochastic.main(price_data, stoch_parameters)
						for stop_loss in ranges.stop_loss:
							for take_profit in ranges.take_profit:
								for K_level_to_sell in ranges.K_level_to_sell:
									for D_level_to_sell in ranges.D_level_to_sell:
										for KD_difference_to_sell in ranges.KD_difference_to_sell:
											for K_level_to_buy in ranges.K_level_to_buy:
												for D_level_to_buy in ranges.D_level_to_buy:
													for KD_difference_to_buy in ranges.KD_difference_to_buy:
														for Weekday_buy in ranges.Weekday_buy:
															for Weekday_sell in ranges.Weekday_sell:
																for Volume_profile_locator in ranges.Volume_profile_locator:
																	strategy['company'] = company
																	strategy['bar_size'] = bar_size
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
																	
																	strting_strategy = ';'.join([str(bar_size), str(K_level_to_buy), str(D_level_to_buy), str(KD_difference_to_buy),
																								str(stop_loss), str(take_profit), str(K_level_to_sell), str(D_level_to_sell), str(KD_difference_to_sell),
																								str(stoch_parameters), str(Weekday_buy), str(Weekday_sell), str(Volume_profile_locator)
																								])
																	strting_strategy = strting_strategy.replace('None', '')
																	profit, history, buy_and_hold_profitability, capital_by_date = (-100,0,0,0)
																	if strting_strategy not in existing_strategies:
																		profit, history, buy_and_hold_profitability, capital_by_date = W7_backtest.main(price_data, strategy, historical_volume_profile, step)
															
																		strategy['profit'] = round(profit,1)
																		strategy['buy_and_hold_profitability'] = round(buy_and_hold_profitability,1)

																		with open(f'!Strategies_for_{company}.csv', 'a', encoding='utf-8') as file:
																			fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
																							'bar_size',
																							'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
																							'stop_loss', 'take_profit',
																							'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
																							'Stoch_parameters',
																							'Weekday_buy', 'Weekday_sell', 'Volume_profile_locator']
																			writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
																			writer.writerow(strategy)
																		
																	if profit > the_best_strategy['profit']:
																		the_best_strategy['company'] = company
																		the_best_strategy['profit'] = round(profit,1)
																		the_best_strategy['buy_and_hold_profitability'] = round(buy_and_hold_profitability,1)
																		the_best_strategy['bar_size'] = bar_size
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

																	print_status((the_best_strategy['profit'],
																				the_best_strategy['max_drawdown'],
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
																				profit,
																				Weekday_buy,
																				Weekday_sell,
																				Volume_profile_locator
																				))
																	i += 1
	except(KeyboardInterrupt):
		print('\n'*22)
						
	return the_best_strategy, capital_by_date

def main(company):
	the_best_strategy, capital_by_date = find_optimum_with_all_parameters(company)

	previous_max_profit = None
	with open(f'!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				previous_max_profit = float(x[1])
	if the_best_strategy['profit'] > previous_max_profit:
		max_drawdown = utils.max_drawdown_calculate(capital_by_date)
		the_best_strategy['max_drawdown'] = max_drawdown
		with open('!BestStrategies.csv', 'a', encoding='utf-8') as file:
			fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
							'bar_size',
							'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
							'stop_loss', 'take_profit',
							'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
							'Stoch_parameters',
							'Weekday_buy', 'Weekday_sell', 'Volume_profile_locator']
			writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
			writer.writerow(the_best_strategy)
	print('\n'*23)


if __name__ == '__main__':
	company = settings.company
	print(company)
	main(company)

