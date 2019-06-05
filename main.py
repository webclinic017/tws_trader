'''from datetime import datetime
import logging
import threading
import time

import ibapi.wrapper
import ibapi.client
import ibapi.contract
import ibapi.connection

def make_contract(symbol, sec_type='STK', currency='USD', exchange='ISLAND'):
	my_contract = ibapi.contract.Contract()
	symbol = my_contract.symbol
	sec_type = my_contract.secType
	currency = my_contract.currency
	exchange = my_contract.exchange
	return my_contract

def make_LMT_order(action, quantity, price):
	my_order = ibapi.order.Order()
	my_order.orderType = "LMT"
	my_order.totalQuantity = quantity
	my_order.action = action
	my_order.lmtPrice = price
	return my_order

def main():
	logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
						level=logging.INFO,
						filename='test.log'
						)

	wrp=ibapi.wrapper.EWrapper()
	cln=ibapi.client.EClient(wrp)
	cln.connect("127.0.0.1", 7497, 1)

	conn = ibapi.connection.Connection.connect("127.0.0.1", 7497)
	conn.connect()


	cont = make_contract('TSLA')
	offer = make_LMT_order('BUY', 1, 300)
	conn.placeOrder(1, cont, offer)

	








	










	time.sleep(120)

	cln.disconnect()

if __name__=='__main__':
	main()
'''
'''
import logging
import datetime
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
from threading import Timer

class TestApp(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self,self)

	def nextValidId(self, orderId):
		self.nextOrderId = orderId
		self.start()

	def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, clientId, whyHeld, mktCapPrice):
		print('Такой ордер')	

	def openOrder(self, orderId, contract, order, orderState):
		print("открыт")

	def start(self):
		contract = Contract()
		contract.symbol = "TSLA"
		contract.secType = "STK"
		contract.currency = "USD"
		contract.exchange = "ISLAND"

		order = Order()
		order.acrion = "BUY"
		order.orderType = "LMT"
		order.totalQuantity = 1
		order.lmtPrice = 300

		self.placeOrder(self.nextOrderId, contract, order)

	def stop(self):
		self.done = True
		self.disconnect()

def main():
	logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
						level=logging.INFO,
						filename='test.log'
						)

	app = TestApp()
	app.nextOrderId = 0
	app.connect("127.0.0.1", 7497, 1)

	Timer(60, app.stop).start()
	app.run()


if __name__ == '__main__':
	main()
'''
'''
import logging

from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
						level=logging.INFO,
						filename='test.log'
						)

from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

contract = Forex('EURUSD')
bars = ib.reqHistoricalData(contract, endDateTime='', durationStr='30 D',
		barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

# convert to pandas dataframe:
df = util.df(bars)
print(df[['date', 'open', 'high', 'low', 'close']])
'''
import logging

from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order

def make_contract(symbol, sec_type, exch, prim_exch, curr):
	Contract.m_symbol = symbol
	Contract.m_secType = sec_type
	Contract.m_exchange = exch
	Contract.m_primaryExch = prim_exch
	Contract.m_currency = curr
	return Contract

def make_order(action, quantity, price = None):
	if price is not None:
		order = Order()
		order.m_orderType = 'LMT'
		order.m_totalQuantity = quantity
		order.m_action = action
		order.m_lmtPrice = price
	else:
		order = Order()
		order.m_orderType = 'MKT'
		order.m_totalQuantity = quantity
		order.m_action = action
	return order

def main():
	logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
						level=logging.INFO,
						filename='test.log'
						)
	conn = Connection.create(port=7497, clientId=1)
	conn.connect()
	oid = 3423583240
	cont = make_contract('TSLA', 'STK', 'SMART', 'SMART', 'USD')
	offer = make_order('BUY', 1, 300)
	conn.placeOrder(oid, cont, offer)
	conn.disconnect()

if __name__ == '__main__':
	main()















































