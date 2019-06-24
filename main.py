# TO DO list:

# tws при потере связи чтобы чаще восстанавливаться пробовала
# update HOG

# main:
# 1. изменить структуру поиска нужных активов - без отслеживания, а в моменте. анализировать определенный период стохастика
# 2. запихнуть "стратегию" в настройки, main сделать по типу воронки

# 1. GET abd FILTER all companies:
# - перестал торговаться - данные не собираем. последняя дата данных должна быть свежей
# - Сбор данных - прикрутить вторую попытку на основе определенных ошибок + показывать результат оставшихся "ошибок"
# - может сразу добавлять данные индекатора в исторические данные?
# - иногда tws путает close и volume при сборе данных!!! - Как решить? HOME,
# AXSM (20190611  21:30:00),
# DUK (20190222  19:30:00)
# XOM 20190318  21:30:00
# A (20190102  19:30:00)
# - исправить эту ошибку
# - неправильные данные - вообще не те иногда!!!!

# 5. WATCH for signals:
# - Here I found ... companies to buy - исключить те, которые уже куплены и выставлены ордера

# 6. TRADE:
# - отработать все ошибки при выполнении ордеров!!!
# - Orders SL TP rejected by system: parent order partially or fully filled
# - исполнение ордеров - прикрутить проверку - не отменен ли ордер (есть ли позиция и т.д.) + вторая попытка в случае определенных ошибок
	# отправлять parent order -> sleep -> + дочерние ордера?? м.б. так?

#######################################################################################################################
#### WORKING SCHEME: ####
# 										| frequency	|			| result in db (out)	| in
# 1. GET and FILTER all companies,		| 			|			|						| https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nasdaq&render=download
# 										|			|			|						| https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=nyse&render=download
# 										|			|			|						| https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=amex&render=download
# 	get price data 						| 2/10		|			| !MyCompanies.csv +	|
# 										|			|			| + historical data 	|
# 2. SORT companies						| 4/10		|			| 	list of companies	| !MyCompanies + ...
#######################################################################################################################
# 3. UPDATE data 						| 10/10		|			| 	list of companies	| !MyCompanies + ...
# 4. MANAGE portfolio					| 10/10		|			| 						|
# 5. WATCH for trade signals			| 10/10		| strategy	| 	buy or sell signal	| 
# 6. TRADE with strong trading signals	| 10/10		|			| 						|
#######################################################################################################################
# 7. BACKTEST							|
# 8. FIND optimal strategy for security	|
#######################################################################################################################

'''
.
├── README.me
├── requirements.txt
├── setup.py
└── src
    ├── __init__.py
    ├── client.py
    ├── logic.py
    ├── models.py
    └── run.py
'''


import csv
import time

from ib.opt import Connection

import W1_filter_all_companies_and_get_price_data
import W2_sort_companies
import W3_price_data_updater

import Worker3_real_signal_awaiter
import Worker4_open_position
import positions_and_orderId_checking
import utils

def main(c):
	##### needs very seldom
	# utils.clear_all_about_collected_price_data()	# this takes from W1 about 10 hours
	# W1_filter_all_companies_and_get_price_data.main(c)

	if utils.SEs_should_work_now():
		
		W3_price_data_updater.main(c)

		company = ''
		if portfolio_manager:
			wait signal...

		else:
			close?


		if want_to_open_position: # no open positions
			if open_signal[0] == 'buy':	# signal to buy
				if open_signal[1] == 'MKT' and i < len(list_with_price_data) - 1:
					open_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					want_to_open_position = False
					quantity = int(capital / open_order_price)
					history.append(f'{date}: bought {quantity} at ${open_order_price}')
		else:	# checking open position if it is signal to close
			if stop_loss != None and take_profit != None:
				sl = open_order_price - ((stop_loss / 100) * open_order_price)
				tp = (take_profit / 100 + 1) * open_order_price
				if low_price <= sl:
					close_order_price = round(sl, 2)
					profit = round((close_order_price - open_order_price) * quantity - (0.0065 * 2)*10, 2)		# comission + *10 smth wrong
					capital += profit
					history.append(f'{date}: SL, close at ${close_order_price}, profit: -${abs(round(profit))}')				
					want_to_open_position = True
				if high_price >= tp and want_to_open_position == False:
					close_order_price = round(tp, 2)
					profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
					capital += profit
					history.append(f'{date}: TP, close at ${close_order_price}, profit: ${round(profit)}')				
					want_to_open_position = True
			if close_signal[0] == 'close' and want_to_open_position == False and i < len(list_with_price_data) - 1:
				if close_signal[1] == 'MKT':
					close_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
					capital += profit
					history.append(f'{date}: STRATEGY SIGNAL, close at ${close_order_price}, profit: ${round(profit)}')				
					want_to_open_position = True





		time.sleep(60*25)	# 25 mins
	else:
		if int(time.strftime("%H", time.gmtime())) == 21:	# = 00:00 MSK
			continue
		else:
			print(' Stock exchange is not working now. Awaiting till it opens.', end = '\r')
			time.sleep(60*10)	# checking time every 10 mins























	if True:	#utils.SEs_should_work_now():
		companies_to_place_order = Worker3_real_signal_awaiter.main(c)
		set_of_companies_to_buy = companies_to_place_order[0]
		set_of_companies_to_sell = companies_to_place_order[1]
		print(f'Found {len(set_of_companies_to_buy)} companies to buy: {set_of_companies_to_buy}')
		print(f'Found {len(set_of_companies_to_sell)} companies to sell: {set_of_companies_to_sell}')
		order_id = int(positions_and_orderId_checking.main(c)[1])
		if set_of_companies_to_buy != set():
			for company in set_of_companies_to_buy:
				print(f'Buying {company}')
				Worker4_open_position.main(c, company, 'BUY', order_id)
				order_id += 3
		if set_of_companies_to_sell != set():
			for company in set_of_companies_to_sell:
				print(f'Selling {company}')
				Worker4_open_position.main(c, company, 'SELL', order_id)
				order_id += 3
		time.sleep(60*25)	# 25 mins
	else:
		if int(time.strftime("%H", time.gmtime())) == 21:	# = 00:00 MSK
			W3_price_data_updater.main(c)
		else:
			print(' Stock exchange is not working now. Awaiting till it opens.', end = '\r')
			time.sleep(60*25)	# 25 mins

if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
		while True:
#			conn.registerAll(print)	# this is for errors searching
			main(conn)
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

