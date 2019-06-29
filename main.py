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
# 4. MANAGE portfolio					| 10/10		|			| 						|
# 5. WATCH for trade signals			| 10/10		| strategy	| 	buy or sell signal	| 
# 6. TRADE with strong trading signals	| 10/10		|			| 						|
#######################################################################################################################
# 7. BACKTEST							|
# 8. FIND optimal strategy for security	|
# 9. ANALYSER strategy parameters 		|			|			|
#######################################################################################################################


import csv
import time

from ib.opt import Connection

import account_checking
import W1_filter_all_companies_and_get_price_data
import W2_sort_companies
import W3_price_data_updater

import Worker4_open_position
import positions_and_orderId_checking
import settings
import utils

def main(conn, company):
	##### needs very seldom
	# utils.clear_all_about_collected_price_data()	# this takes from W1 about 10 hours
	# W1_filter_all_companies_and_get_price_data.main(c)
	
	strategy = utils.the_best_known_strategy(company)
	if True:	#utils.SEs_should_work_now():
		conn.registerAll(print)	# this is for errors searching
		W3_price_data_updater.main(conn, company, strategy['Stoch_parameters'])


		open_position_type = account_checking.open_position(conn, company)
		# check orders

		if open_position_type == None:
			# last row with price data --> trade_signals_watcher.py
			# if buy -> order to buy
			# if sell -> order to sell
			print('Buy or sell with signal')
		if open_position_type == 'long':
			# last row with price data --> trade_signals_watcher.py
			# if sell:
				# close position + order to sell (order to sell with quantity*2)
			print('Sell with a signal')
		if open_position_type == 'short':
			# last row with price data --> trade_signals_watcher.py
			# if buy:
				# order to buy with quantity*2	
			print('Buy with a signal')	






		time.sleep(60*25)




		#print(strategy)








	


		





	else:
		print(' Stock exchange is not working now. Awaiting till it opens.', end = '\r')
		time.sleep(60*25)	# 25 mins

if __name__ == "__main__":
	try:
		conn = Connection.create(port=7497, clientId=0)
		conn.connect()	
		while True:
			company = settings.company
			main(conn, company)
		conn.disconnect()
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

