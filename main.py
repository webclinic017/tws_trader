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
# 3. UPDATE data 						| 10/10		|			| 	list of companies	| !MyCompanies + ...
# 4. CHECKING account 					| 10/10		|			| 						|
# 5. WATCH for trade signals			| 10/10		| strategy	| 	buy or sell signal	| 
# 6. TRADE with strong trading signals	| 10/10		|			| 						|
#######################################################################################################################
# 7. BACKTEST							|
# 8. FIND optimal strategy for security	|
# 9. ANALYSER strategy parameters 		|			|			|
#######################################################################################################################


import csv
import time

from ib.opt import Connection, sender

import W4_checking_account
import W1_filter_all_companies_and_get_price_data
import W2_sort_companies
import W3_price_data_updater
import W6_position_manager

from indicators import volume_profile
import settings
import trade_signals_watcher
import utils


def print_status(info):
	print(f'''
Time:		{time.strftime('%H:%M', time.gmtime())}
Signal:		{info[0]}
Open position:	{info[1]}
Price data row:	{info[2]}
Order id:	{info[3]}
''')
	# print('\033[F'*8)


def main(company):
	##### needs very seldom
	# utils.clear_all_about_collected_price_data()	# this takes from W1 about 10 hours
	# W1_filter_all_companies_and_get_price_data.main(c)
	
	strategy = utils.the_best_known_strategy(company)
	if utils.SEs_should_work_now():
		W3_price_data_updater.main(company, strategy['Stoch_parameters'], strategy['bar_size'])
		time.sleep(6)
		price_data = utils.get_price_data(company, strategy['bar_size'])


		open_position_type = W4_checking_account.what_position_is_open_now_for(company)
		time.sleep(7)
		orderId = W4_checking_account.next_valid_order_Id()
		time.sleep(3)
		buying_power = W4_checking_account.buying_power()
		time.sleep(3)

		first_date = price_data[1][0]
		end_date = [int(first_date[:4]), int(first_date[4:6]), int(first_date[6:8])]
		historical_volume_profile, step = volume_profile.historical_volumes(end_date)
		new_volume_profile = volume_profile.update_volume_profile(price_data, step, historical_volume_profile)
		
		signal = trade_signals_watcher.signal(price_data, new_volume_profile, strategy)

		print_status((signal, open_position_type, price_data[-1], orderId))

		last_row_with_price_data = price_data[-1]
		quantity = int((buying_power * settings.POSITION_QUANTITY / 100) / float(last_row_with_price_data[1]))
		
		if open_position_type == None:
			if signal == 'buy':
				print(f'Buying {company}')
				action = 'BUY'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 - strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 + strategy['take_profit'] / 100), 2)
				W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
			if signal == 'sell':
				print(f'Selling {company}')
				action = 'SELL'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 + strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 - strategy['take_profit'] / 100), 2)
				W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
		if open_position_type == 'long':
			if signal == 'sell':
				print('Closing long by signal...')
				W6_position_manager.close_position(company, orderId)
				orderId += 1
				time.sleep(20)
				action = 'SELL'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 + strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 - strategy['take_profit'] / 100), 2)
				print('...and open short')
				W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
		if open_position_type == 'short':
			if signal == 'buy':
				print('Closing short by signal...')
				W6_position_manager.close_position(company, orderId)
				orderId += 1
				time.sleep(20)
				action = 'BUY'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 - strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 + strategy['take_profit'] / 100), 2)
				print('...and open long')
				W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	else:
		print(' Stock exchange is not working now. Awaiting till it opens.', end = '\r')
		time.sleep(60*25)	# 25 mins


if __name__ == "__main__":
	company = settings.company
	try:
		while True:
			start = time.clock()
			main(company)
			end = time.clock()
			cycle_executed_in_seconds = (end - start) / (24 * 60 * 60)
			time.sleep((60 * 30) - cycle_executed_in_seconds)	# new cycle runs every 30 mins
	except(KeyboardInterrupt):
		print('\nBye!')
	except():
		print('ERROR!')

