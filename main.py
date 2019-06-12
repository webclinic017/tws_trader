import time
import threading

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import message, Connection

import positions_and_orderId_checking
import place_MKT_order
import rare2_filter_companies_and_collect_historical_data
from rare1_all_companies import set_of_all_companies
import settings
import stoch_pre_signal
import stoch_real_signal_await
import updater

def main(c):
	while True:
		set_of_companies_in_position = positions_and_orderId_checking.main(c)[0]
		tuple_of_sets_with_comanies_to_buy_and_sell = stoch_real_signal_await.main(c) # N.B.: 1 D updating depth!
		set_of_companies_to_buy = tuple_of_sets_with_comanies_to_buy_and_sell[0]
		set_of_companies_to_sell = tuple_of_sets_with_comanies_to_buy_and_sell[1]
		if set_of_companies_to_buy != set():
			order_id = positions_and_orderId_checking.main(c)[1]
			for company in set_of_companies_to_buy:
				if company not in set_of_companies_in_position:
					print('Trying to buy', company)
					time.sleep(3)
					place_MKT_order.main(c, company, 1, 'BUY', order_id)
				order_id += 1
		time.sleep(60*25)	# update every 25 mins

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

