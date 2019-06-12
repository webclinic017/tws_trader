# WHY DO NOT WORK KeybpardInterrupt ???!!

# M.B. smthng needs to convert function -> class ??


import time
import threading

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import message, Connection

import positions_checking
import place_MKT_order
import rare2_filter_companies_and_collect_historical_data
from rare1_all_companies import set_of_all_companies
import settings
import stoch_pre_signal
import stoch_real_signal_await
import updater

# STRUCTURE:

# 0. RARE ACTIONS: - DONE
	# 0-1 Create a set of all companies(companylist.csv from nasdaq.com) - rare1_all_companies.py
	# 0-2 Choose interesting securities and collect historical data(set_of_all_companies, filters=(price, average_volume), timeframes)
	#									 - 0-2_filter_companies_and_collect_historical_data.py
	# -------------------
# >>> companylist.csv
# >>> initial 'stock screener' filters
# >>> timeframe
#
# <<< !MyCompanies.csv
# <<< price data in sertain timeframe

# 1. EVERY <timeline> ACTIONS:
	# 1-1 Udate historical data - DONE! ~20 mins
	# 1-2 Analysis:
	#		- volume analysis: signals db
	#		- comare signals and range watchlist by signal force
	# 1-3 Make trading decisions
	#		- account alanysis
	# 1-4 Trading

def historical_data_collect():
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	i = 1
	for company in set_of_all_companies():
		print(f'{i}/{len(set_of_all_companies())}')
		i += 1
		rare2_filter_companies_and_collect_historical_data.main(conn, company)
	conn.disconnect()

def update_everyday_data_for_MyCompanies(c):
	while True:
		time.sleep(60*60*24)	# update every day
		updater.main(c)	 # N.B.: 2 D updating depth!
		stoch_pre_signal.main(c)
#		time.sleep(60*60*24)	# update every day

def real_signal_await(c):
	while True:
		set_of_companies_in_position = positions_checking.main(c)
		tuple_of_sets_with_comanies_to_buy_and_sell = stoch_real_signal_await.main(c) # N.B.: 1 D updating depth!
		set_of_companies_to_buy = tuple_of_sets_with_comanies_to_buy_and_sell[0]
		set_of_companies_to_sell = tuple_of_sets_with_comanies_to_buy_and_sell[1]
		if set_of_companies_to_buy != set():
			for company in set_of_companies_to_buy:
				if company not in set_of_companies_in_position:
					place_MKT_order.main(c, company, 1, 'BUY')
		time.sleep(60*25)	# update every 25 mins

def main():
# 0. RARE ACTIONS:
	# historical_data_collect()
# 1. EVERY <timeline> ACTIONS:
	# 1-1 Udate historical data - DONE! ~20 mins
	updating_prices = threading.Thread(target=update_everyday_data_for_MyCompanies, args=(conn,))
	updating_positions = threading.Thread(target=real_signal_await, args=(conn,))
	simultaneous_processes = [updating_prices,
							updating_positions
						]
	for process in simultaneous_processes:
		process.start()


	# 1-2 Analysis:
	#		- comare signals and range watchlist by signal force

	# 1-3 Make trading decisions
	#		- account alanysis

	# 1-4 Trading

#	conn = Connection.create(port=7497, clientId=0)
#	contract = create_contract('FB', 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print_message_from_ib)
#	conn.connect()
#	order = create_LMT_order('LMT', 1, 'BUY', 100)
#	tws_conn.placeOrder(order_id, contract, order)
#	time.sleep(5)
#	conn.disconnect()






if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
		main()
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()





# It may be usefull:


# Get account info:
# def prt_msg(msg):
# 	if msg.key == 'BuyingPower' and msg.currency == 'USD':
# 		print(f"Buying Power: ${msg.value}")
# 	if msg.key == 'TotalCashValue' and msg.currency == 'USD':
# 		print(f'Total: ${msg.value}')
# 	if msg.key == 'GrossPositionValue' and msg.currency == 'USD':
# 		print(f'Gross positions value: ${msg.value}')
# 	if msg.key == 'UnrealizedPnL' and msg.currency == 'USD':
# 		print(f'Unrealized P&L: ${msg.value}')
#
#	c.registerAll(print)	# this is for errors searching
#	c.register(prt_msg, message.updateAccountValue)	#	message.updatePortfolio
#	c.reqAccountUpdates(True, settings.ACCOUNT_NUMBER)





