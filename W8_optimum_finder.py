import csv
from datetime import datetime
import logging
import time

from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D

from indicators import stochastic
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


def my_range(start, stop, step=0.5):	# stop is included
	float_list = []
	x = start
	while x <= stop:
		float_list.append(round(x, 1))
		x += step
	return tuple(float_list)

#TSLA;203.89400549999928;12.0595401895667;-28.706049999999994;;(19, 29);1;4;8.5;;;0;(19, 12, 5)
class ranges:
	bar_size = ('5 mins',) 	# '10 mins', '20 mins', '1 hour', '1 day') 	# 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
	K_level_to_buy = (None,)	#(1,20),(20,60), (40,80),(80,100))
	D_level_to_buy = (None,)	#(19,28),(20,28),(18,29),(20,29),(18,30))	#None, (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	KD_difference_to_buy = (-1,0)	# -1, 0, None)
	stop_loss = (4,6,9.5, 10.5, 15)	#3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5)	#my_range(4, 7)
	take_profit = (3,4.3,4.7,9,11,12)#(None, 8.5, 8.6, 8.7, 8.8, 8.9, 9, 10.1, 10.2, 10.3, 10.4, 10.5)	#my_range(6.5, 8.5)
	K_level_to_sell = (None,)	#(1,20),(20,60), (40,80),(80,100))
	D_level_to_sell = (None,)	#(80,100),(60,80))	# (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	KD_difference_to_sell = (1,)	#1, -1, 0, None)	# -1, 1, None)
	stoch_period = (23,24,26,27)#range(7, 50, 7)	#range(3,101, 10)
	slow_avg = (5,6,7,15,25,35,45)#range(7,50,7)	#range(3,101, 10)
	fast_avg = (26,28,29,30) # range(2,32,5)#range(3,13,3)	#range(3,51, 5)


def print_status(info):
	a = len(ranges.K_level_to_buy)*len(ranges.D_level_to_buy)*len(ranges.KD_difference_to_buy)*len(ranges.stop_loss)
	b = len(ranges.take_profit)*len(ranges.K_level_to_sell)*len(ranges.D_level_to_sell)*len(ranges.KD_difference_to_sell)
	c = len(ranges.stoch_period)*len(ranges.slow_avg)*len(ranges.fast_avg)*len(ranges.bar_size)
	total_number = a*b*c
	done_number = info[12]
	percentage = int((done_number/total_number)*30)
	# if done_number < total_number:
	# 	print(f'  Calculating: {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number}', ' '*5, end='\r')
	# else:
	# 	time_now = time.strftime("%m/%d/%Y %I:%M %p", time.gmtime())
	# 	print(f'  Calculating: {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number}')
	
	def choosen_parameter(choosen_parameter, tuple_of_parameters):
		if choosen_parameter == None:
			choosen_parameter = 'None'
		choosen_start = '\033[1m'+'\033[4m'+'\033[91m'
		choosen_end = '\033[0m'
		if len(tuple_of_parameters) > 1:
			slice_before_choosen = tuple_of_parameters[:tuple_of_parameters.index(choosen_parameter)]
			slice_after_choosen = tuple_of_parameters[tuple_of_parameters.index(choosen_parameter)+1:]
			before_choosen = '' if len(slice_before_choosen) == 0 else ', '.join(str(x) for x in slice_before_choosen)+', '
			choosen = choosen_start + str(choosen_parameter) + choosen_end
			after_choosen = '' if len(slice_after_choosen) == 0 else ', '+', '.join(str(x) for x in slice_after_choosen)
			return (before_choosen, choosen, after_choosen)
		else:
			return (str(choosen_parameter), ' ', ' ')

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
=========================================================================
Best founded strategy's profitability:	{round(info[0],1)}%         
Buy and hold profitability:		{round(info[2],1)}%       
=========================================================================
Calculated: {int(round(percentage*3.33, 0))}% |{"█"*percentage+' '*(30 - percentage)}| {done_number}/{total_number} combinations                   
""")
	print('\033[F'*20)

def find_optimum_with_all_parameters(company):
	the_best_strategy = {}
	strategy = {}
	the_best_strategy['profit'] = 0
	the_best_strategy['max_drawdown'] = 0
	try:
		i = 1
		for bar_size in ranges.bar_size:
			price_data = utils.get_price_data(company, bar_size)
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
														profit, history, buy_and_hold_profitability, capital_by_date = W7_backtest.main(price_data, 
																																		{'K_level_to_buy': K_level_to_buy,
																																		'D_level_to_buy': D_level_to_buy,
																																		'KD_difference_to_buy': KD_difference_to_buy,
																																		'stop_loss': stop_loss,
																																		'take_profit': take_profit,
																																		'K_level_to_sell': K_level_to_sell,
																																		'D_level_to_sell': D_level_to_sell,
																																		'KD_difference_to_sell': KD_difference_to_sell,
																																		'Stoch_parameters': (stoch_period, slow_avg, fast_avg)
																																		})
														
														strategy['company'] = company
														strategy['profit'] = profit
														strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
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

														with open(f'!Strategies_for_{company}.csv', 'a', encoding='utf-8') as file:
															fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
																			'bar_size',
																			'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
																			'stop_loss', 'take_profit',
																			'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
																			'Stoch_parameters']
															writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
															writer.writerow(strategy)
														
														if profit > the_best_strategy['profit']:
															the_best_strategy['company'] = company
															the_best_strategy['profit'] = profit
															the_best_strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
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
																	bar_size
																	))
														i += 1
	except(KeyboardInterrupt):
		print('\n'*19)
		print(f"""  The best strategy was found is:
Bar size:			{the_best_strategy['bar_size']}
K level to buy:			{the_best_strategy['K_level_to_buy']}              
D level to buy:			{the_best_strategy['D_level_to_buy']}           
KD difference to buy:		{the_best_strategy['KD_difference_to_buy']}           
stop loss:			{the_best_strategy['stop_loss']}           
take profit:			{the_best_strategy['take_profit']}           
K level to sell:		{the_best_strategy['K_level_to_sell']}           
D level to sell:		{the_best_strategy['D_level_to_sell']}           
KD difference to sell:		{the_best_strategy['KD_difference_to_sell']}           
Stoch period:			{the_best_strategy['Stoch_parameters'][0]}           
Stoch slow average:		{the_best_strategy['Stoch_parameters'][1]}           
Stoch fast average:		{the_best_strategy['Stoch_parameters'][2]}           
=========================================================================
Profitability:			{round(the_best_strategy['profit'],1)}%         
Buy and hold profitability:	{round(the_best_strategy['buy_and_hold_profitability'],1)}%       
=========================================================================
""")
														
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
							'Stoch_parameters']
			writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
			writer.writerow(the_best_strategy)
	print('\n'*19)


if __name__ == '__main__':
	company = settings.company
	print(company)
	main(company)

