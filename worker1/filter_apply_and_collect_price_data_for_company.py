# КАК остановить функцию при получении этой ошибки?
# Как остановить функцию, если файл не создан?

import csv
import time

from ib.opt import Connection, message
from pymongo import MongoClient

from .all_companies import set_of_all_companies
from settings import MONGO_LINK
from settings import BAR_SIZE
from settings import PRICE_FILTER, AVERAGE_VOLUME_FILTER
import utils

price_data = []
def create_price_data_list(msg):
	if 'finished' not in msg.date:
		price_data.append(f'{msg.date};{float(msg.open)};{float(msg.high)};{float(msg.low)};{float(msg.close)};{int(msg.volume)};')

def filter_apply(price_data):
	if price_data != []:
		sum_volume = 0
		for i in range(0, len(price_data)):
			sum_volume += int(price_data[i].split(';')[5])
		average_volume = int(sum_volume / len(price_data))
		last_close = float(price_data[-1].split(';')[2])
		if average_volume >= AVERAGE_VOLUME_FILTER and last_close >= PRICE_FILTER:
			return True
		else:
			return False

def create_csv_from_list(price_data, stock_ticker):
	with open(f'./historical_data/{stock_ticker}.csv', 'w', encoding='utf-8') as csvfile:
		fieldnames = ('date', 'open', 'high', 'low', 'close', 'volume')
		delimiter=';'
		a = csv.writer(csvfile, fieldnames, delimiter=delimiter)
		for row in price_data:
			a.writerow(row.split(';'))
		with open(f'./!MyCompanies.csv', 'a', encoding='utf-8') as file:
			file.write(stock_ticker+';')
	price_data = []

def adding_in_db(stock_ticker, price_data):
	client = MongoClient(MONGO_LINK)
	db = client.test
	db.collection.insert({stock_ticker: price_data})
#	print(f"Added in mongo db prices for {stock_ticker}")

error_list = []
def error_handler(msg):
	if msg.errorCode == 2104 or msg.errorCode == 2106:
		pass
	elif msg.errorCode == 2103 or msg.errorCode == 504:
		print(msg)
		print('CONNECTION ERROR!')
		exit()
	else:
		error_text = str(msg.errorCode) + ';' + msg.errorMsg
		error_list.append(error_text)
		print(msg)

def write_errors(error_list, stock_ticker):
	with open(f'worker1/Errors.csv', 'a', encoding='utf-8') as csvfile:
		a = csv.writer(csvfile, delimiter=';')
		time_now = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
		row = (time_now, stock_ticker, error_list[0])
		a.writerow(row)

def requesting(conn, stock_ticker, duration):
	my_contract = utils.create_contract_from_ticker(stock_ticker)
#	conn.registerAll(print)	# this is for errors searching
	conn.register(create_price_data_list, message.historicalData)
	conn.register(error_handler, message.Error)
	conn.reqHistoricalData(1,	# tickerId, A unique identifier which will serve to identify the incoming data.
							my_contract,	# your Contract()
							'',	# endDateTime, The request's end date and time (the empty string indicates current present moment)
							duration,	# durationString, S D W M Y (seconds, days, weeks, months, year)
							BAR_SIZE,	# barSizeSetting, 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
							"TRADES",	# whatToShow
							1,	# useRTH, Whether (1) or not (0) to retrieve data generated only within Regular Trading Hours (RTH)
							1	# formatDate, The format in which the incoming bars' date should be presented. Note that for day bars, only yyyyMMdd format is available.
						#	, False	# keepUpToDate, Whether a subscription is made to return updates of unfinished real time bars as they are available (True), 
									# or all data is returned on a one-time basis (False). Available starting with API v973.03+ and TWS v965+. 
									# If True, and endDateTime cannot be specified.
									# 10th argument is from ibapi, it doesn't work with IbPy
							)
	time.sleep(2.5)

	global error_list
	if error_list != []:
		write_errors(error_list, stock_ticker)
		error_list = []

def check_data_existing(stock_ticker):
	with open(f'./!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = y.split(';')
	if stock_ticker in companies_with_data:
		return False	# we do not have any data for this company yet
	else:
		return True	# we already have data for this company

def main(conn, stock_ticker, duration):
	global price_data
	if check_data_existing(stock_ticker):
		requesting(conn, stock_ticker, duration)
		if filter_apply(price_data):
			create_csv_from_list(price_data, stock_ticker)
		else:
			write_errors(['filtered'], stock_ticker)
	else:
		write_errors(['We already have price data'], stock_ticker)
	price_data = []

# In case of testing:
if __name__ == '__main__':
	company = 'AAPL'
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	main(c, company)
	c.disconnect()
