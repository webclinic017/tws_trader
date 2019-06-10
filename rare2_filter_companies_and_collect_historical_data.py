# КАК остановить функцию при получении этой ошибки?
# Как остановить функцию, если файл не создан?

import csv
import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import Connection, dispatcher, message
from pymongo import MongoClient

from rare1_all_companies import set_of_all_companies
from settings import MONGO_LINK
from settings import DURATION, BAR_SIZE
from settings import PRICE_FILTER, AVERAGE_VOLUME_FILTER

price_data = []

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
		price_data.append(f'{msg.date};{float(msg.open)};{float(msg.close)};{float(msg.high)};{float(msg.low)};{int(msg.volume)};')

def filter_companies(price_data):
	if price_data != []:
		sum_volume = 0
		for i in range(0, len(price_data)):
			sum_volume += int(price_data[i].split(';')[5])
		average_volume = int(sum_volume / len(price_data))
		last_close = float(price_data[-1].split(';')[2])
		if average_volume >= AVERAGE_VOLUME_FILTER and last_close >= PRICE_FILTER:
			return True
		else:
			print('This security is a \'penny stock\' or illiquid')
			return False

def create_csv_from_list(price_data, stock_ticker):
	with open(f'historical_data/{stock_ticker}.csv', 'w', encoding='utf-8') as csvfile:
		fieldnames = ('date', 'open', 'close', 'high', 'low', 'volume')
		delimiter=';'
		a = csv.writer(csvfile, fieldnames, delimiter=delimiter)
		for row in price_data:
			a.writerow(row.split(';'))
		with open(f'!MyCompanies.csv', 'a', encoding='utf-8') as file:
			file.write(stock_ticker+';')
	price_data = []

def adding_in_db(stock_ticker, price_data):
	client = MongoClient(MONGO_LINK)
	db = client.test
	db.collection.insert({stock_ticker: price_data})
	print(f"Added in mongo db prices for {stock_ticker}")

def error_handler(msg):
	if msg.errorCode == 326:
		print(f"ERROR {msg.errorCode}: No data permissions for this item")
	elif msg.errorCode == 2104 or msg.errorCode == 2106:
		pass
	elif msg.errorCode == 2103 or msg.errorCode == 504:
		print('CONNECTION ERROR!')
		print(msg)
		exit()
	else:
		print(msg)

# <error id=-1, errorCode=2105, errorMsg=HMDS data farm connection is broken:ushmds> - Crucial! IB server may be reseting at this moment

# <error id=1, errorCode=322, errorMsg=Error processing request:-'bI' : cause - Duplicate ticker ID for API historical data query>
# RFI, SAFT, MFV, JSD, JSM, BIOC, TSM, GGT, EGP, GECC, FUSB, 

# # ОШИБКА: 
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.hfarm>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.hfarm>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfarm.nj>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfarm.nj>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.jfarm>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfuture>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.jfarm>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.usfuture>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.cashfarm>
# <error id=-1, errorCode=2108, errorMsg=Market data farm connection is inactive but should be available upon demand.cashfarm>

# <error id=1, errorCode=200, errorMsg=No security definition has been found for the request>
# <error id=1, errorCode=200, errorMsg=The contract description specified for <stock_ticker> is ambiguous.>
# FTEK, AMBCW, SCOR, 

# <error id=None, errorCode=None, errorMsg=[Errno 54] Connection reset by peer>
# <error id=-1, errorCode=2103, errorMsg=Market data farm connection is broken:cashfarm>
# <error id=1, errorCode=162, errorMsg=Historical Market Data Service error message:No historical market data for 1527/STK@NYSENBBO Last 1d> TDW

def requesting(conn, stock_ticker):
	my_contract = create_contract(stock_ticker, 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print)	# this is for errors searching
	conn.register(create_price_data_list, message.historicalData)
	conn.register(error_handler, message.Error)
#	conn.connect()
	conn.reqHistoricalData(1,	# tickerId, A unique identifier which will serve to identify the incoming data.
							my_contract,	# your Contract()
							'',	# endDateTime, The request's end date and time (the empty string indicates current present moment)
							DURATION,	# durationString, S D W M Y (seconds, days, weeks, months, year)
							BAR_SIZE,	# barSizeSetting, 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
							"TRADES",	# whatToShow
							1,	# useRTH, Whether (1) or not (0) to retrieve data generated only within Regular Trading Hours (RTH)
							1	# formatDate, The format in which the incoming bars' date should be presented. Note that for day bars, only yyyyMMdd format is available.
						#	, False	# keepUpToDate, Whether a subscription is made to return updates of unfinished real time bars as they are available (True), 
									# or all data is returned on a one-time basis (False). Available starting with API v973.03+ and TWS v965+. 
									# If True, and endDateTime cannot be specified.
									# 10th argument is from ibapi, it doesn't work with IbPy
							)
	time.sleep(3)
#	conn.disconnect()

def check_data_existing(stock_ticker):
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = y.split(';')
	if stock_ticker in companies_with_data:
		return False	# we do not have any data for this company yet
	else:
		return True	# we already have data for this company

def main(conn, stock_ticker):
	print(f"Requesting data for {stock_ticker}")
	global price_data
	if check_data_existing(stock_ticker):
		requesting(conn, stock_ticker)
		if filter_companies(price_data):
			create_csv_from_list(price_data, stock_ticker)
			print(f"Created csv file with price data for {stock_ticker}")
	#	adding_in_db(stock_ticker, price_data)
	else:
		print(f'We already have price data for {stock_ticker}')
	price_data = []

# In case of testing:
if __name__ == '__main__':
#	for company in set_of_all_companies():
	company = 'AAPL'
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	main(c, company)
	c.disconnect()
