import time

from ib.ext.Order import Order
from ib.opt import Connection, message

import utils

order_id = []
def get_order_id(msg):
	global order_id
	print('Order ID from msg:', msg.orderId)
	order_id.append(msg.orderId)

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

def main(conn, company, quantity, action):
#	conn.registerAll(print)

	global order_id
	conn.register(get_order_id, message.nextValidId)
	conn.reqPositions()
	time.sleep(2)
	print('order_id = ', order_id)

##### ERROR: order_id = [] WHY???!!
	orderid = order_id[0]	# ERROR: order_id = [] WHY???!! only if __name__ != '__main__'

	contract = utils.create_contract_from_ticker(company)
	order = create_MKT_order(quantity, action)
	conn.placeOrder(orderid, contract, order)
	order_id = []

if __name__ == "__main__":
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	main(c, 'AAPL', 1, 'BUY')
	c.disconnect()

