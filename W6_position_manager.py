from datetime import datetime
import csv
import time

from ib.ext.Order import Order
from ib.opt import Connection, message

import utils
from settings import TWS_CONNECTION
import W4_checking_account


def create_MKT_order(action, quantity, order_id):
	parent_order = Order()
	parent_order.m_orderType = 'MKT'
	parent_order.m_totalQuantity = quantity
	parent_order.m_action = action
	parent_order.order_id = order_id
	return parent_order


def create_TP_order(action, take_profit, quantity, parent_order_id):
	tp = Order()
	tp.m_orderType = 'LMT'
	tp.m_totalQuantity = quantity
	tp.m_action = "SELL" if action == "BUY" else "BUY"
	tp.m_lmtPrice = take_profit
	tp.order_id = parent_order_id + 1
	tp.m_tif = 'GTC'
	return tp


def create_SL_order(action, stop_loss, quantity, parent_order_id):
	sl = Order()
	sl.m_orderType = 'STP'
	sl.m_totalQuantity = quantity
	sl.m_action = "SELL" if action == "BUY" else "BUY"
	sl.m_auxPrice = stop_loss
	sl.order_id = parent_order_id + 2
	sl.m_tif = 'GTC'
	return sl


def create_bracket_order(action, stop_loss, take_profit, quantity, order_id):
	parent_order = create_MKT_order(action, quantity, order_id)
	tp = create_TP_order(action, take_profit, quantity, order_id)
	sl = create_SL_order(action, stop_loss, quantity, order_id)
	parent_order.m_orderType = 'MKT'
	parent_order.transmit = False
	tp.m_parentId = order_id
	sl.m_parentId = order_id
	tp.transmit = False
	sl.transmit = True
	return [parent_order, tp, sl]

# Takes 15 - 49 secs
def place_bracket_order(company, action, stop_loss, take_profit, quantity, order_id, try_count=1):
	contract = utils.create_contract_from_ticker(company)
	bracket_order = create_bracket_order(action, stop_loss, take_profit, quantity, order_id)
	for order in bracket_order:
		TWS_CONNECTION.connect()
		TWS_CONNECTION.placeOrder(order.order_id, contract, order)
		time.sleep(5)
		TWS_CONNECTION.disconnect()
# Check opened position
	position = W4_checking_account.what_position_is_open_now_for(company)
	time.sleep(7)
	weekday = datetime.strftime(datetime.now(), '%w')
	if position == None and weekday not in ('6', '0'):
		if try_count <= 3:
			try_count += 1
			place_bracket_order(company, action, stop_loss, take_profit, quantity, order_id, try_count)
		else:
			print('ERROR with braket order placing or execution!')
# Check opened orders
	W4_checking_account.orders_ids_are_open_now_for(company)
	time.sleep(3)
	placed_orders = []
	with open('!MyOrders.csv', 'r', encoding='utf-8') as csvfile:
		fieldnames = ('OrderId', 'Company', 'Quantity', 'OrderType')
		a = csv.DictReader(csvfile, fieldnames, delimiter=';')
		for row in a:
			if row.get('Company') == company:
				if row.get('OrderType') == 'LMT':
					placed_orders.append('TP')
				if row.get('OrderType') == 'STP':
					placed_orders.append('SL')
	if 'LMT' not in placed_orders:
		tp = create_TP_order(action, take_profit, quantity, order_id)
		tp.transmit = True
		TWS_CONNECTION.connect()
		TWS_CONNECTION.placeOrder(tp.order_id+2, contract, tp)
		time.sleep(3)
		TWS_CONNECTION.disconnect()
	time.sleep(2)
	if 'STP' not in placed_orders:
		sl = create_SL_order(action, stop_loss, quantity, order_id)
		sl.transmit = True
		TWS_CONNECTION.connect()
		TWS_CONNECTION.placeOrder(sl.order_id+2, contract, sl)
		time.sleep(3)
		TWS_CONNECTION.disconnect()		
	time.sleep(2)	


def close_all_open_orders_for(company):
# it takes >16 secs
	open_orders_ids = W4_checking_account.orders_ids_are_open_now_for(company)
	time.sleep(4)
	print('Open orders befor closing are:', open_orders_ids)
	if open_orders_ids != ():
		TWS_CONNECTION.connect()
		for order_id in open_orders_ids:
			TWS_CONNECTION.cancelOrder(order_id)
			time.sleep(1)
		time.sleep(1)
		TWS_CONNECTION.disconnect()
		open_orders_ids = W4_checking_account.orders_ids_are_open_now_for(company)
		time.sleep(4)
		print('Open orders after closing are:', open_orders_ids)
		if open_orders_ids != ():
			close_all_open_orders_for(company)

#### NEEDS TO AWAIT TILL POSITION FULLY CLOSES!!! ####
# it takes >22 secs
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
	time.sleep(2)
# Close all open orders for the company
	close_all_open_orders_for(company)


if __name__ == "__main__":
	company = 'TSLA'
	order_id = 105
	# place_bracket_order(company, 'BUY', order_id)
	close_position(company, order_id)

