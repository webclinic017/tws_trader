import time

from ib.ext.Order import Order
from ib.opt import Connection, message

import positions_and_orderId_checking
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

def main(conn, company, quantity, action, order_id):
	order_id = positions_and_orderId_checking.main(conn)[1]
	print('order_id = ', order_id)
	
	contract = utils.create_contract_from_ticker(company)
	order = create_MKT_order(quantity, action)
	conn.placeOrder(order_id, contract, order)

# if __name__ == "__main__":
# 	c = Connection.create(port=7497, clientId=0)
# 	c.connect()
# 	main(c, 'Z', 1, 'BUY')
# 	c.disconnect()

