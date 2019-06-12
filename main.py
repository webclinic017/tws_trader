import time
import threading

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import message, Connection

import Worker1_filter_all_companies_and_historical_data_update
import Worker2_everyday_price_data_collect
import Worker3_make_watchlist_of_interesting_companies
import Worker4_real_signal_awaiter
import Worker5_place_MKT_order
import positions_and_orderId_checking

def main(c):
	# Worker1_filter_all_companies_and_historical_data_update.main(c)	# needs very seldom
	# Worker2_everyday_price_data_collect.main(c)	# needs 1-3 times per day
#	Worker3_make_watchlist_of_interesting_companies.main()	# needs each time after Worker3

	# companies_to_place_order = Worker4_real_signal_awaiter.main(c)	# Worker4 must go a long time after Worker3 !!!
	# set_of_companies_to_buy = companies_to_place_order[0]
	# set_of_companies_to_sell = companies_to_place_order[1]
	# print(set_of_companies_to_buy)
	# print(set_of_companies_to_sell)

	set_of_companies_to_buy = {'Z', 'RIG'}
	order_id = int(positions_and_orderId_checking.main(conn)[1])
	for company in set_of_companies_to_buy:
		Worker5_place_MKT_order.main(c, company, 'BUY', order_id)
		order_id += 1









	# while True:
	# 	set_of_companies_in_position = positions_and_orderId_checking.main(c)[0]
	# 	tuple_of_sets_with_comanies_to_buy_and_sell = stoch_real_signal_await.main(c) # N.B.: 1 D updating depth!
	# 	set_of_companies_to_buy = tuple_of_sets_with_comanies_to_buy_and_sell[0]
	# 	set_of_companies_to_sell = tuple_of_sets_with_comanies_to_buy_and_sell[1]
	# 	if set_of_companies_to_buy != set():
	# 		order_id = positions_and_orderId_checking.main(c)[1]
	# 		for company in set_of_companies_to_buy:
	# 			if company not in set_of_companies_in_position:
	# 				print('Trying to buy', company)
	# 				time.sleep(3)
	# 				place_MKT_order.main(c, company, 1, 'BUY', order_id)
	# 			order_id += 1
	# 	time.sleep(60*25)	# update every 25 mins

if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
		main(conn)
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

# Worker1 - filter_all_companies_and_historical_data_update.py	| (c) | companylist.csv => !MyCompanies.csv + historical_data/
# Worker2 - everyday_price_data_collect.py						| (c) | !MyCompanies.csv => historical_data/
# Worker3 - make_watchlist_of_interesting_companies.py			| ()  | !MyCompanies.csv + historical_data/ =>
# 																		=> Stoch_watchlist_to_buy.csv + Stoch_watchlist_to_sell.csv
# Worker4 - real_signal_awaiter.py								| (c) | Stoch_watchlist_to_buy.csv + Stoch_watchlist_to_sell.csv +
# 																		+ historical_data => 
# Worker5 - place_MKT_order.py							| (c, company) | => 







