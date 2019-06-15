import csv
import time

from ib.ext.Order import Order
from ib.opt import Connection, message

import positions_and_orderId_checking
from settings import POSITION_QUANTITY, TP, SL
import utils

def create_MKT_order(stock_ticker, quantity, action, order_id):

	parent_order = Order()
	parent_order.m_orderType = 'MKT'
	parent_order.m_totalQuantity = quantity
	parent_order.m_action = action
	parent_order.order_id = order_id
	parent_order.transmit = False

	last_price = None
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			last_price = float(row[2])

	tp = Order()
	tp.m_orderType = 'LMT'
	tp.m_totalQuantity = quantity
	tp.m_action = "SELL" if action == "BUY" else "BUY"
	tp.m_lmtPrice = round(last_price * (1 + TP / 100), 2)
	tp.order_id = order_id + 1
	tp.m_parentId = order_id
	tp.transmit = False

	sl = Order()
	sl.m_orderType = 'STP'
	sl.m_totalQuantity = quantity
	sl.m_action = "SELL" if action == "BUY" else "BUY"
	sl.m_auxPrice = round(last_price * (1 - SL / 100), 2)
	sl.order_id = order_id + 2
	sl.m_parentId = order_id
	sl.transmit = True

	return [parent_order, tp, sl]

def quantity_calculate(stock_ticker):
	last_price = None
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			last_price = float(row[2])
	quantity = POSITION_QUANTITY / last_price
	return int(quantity)

def main(conn, company, action, order_id):
	set_of_companies_in_position = positions_and_orderId_checking.main(conn)[0]
	if company not in set_of_companies_in_position:
		quantity = quantity_calculate(company)
		contract = utils.create_contract_from_ticker(company)
		bracket_order = create_MKT_order(company, quantity, action, order_id)
		for order in bracket_order:
			conn.placeOrder(order.order_id, contract, order)
		time.sleep(3)

if __name__ == "__main__":
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	order_id = int(positions_and_orderId_checking.main(c)[1])
	for com in {'AAPL', 'TQQQ'}:
		main(c, com, 'BUY', order_id)
		order_id += 3
	c.disconnect()

