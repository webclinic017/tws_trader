import csv
import time

from ib.ext.Order import Order
from ib.opt import Connection, message

import utils
from settings import TWS_CONNECTION
import W4_checking_account


def place_bracket_order(company, action, stop_loss, take_profit, quantity, order_id):
	def create_bracket_order(action, stop_loss, take_profit, quantity, order_id):
		parent_order = Order()
		parent_order.m_orderType = 'MKT'
		parent_order.m_totalQuantity = quantity
		parent_order.m_action = action
		parent_order.order_id = order_id
		parent_order.transmit = False

		tp = Order()
		tp.m_orderType = 'LMT'
		tp.m_totalQuantity = quantity
		tp.m_action = "SELL" if action == "BUY" else "BUY"
		tp.m_lmtPrice = take_profit
		tp.order_id = order_id + 1
		tp.m_parentId = order_id
		tp.transmit = False

		sl = Order()
		sl.m_orderType = 'STP'
		sl.m_totalQuantity = quantity
		sl.m_action = "SELL" if action == "BUY" else "BUY"
		sl.m_auxPrice = stop_loss
		sl.order_id = order_id + 2
		sl.m_parentId = order_id
		sl.transmit = True

		return [parent_order, tp, sl]

	contract = utils.create_contract_from_ticker(company)
	bracket_order = create_bracket_order(action, stop_loss, take_profit, quantity, order_id)
	for order in bracket_order:
		TWS_CONNECTION.connect()
		TWS_CONNECTION.placeOrder(order.order_id, contract, order)
		time.sleep(3)
		TWS_CONNECTION.disconnect()
#### + ADD CHECKING SL-TP - IF TWS ANSWERED: <error id={order_id}, errorCode=201, errorMsg=Order rejected - reason:Parent order is partially or fully filled>
#### in this case I'll place single SL order and single TP order

def close_position(company, order_id):
# Getting position quantity
	open_positions = []
	with open('!MyPositions.csv', 'r', encoding='utf-8') as csvfile:
		fieldnames = ('Company', 'Quantity')
		a = csv.DictReader(csvfile, fieldnames, delimiter=';')
		for row in a:
			open_positions.append(row)
	quantity = None
	for position in open_positions:
		if position.get('Company') == company:
			quantity = int(position.get('Quantity'))
# Placing opposite order
	action = None
	if quantity > 0:
		action = 'SELL'
	if quantity < 0:
		action = 'BUY'
	order = Order()
	order.m_orderType = 'MKT'
	order.m_totalQuantity = abs(quantity)
	order.m_action = action
	order.order_id = order_id
	order.transmit = True
	contract = utils.create_contract_from_ticker(company)
	TWS_CONNECTION.connect()
	TWS_CONNECTION.placeOrder(order_id, contract, order)
	time.sleep(3)
	TWS_CONNECTION.disconnect()
# Close all open orders for the company
	open_orders_ids = W4_checking_account.orders_ids_are_open_now_for(company)
	time.sleep(2.5)
	if open_orders_ids != ():
		TWS_CONNECTION.connect()
		for order_id in open_orders_ids:
			TWS_CONNECTION.cancelOrder(order_id)
		TWS_CONNECTION.disconnect()
		

if __name__ == "__main__":
	company = 'TSLA'
	order_id = 105
	# place_bracket_order(company, 'BUY', order_id)
	close_position(company, order_id)

