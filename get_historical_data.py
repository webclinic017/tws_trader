# ПРОБЛЕМА: перестает записывать файлы после 5-20 успешных попыток, хотя по списку продолжает проверять
# не получив ответ от TWS однажды, перестает получать ответы на другие запросы. Помогает перезагрузка TWS
# но иногда после безответного запроса может давать ответы на другие запросы

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
		if msg.close > 1:	# ПРОБЛЕМА: продолжает собирать данные, отвечающие условию. Надо: прекратить собирать данные по запросу вообще
			with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'a', encoding='utf-8') as csvfile:
				fieldnames = dict.keys()
				delimiter=';'
				writer = csv.DictWriter(csvfile, fieldnames, delimiter=delimiter)
				if 'finished' not in dict['Date']:
					writer.writerow(dict)

	contract = create_contract(stock_ticker, 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print)	# this is for errors searching
	conn.register(create_csv_from_data, message.historicalData)
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
	main('AAPL', '5 Y', '1 hour')

