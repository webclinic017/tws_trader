import csv
import time

from ib.opt import message, Connection

open_orders = set()
def get_open_orders_info(msg):
	open_orders.add(msg.contract.m_symbol)

def create_csv_with_open_orders(open_orders):
	open_orders = list(open_orders)
	with open('!MyOrders.csv', 'w', encoding='utf-8') as csvfile:
		a = csv.writer(csvfile, delimiter=';')
		a.writerow(open_orders)

def main(c):
	global open_orders
	c.register(get_open_orders_info, message.openOrder)
	c.reqAllOpenOrders()
	time.sleep(2)
	create_csv_with_open_orders(open_orders)
	open_orders = set(open_orders)
	return open_orders

# In case of testing:
if __name__ == '__main__':
	c = Connection.create(port=7497, clientId=0)
	c.connect()
#	c.registerAll(print)
	main(c)
	c.disconnect()

