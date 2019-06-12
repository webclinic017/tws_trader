import csv
import time

from ib.ext.Order import Order
from ib.opt import Connection, message

import positions_and_orderId_checking
from settings import POSITION_QUANTITY
import utils

def create_MKT_order(quantity, action):
	"""Create an Order object (Market/Limit) to go long/short.
	order_type - 'MKT', 'LMT' for Market or Limit orders
	quantity - Integral number of assets to order
	action - 'BUY' or 'SELL'"""
	order = Order()
	order.m_orderType = 'MKT'
	order.m_totalQuantity = quantity
	order.m_action = action
	return order

def quantity_calculate(stock_ticker):
	last_price = None
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			last_price = float(row[2])
	quantity = POSITION_QUANTITY / last_price
	return int(quantity)

def main(conn, company, action, order_id):
	quantity = quantity_calculate(company)
	order_id = positions_and_orderId_checking.main(conn)[1]
	contract = utils.create_contract_from_ticker(company)
	order = create_MKT_order(quantity, action)
	conn.placeOrder(order_id, contract, order)

if __name__ == "__main__":
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	order_id = positions_and_orderId_checking.main(c)[1]
	main(c, 'AAPL', 'BUY', order_id)
	c.disconnect()

