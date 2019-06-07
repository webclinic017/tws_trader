# ПРОБЛЕМА: перестает записывать файлы после 5-20 успешных попыток, хотя по списку продолжает проверять
# не получив ответ от TWS однажды, перестает получать ответы на другие запросы. Помогает перезагрузка TWS
# но иногда после безответного запроса может давать ответы на другие запросы - если возникает сразу после ошибки 326
# ОШИБКА, возникающая когда все встает: [Errno 54] Connection reset by peer

'''
# ОШИБКА ПРИЧИНА ОСТАНОВКИ: 
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.hfarm>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.hfarm>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfarm.nj>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfarm.nj>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.jfarm>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfuture>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.jfarm>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfuture>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.cashfarm>
<error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.cashfarm>
'''

# КАК остановить функцию при получении этой ошибки?
# ИЛИ как избежать остановки при получении этой ошибки?

import csv
import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, dispatcher, message

def main(stock_ticker, duration, bar_size):
	conn = Connection.create(port=7497, clientId=0)
	print(f"Requesting data for {stock_ticker}")

	def create_contract(symbol, sec_type, exch, prim_exch, curr):
		contract = Contract()
		contract.m_symbol = symbol
		contract.m_secType = sec_type
		contract.m_exchange = exch
		contract.m_primaryExch = prim_exch
		contract.m_currency = curr
		return contract

	def create_csv_from_data(msg):
		dict={}
		dict['Date']=msg.date
		dict['Open']=msg.open
		dict['Close']=msg.close
		dict['High']=msg.high
		dict['Low']=msg.low
		dict['Volume']=msg.volume
		with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'w', encoding='utf-8') as csvfile:
			fieldnames = dict.keys()
			delimiter=';'
			writer = csv.DictWriter(csvfile, fieldnames, delimiter=delimiter)
			if 'finished' not in dict['Date']:
				writer.writerow(dict)

	def error_handler(msg):
		if msg.errorCode == 326:
			print(f"ERROR {msg.errorCode}: No data permissions for {stock_ticker}")
		elif msg.errorCode == 2104 or msg.errorCode == 2106:
			pass
		else:
			print(msg)

	contract = create_contract(stock_ticker, 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print)	# this is for errors searching
	conn.register(create_csv_from_data, message.historicalData)
	conn.register(error_handler, message.Error)
	conn.connect()
	conn.reqHistoricalData(1,	# tickerId, A unique identifier which will serve to identify the incoming data.
							contract,	# your Contract()
							'',	# endDateTime, The request's end date and time (the empty string indicates current present moment)
							duration,	# durationString, S D W M Y (seconds, days, weeks, months, year)
							bar_size,	# barSizeSetting, 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
							"TRADES",	# whatToShow
							1,	# useRTH, Whether (1) or not (0) to retrieve data generated only within Regular Trading Hours (RTH)
							1	# formatDate, The format in which the incoming bars' date should be presented. Note that for day bars, only yyyyMMdd format is available.
						#	, False	# keepUpToDate, Whether a subscription is made to return updates of unfinished real time bars as they are available (True), 
									# or all data is returned on a one-time basis (False). Available starting with API v973.03+ and TWS v965+. 
									# If True, and endDateTime cannot be specified.
									# 10th argument is from ibapi, it doesn't work with IbPy
							)
	time.sleep(4)
	conn.disconnect()

# In case of testing:
if __name__ == '__main__':
	main('GBTC', '1 Y', '1 hour')

