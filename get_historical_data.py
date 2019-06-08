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
# ЕЩЕ ОДНА ОШИБКА ПРИЧИНА ОСТАНОВКИ: <error id=1, errorCode=200, errorMsg=No security definition has been found for the request>

# КАК остановить функцию при получении этой ошибки?
# ИЛИ как избежать остановки при получении этой ошибки?

# ИНОГДА СОЗДАЮТСЯ ПУСТЫЕ ФАЙЛЫ, хотя данные есть


# Как остановить функцию, если файл не создан?

import csv
import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, dispatcher, message

from all_companies import set_of_all_companies

price_data = ['date;open;close;high;low;volume']

def create_contract(symbol, sec_type, exch, prim_exch, curr):
	contract = Contract()
	contract.m_symbol = symbol
	contract.m_secType = sec_type
	contract.m_exchange = exch
	contract.m_primaryExch = prim_exch
	contract.m_currency = curr
	return contract

def create_price_data_list(msg):
	if 'finished' not in msg.date:
		price_data.append(f'{msg.date};{float(msg.open)};{float(msg.close)};{float(msg.high)};{float(msg.low)};{float(msg.volume)};')

def create_csv_from_dict(price_data, stock_ticker, duration, bar_size):
	with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'w', encoding='utf-8') as csvfile:
		fieldnames = ('date', 'open', 'close', 'high', 'low', 'volume')
		delimiter=';'
		a = csv.writer(csvfile, fieldnames, delimiter=delimiter)
		for row in price_data:
			a.writerow(row.split(';'))
	print(f"Для {stock_ticker} успешно собраны данные")

def error_handler(msg):
	if msg.errorCode == 326:
		print(f"ERROR {msg.errorCode}: No data permissions for {stock_ticker}")
	elif msg.errorCode == 2104 or msg.errorCode == 2106:
		pass
	elif msg.errorMsg == '[Errno 54] Connection reset by peer':
		print('[Errno 54] Connection reset by peer')
		main(stock_ticker, duration, bar_size) # почему не работает?
	else:
		print(msg)

def requesting(conn, stock_ticker, duration, bar_size):
	my_contract = create_contract(stock_ticker, 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print)	# this is for errors searching
	conn.register(create_price_data_list, message.historicalData)
	conn.register(error_handler, message.Error)
	conn.reqHistoricalData(1,	# tickerId, A unique identifier which will serve to identify the incoming data.
							my_contract,	# your Contract()
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
	time.sleep(3)

def main(conn, stock_ticker, duration, bar_size):
	print(f"Requesting data for {stock_ticker}")
	requesting(conn, stock_ticker, duration, bar_size)
	create_csv_from_dict(price_data, stock_ticker, duration, bar_size)

# In case of testing:
if __name__ == '__main__':
#	for company in set_of_all_companies():
	company = 'TSLA'
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	main(c, company, '1 W', '1 day')
	c.disconnect()

