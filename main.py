# TO DO list:

# main:
# 1. предусмотреть потерю связи: подождать, повторить последнее действие

# 1. GET abd FILTER all companies:
# - перестал торговаться - данные не собираем. последняя дата данных должна быть свежей
# - Сбор данных - прикрутить вторую попытку на основе определенных ошибок + показывать результат оставшихся "ошибок"
# - иногда в единичных случаях tws путает close и volume при сборе данных!!! - Исправить эту ошибку
# - неправильные данные - вообще не той компании - при массовом запросе даже с большой задержкой time.sleep!!!


# 6. TRADE:
# - отработать все ошибки при выполнении ордеров!!!
# - Orders SL TP rejected by system: parent order partially or fully filled
# - исполнение ордеров - прикрутить проверку - не отменен ли ордер (есть ли позиция и т.д.) + вторая попытка в случае определенных ошибок
	# отправлять parent order -> sleep -> + дочерние ордера?? м.б. так?


#### WORKING SCHEME: ####

#######################################################################################################################
# 										| frequency	|			| result in db (out)	| in
# 1. GET and FILTER all companies,		| 			|			|						| https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download
# 										|			|			|						| https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download
# 										|			|			|						| https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download
# 	get price data 						| 2/10		|			| !MyCompanies.csv +	|
# 										|			|			| + historical data 	|
# 2. SORT companies						| 4/10		|			| 	list of companies	| !MyCompanies + ...
#######################################################################################################################
# 3. untitled							| 10/10		|			| 	list of companies	| !MyCompanies + ...
# 4. CHECKING account 					| 10/10		|			| 						|
# 5. WATCH for trade signals			| 10/10		| strategy	| 	buy or sell signal	| 
# 6. TRADE with strong trading signals	| 10/10		|			| 						|
#######################################################################################################################
# 7. BACKTEST							|
# 8. FIND optimal strategy for security	|
# 9. ANALYSER strategy parameters 		|			|			|
#######################################################################################################################

import csv
from datetime import datetime, timedelta
import time

from ib.opt import Connection, sender

from indicators import volume_profile, stochastic, SMA, RS
import settings
import trade_signals_watcher
import utils
import W4_checking_account
import W6_position_manager


def print_status(info):
	# print('\033[F'*7)
	print(f'''
Time:		{time.strftime('%H:%M', time.gmtime())}                                    
Signal:		{info[0]}                                                      
Open position:	{info[1]}                                          
Price data row:	{info[2]}                                          
Order id:	{info[3]}                                               
Strategy:	{info[4]}
''')
	# print('\033[F'*8)


def print_waiting():
	working_shedule = utils.get_working_shedule('30 mins')
	# reset date in time now:
	time_now_str = datetime.strftime(datetime.now(), '%H:%M')
	time_now = datetime.strptime(time_now_str, '%H:%M')
	times_to_await = []
	for sheduled_time in working_shedule:
		sheduled_time = datetime.strptime(sheduled_time, '%H:%M')
		if time_now > sheduled_time:
			sheduled_time += timedelta(days=1)
		time_to_await = sheduled_time - time_now # + timedelta(seconds=60)
		times_to_await.append(time_to_await)
	time_to_await = min(times_to_await)
	hours_to_await = time_to_await.seconds//(60*60)
	minutes_to_await = (time_to_await.seconds//60)%60
	for count in range(4):
		print(f'  The next update will be in {hours_to_await} hours {minutes_to_await} minute(s){"."*count}     ', end='')
		print('\033[F'*1)
		time.sleep(1)


def main():
	company = settings.company
	strategy = utils.the_best_known_strategy(company)
	working_shedule = utils.get_working_shedule(strategy['bar_size'])

	utils.update_price_data(company, strategy['bar_size'])
	historical_data = utils.request_historical_data(company)
	price_data = utils.get_price_data(company, strategy['bar_size'])
	price_data = stochastic.update(price_data,
	                               strategy['indicators']['stochastic']['stoch_period'],
				                   strategy['indicators']['stochastic']['stoch_slow_avg'],
				                   strategy['indicators']['stochastic']['stoch_fast_avg'])
	price_data = SMA.update(price_data, strategy['indicators']['SMA']['period'])
	price_data = volume_profile.update(price_data, strategy['indicators']['volume_profile']['locator'], historical_data)
	price_data = RS.update(price_data, strategy['indicators']['RS'], historical_data)

	open_position_type = W4_checking_account.what_position_is_open_now_for(company)
	time.sleep(7)
	orderId = W4_checking_account.next_valid_order_Id()
	time.sleep(3)
	available_funds = W4_checking_account.available_funds()
	time.sleep(3)

	signal = trade_signals_watcher.signal(price_data, strategy['indicators'])

	print_status((signal, open_position_type, price_data[-1], orderId, strategy))

	last_close_price = price_data[-1]['Close']
	quantity = int((available_funds * settings.POSITION_QUANTITY) / last_close_price)
	
	if open_position_type == None:
		if signal == 'buy':
			print(f'Buying {company}')
			action = 'BUY'
			stop_loss = round(last_close_price * (1 - strategy['stop_loss'] / 100), 2)
			take_profit = round(last_close_price * (1 + strategy['take_profit'] / 100), 2)
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
		if signal == 'sell':
			print(f'Selling {company}')
			action = 'SELL'
			stop_loss = round(last_close_price * (1 + strategy['stop_loss'] / 100), 2)
			take_profit = round(last_close_price * (1 - strategy['take_profit'] / 100), 2)
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	if open_position_type == 'long':
		if signal == 'sell':
			print('Closing long by signal...')
			W6_position_manager.close_position(company, orderId)
			orderId += 1
			time.sleep(30)
			action = 'SELL'
			stop_loss = round(last_close_price * (1 + strategy['stop_loss'] / 100), 2)
			take_profit = round(last_close_price * (1 - strategy['take_profit'] / 100), 2)
			print('...and open short')
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	if open_position_type == 'short':
		if signal == 'buy':
			print('Closing short by signal...')
			W6_position_manager.close_position(company, orderId)
			orderId += 1
			time.sleep(30)
			action = 'BUY'
			stop_loss = round(last_close_price * (1 - strategy['stop_loss'] / 100), 2)
			take_profit = round(last_close_price * (1 + strategy['take_profit'] / 100), 2)
			print('...and open long')
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	time.sleep(60)
	print_waiting()
	while True:
		time_now_str = datetime.strftime(datetime.now(), '%H:%M')
		weekday = datetime.strftime(datetime.now(), '%w')
		if weekday not in ('6', '0'):
			print_waiting()
			if time_now_str in working_shedule:
				time.sleep(15)
				main()
		else:
			print('  Wait till stock exchange will be open.                  ')
			print('\033[F'*2)
			time.sleep(60)


if __name__ == "__main__":
	try:
		main()
	except(KeyboardInterrupt):
		print('\nBye!')
	except():
		print('ERROR!')

