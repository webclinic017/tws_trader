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
import W6_open_position

import settings
import trade_signals_watcher
import utils


def print_status(info):
	print(f'''
Time:			{time.strftime('%H:%M', time.gmtime())}
Buy signal:		{info[0]}
Sell signal:		{info[1]}
Open position type:	{info[2]}
Price data row:		{info[3]}
Order id:		{info[4]}
''')
	# print('\033[F'*8)

# СДЕЛАТЬ ОТТАЛКИВАНИЕ ОТ ДАТЫ РЯДА С ЦЕНАМИ!!
# И НЕ проверять позиции, а верить себе, что если отправлялся ордер, то сейчас открыта позиция (или узнавать только первый раз как с ордер айди)

def main(conn, company, orderId):
	##### needs very seldom
	# utils.clear_all_about_collected_price_data()	# this takes from W1 about 10 hours
	# W1_filter_all_companies_and_get_price_data.main(c)
	
	strategy = utils.the_best_known_strategy(company)
	if utils.SEs_should_work_now():
		W3_price_data_updater.main(conn, company, strategy['Stoch_parameters'])
		last_row_with_price_data = utils.get_price_data(company)[-1]

		open_position_type = W4_checking_account.open_position(conn, company)
		quantity = int((W4_checking_account.buying_power(conn) * settings.POSITION_QUANTITY / 100) / float(last_row_with_price_data[1]))

		buy_signal = trade_signals_watcher.buy(last_row_with_price_data, 
												strategy['K_level_to_buy'],
												strategy['D_level_to_buy'],
												strategy['KD_difference_to_buy']
												)
		sell_signal = trade_signals_watcher.sell(last_row_with_price_data, 
												strategy['K_level_to_sell'],
												strategy['D_level_to_sell'],
												strategy['KD_difference_to_sell']
												)

		print_status((buy_signal, sell_signal, open_position_type, last_row_with_price_data, orderId))

		if open_position_type == None:
			if buy_signal[0] == 'buy':
				print(f'Buying {company}')
				action = 'BUY'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 - strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 + strategy['take_profit'] / 100), 2)
				W6_open_position.place_bracket_order(conn, company, action, stop_loss, take_profit, quantity, orderId)
				orderId += 3
			if sell_signal[0] == 'sell':
				print(f'Selling {company}')
				action = 'SELL'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 + strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 - strategy['take_profit'] / 100), 2)
				W6_open_position.place_bracket_order(conn, company, action, stop_loss, take_profit, quantity, orderId)
				orderId += 3
		if open_position_type == 'long':
			if sell_signal[0] == 'sell':
				print('Close long by signal + open short')
				W6_open_position.close_position(conn, company, orderId)
				orderId += 1
				action = 'SELL'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 + strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 - strategy['take_profit'] / 100), 2)
				W6_open_position.place_bracket_order(conn, company, action, stop_loss, take_profit, quantity, orderId)
				orderId += 3
		if open_position_type == 'short':
			if sell_signal[0] == 'sell':
				print('Close short by signal + open long')
				W6_open_position.close_position(conn, company, orderId)
				orderId += 1
				action = 'BUY'
				stop_loss = round(float(last_row_with_price_data[1]) * (1 - strategy['stop_loss'] / 100), 2)
				take_profit = round(float(last_row_with_price_data[1]) * (1 + strategy['take_profit'] / 100), 2)
				W6_open_position.place_bracket_order(conn, company, action, stop_loss, take_profit, quantity, orderId)
				orderId += 3

		time.sleep(60*15)

	else:
		print(' Stock exchange is not working now. Awaiting till it opens.', end = '\r')
		time.sleep(60*25)	# 25 mins

if __name__ == "__main__":
	try:
		conn = Connection.create(port=7497, clientId=0)
		conn.connect()
		conn.registerAll(print)	# this is for errors searching
		count = 1
		orderId = W4_checking_account.next_valid_order_Id(conn)
		while True:
			if conn.isConnected():
				company = settings.company
				main(conn, company, orderId)
			else:
				print(f'  CONNECTION ERROR! TRYING TO RECONNECT! Attempt: {count}', end='\r')
				time.sleep(40)
				count += 1
				conn.connect()
		conn.disconnect()
	except(KeyboardInterrupt):
		print('\n'*10)
		print('\nBye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

