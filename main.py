import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, dispatcher, message

from all_companies import set_of_all_companies
import get_historical_data
import volume_analysis

order_id = 42

def print_message_from_ib(msg):
	print(msg)

def create_contract(symbol, sec_type, exch, prim_exch, curr):
	"""Create a Contract object defining what will
	be purchased, at which exchange and in which currency.

	symbol - The ticker symbol for the contract
	sec_type - The security type for the contract ('STK' is 'stock')
	exch - The exchange to carry out the contract on
	prim_exch - The primary exchange to carry out the contract on
	curr - The currency in which to purchase the contract"""
	contract = Contract()
	contract.m_symbol = symbol
	contract.m_secType = sec_type
	contract.m_exchange = exch
	contract.m_primaryExch = prim_exch
	contract.m_currency = curr
	return contract

def create_LMT_order(order_type, quantity, action, price):
	"""Create an Order object (Market/Limit) to go long/short.

	order_type - 'MKT', 'LMT' for Market or Limit orders
	quantity - Integral number of assets to order
	action - 'BUY' or 'SELL'"""
	order = Order()
	order.m_orderType = order_type
	order.m_totalQuantity = quantity
	order.m_action = action
	order.m_lmtPrice = price
	return order
	order_id += 1

def historical_data_handler(msg):
    # The response data callback function
    # print (msg.reqId, msg.date, msg.open, msg.close, msg.high, msg.low)
    print(f"Date: {msg.date}, open: {msg.open}, close: {msg.close}, high: {msg.high}, low: {msg.low}, volume: {msg.volume}")


if __name__ == "__main__":
# STRUSTURE:
# 1. Updating historical data
# 2. Historical data analysis
# 3. Make trading decisions
# 4. Trading

# 1. Historical data updating functional:
#	for company in set_of_all_companies():
#		get_historical_data.main(company, '3 Y', '1 day')
#	here we need UPDATE_historical_data


# 2. Historical data analysis:
	company = 'SPY'
	get_historical_data.main(company, '3 Y', '1 day')
	volume_analysis.main(company, '3 Y', '1 day')



# 4. Trading functional:
#	conn = Connection.create(port=7497, clientId=0)
#	contract = create_contract('FB', 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print_message_from_ib)
#	conn.connect()
#	order = create_LMT_order('LMT', 1, 'BUY', 100)
#	tws_conn.placeOrder(order_id, contract, order)
#	time.sleep(5)
#	conn.disconnect()
























































