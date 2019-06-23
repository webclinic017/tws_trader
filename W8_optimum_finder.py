import csv
from datetime import datetime
import logging
import time
import json

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
	K_level_to_buy = (None,)	#(1,20),(20,60), (40,80),(80,100))
	D_level_to_buy = (None,(20,30))	#(19,28),(20,28),(18,29),(20,29),(18,30))	#None, (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	KD_difference_to_buy = (None,-1,)	# -1, 0, None)
	stop_loss = (6,10)#(None, 3.5, 3.6, 3.7, 3.8, 3.9, 4, 4.1, 4.2, 4.3, 4.4, 4.5)	#my_range(4, 7)
	take_profit = (None, 1,2,5)#(None, 8.5, 8.6, 8.7, 8.8, 8.9, 9, 10.1, 10.2, 10.3, 10.4, 10.5)	#my_range(6.5, 8.5)
	K_level_to_sell = (None,)	#(1,20),(20,60), (40,80),(80,100))
	D_level_to_sell = (None,(70,80))	#(80,100),(60,80))	# (10,20),(20,30),(30,40),(40, 50), (50,60), (70, 80), (90,100))
	KD_difference_to_sell = (0,)	#1, -1, 0, None)	# -1, 1, None)
	stoch_period = (5,6,7,8,9)#range(7, 50, 7)	#range(3,101, 10)
	slow_avg = (11,12,13,14,15,16,17)#range(7,50,7)	#range(3,101, 10)
	fast_avg = range(2,16)#range(3,13,3)	#range(3,51, 5)


def print_status(info):
	a = len(ranges.K_level_to_buy)*len(ranges.D_level_to_buy)*len(ranges.KD_difference_to_buy)*len(ranges.stop_loss)
	b = len(ranges.take_profit)*len(ranges.K_level_to_sell)*len(ranges.D_level_to_sell)*len(ranges.KD_difference_to_sell)
	c = len(ranges.stoch_period)*len(ranges.slow_avg)*len(ranges.fast_avg)
	total_number = a*b*c
	done_number = info[12]
	percentage = int((done_number/total_number)*30)
	# if done_number < total_number:
	# 	print(f'  Calculating: {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number}', ' '*5, end='\r')
	# else:
	# 	time_now = time.strftime("%m/%d/%Y %I:%M %p", time.gmtime())
	# 	print(f'  Calculating: {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number}')
	print(f"""  
K level to buy:			{info[3]} from {ranges.K_level_to_buy}              
D level to buy:			{info[4]} from {ranges.D_level_to_buy}           
KD difference to buy:		{info[5]} from {ranges.KD_difference_to_buy}           
stop loss:			{info[6]} from {ranges.stop_loss}           
take profit:			{info[7]} from {ranges.take_profit}           
K level to sell:		{info[8]} from {ranges.K_level_to_sell}           
D level to sell:		{info[9]} from {ranges.D_level_to_sell}           
KD difference to sell:		{info[10]} from {ranges.KD_difference_to_sell}           
Stoch period:			{info[11][0]} from {ranges.stoch_period}           
Stoch slow average:		{info[11][1]} from {ranges.slow_avg}           
Stoch fast average:		{info[11][2]} from {ranges.fast_avg}           
=========================================================================
Best founded strategy's profitability:	{round(info[0],1)}%      
Best founded strategy's max drawdown:	{round(info[1],1)}%     
Buy and hold profitability:		{round(info[2],1)}%       
=========================================================================
Calculated: {int(round(percentage*3.33, 0))}% |{"█"*percentage+' '*(30 - percentage)}| {done_number}/{total_number} combinations                   
""")
	print('\033[F'*20)

def find_optimum_with_all_parameters(price_data, company):
	the_best_strategy = {}
	strategy = {}
	the_best_strategy['profit'] = 0
	the_best_strategy['max_drawdown'] = 0
	try:
		i = 1
		for fast_avg in ranges.fast_avg:
			for slow_avg in ranges.slow_avg:
				for stoch_period in ranges.stoch_period:
					stoch_parameters = (stoch_period, slow_avg, fast_avg)
					price_data = stochastic.main(price_data, stoch_parameters)
					for stop_loss in ranges.stop_loss:	# range(2,5):#my_range(0.5, 4, 0.5):
						for take_profit in ranges.take_profit:	#my_range(1, 10, 1):
							for K_level_to_sell in ranges.K_level_to_sell:	# (1,20), (20,80), (80,100)):
								for D_level_to_sell in ranges.D_level_to_sell:	#(80,100)):	# (1,20), (20,80), (80,100)):
									for KD_difference_to_sell in ranges.KD_difference_to_sell:	#(-1, 0):	#, 1):	#(None, -1, 0, 1):
										for K_level_to_buy in ranges.K_level_to_buy:	# (1,20), (20,80), (80,100)):
											for D_level_to_buy in ranges.D_level_to_buy:	#(None, (1,20),):	# (20,80), (80,100)):
												for KD_difference_to_buy in ranges.KD_difference_to_buy:	#(-1, 0, 1):	#(None, -1, 0, 1):
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
													max_drawdown = utils.max_drawdown_calculate(capital_by_date)
													strategy['company'] = company
													strategy['profit'] = profit
													strategy['max_drawdown'] = max_drawdown
													strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
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
																		'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
																		'stop_loss', 'take_profit',
																		'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
																		'Stoch_parameters']
														writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
														writer.writerow(strategy)
													
													if profit > the_best_strategy['profit']:
														the_best_strategy['company'] = company
														the_best_strategy['profit'] = profit
														the_best_strategy['max_drawdown'] = max_drawdown
														the_best_strategy['buy_and_hold_profitability'] = buy_and_hold_profitability
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
																i
																))
													i += 1
	except(KeyboardInterrupt):
		print('\n'*18)
		print(f"""  The best strategy was found is:
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
Max drawdown:			{round(the_best_strategy['max_drawdown'],1)}%     
Buy and hold profitability:	{round(the_best_strategy['buy_and_hold_profitability'],1)}%       
=========================================================================
""")
														
	return the_best_strategy


def main(company):
	price_data = utils.get_price_data(company)
	#open(f'!Strategies_for_{company}.csv', "w+").close()
	the_best_strategy = find_optimum_with_all_parameters(price_data, company)
	with open('!BestStrategies.csv', 'a', encoding='utf-8') as file:
		fieldnames = ['company', 'profit', 'max_drawdown', 'buy_and_hold_profitability',
						'K_level_to_buy', 'D_level_to_buy', 'KD_difference_to_buy',
						'stop_loss', 'take_profit',
						'K_level_to_sell', 'D_level_to_sell', 'KD_difference_to_sell',
						'Stoch_parameters']
		writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
		writer.writerow(the_best_strategy)
	print('\n'*18)


if __name__ == '__main__':
	# for x in {'TSLA',}:# 'WMT', 'SPY', 'F', 'MS', 'GM', 'TSLA',
	# 			#'GE', 'AMD', 'MU', 'NVDA', 'AAPL', 'BA', 'FB',
	# 			#'GS', 'EBAY', 'C', 'TWTR', 'AMZN', 'IBM', 'KO', 'TQQQ'}:
	# 	#try:
	company = settings.company
	print(company)
	main(company)
	#	except(ValueError):
	#		print('incorrect data                         \n')

