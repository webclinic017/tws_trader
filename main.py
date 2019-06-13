import csv
import time

from ib.opt import Connection

import Worker1_filter_all_companies_and_historical_data_update
import Worker2_everyday_price_data_update
import Worker3_real_signal_awaiter
import Worker4_open_position
import positions_and_orderId_checking

def SEs_should_work_now():
	hours_now = int(time.strftime("%H", time.gmtime()))
	work_day = int(time.strftime("%w", time.gmtime()))
	if work_day == 1 or work_day == 6:
		work_day = False
		return False
	if work_day:
		if hours_now < 14 or hours_now > 19:
			return False

def main(c):
# '''This is traiding robot. It trades stocks at u.s. echanges.
# Here is structure:
# Worker1 - filter_all_companies_and_historical_data_update.py	| (c) | companylist.csv => !MyCompanies.csv + historical_data/
# Worker2 - everyday_price_data_collect.py						| (c) | !MyCompanies.csv => historical_data/ =>
# 																		=> Stoch_watchlist_to_buy.csv + Stoch_watchlist_to_sell.csv
# Worker3 - real_signal_awaiter.py								| (c) | Stoch_watchlist_to_buy.csv + Stoch_watchlist_to_sell.csv +
# 																		+ historical_data => 
# Worker4 - open_position.py							| (c, company) | => open posiions with trading signals
# Worker5 - positions_manager									| (c) | Closes positions with certain conditions.
# '''

	# Worker1_filter_all_companies_and_historical_data_update.main(c)	# needs very seldom

	if SEs_should_work_now():
		companies_to_place_order = Worker3_real_signal_awaiter.main(c)
		set_of_companies_to_buy = companies_to_place_order[0]
		set_of_companies_to_sell = companies_to_place_order[1]
		print(f'Found {len(set_of_companies_to_buy)} companies to buy: {set_of_companies_to_buy}')
		print(f'Found {len(set_of_companies_to_sell)} companies to buy: {set_of_companies_to_sell}')
		order_id = int(positions_and_orderId_checking.main(c)[1])
		if set_of_companies_to_buy != set():
			for company in set_of_companies_to_buy:
				Worker4_open_position.main(c, company, 'BUY', order_id)
				order_id += 1
		if set_of_companies_to_sell != set():
			for company in set_of_companies_to_sell:
				Worker4_open_position.main(c, company, 'SELL', order_id)
				order_id += 1
		time.sleep(60*25)	# 25 mins
	else:
		if int(time.strftime("%H", time.gmtime())) == 21:	# = 00:00 MSK
			Worker2_everyday_price_data_update.main(c)
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

