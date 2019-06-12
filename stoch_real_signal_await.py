import csv
import time

from ib.opt import Connection, message

from settings import DURATION, BAR_SIZE
import stochastic
import utils

new_price_data = []
def new_price_data_list(msg):
	if 'finished' not in msg.date:
		new_price_data.append(f'{msg.date};{float(msg.open)};{float(msg.close)};{float(msg.high)};{float(msg.low)};{int(msg.volume)};')

def data_adding(new_price_data, stock_ticker):
	last_date = None
	i = -1
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		last_date = list(csv.reader(data_file, delimiter=';'))[-1][0]	# last date in collected data
	for row in new_price_data:
		if last_date in row:
			i = new_price_data.index(row)	# new prices cince this index in new_price_data
	with open(f'historical_data/{stock_ticker}.csv', 'a', encoding='utf-8') as data_file:
		fieldnames = ('date', 'open', 'close', 'high', 'low', 'volume')
		delimiter=';'
		a = csv.writer(data_file, fieldnames, delimiter=delimiter)
		for row in new_price_data[i+1:-1]:
			a.writerow(row.split(';'))

def error_handler(msg):
	if msg.errorCode == 2104 or msg.errorCode == 2106:
		pass
	elif msg.errorCode == 2103 or msg.errorCode == 504:
		print('CONNECTION ERROR!')
		print(msg)
		exit()
	else:
		print(msg)

def requesting(conn, stock_ticker):
	my_contract = utils.create_contract_from_ticker(stock_ticker)
#	conn.registerAll(print)	# this is for errors searching
	conn.register(new_price_data_list, message.historicalData)
	conn.register(error_handler, message.Error)
	conn.reqHistoricalData(1,	# tickerId, A unique identifier which will serve to identify the incoming data.
							my_contract,	# your Contract()
							'',	# endDateTime, The request's end date and time (the empty string indicates current present moment)
							'1 D',	# durationString, S D W M Y (seconds, days, weeks, months, year)
							BAR_SIZE,	# barSizeSetting, 1,5,10,15,30secs, 1,2,3,5,10,15,20,30min[s], 1,2,3,4,8hour[s], 1day,week,month
							"TRADES",	# whatToShow
							1,	# useRTH, Whether (1) or not (0) to retrieve data generated only within Regular Trading Hours (RTH)
							1	# formatDate, The format in which the incoming bars' date should be presented. Note that for day bars, only yyyyMMdd format is available.
						#	, False	# keepUpToDate, Whether a subscription is made to return updates of unfinished real time bars as they are available (True), 
									# or all data is returned on a one-time basis (False). Available starting with API v973.03+ and TWS v965+. 
									# If True, and endDateTime cannot be specified.
									# 10th argument is from ibapi, it doesn't work with IbPy
							)
	time.sleep(1.5)

def stoch_real_signal_to_buy(set_of_companies):
	companies_to_buy_now = set()
	for company in set_of_companies:
		if stochastic.main(company)[0] - stochastic.main(company)[1] >= 2:	# %K > %D
			companies_to_buy_now.add(company)
	return companies_to_buy_now

def stoch_real_signal_to_sell(set_of_companies):
	companies_to_buy_now = set()
	for company in set_of_companies:
		if stochastic.main(company)[1] - stochastic.main(company)[0] >= 2:	# %K < %D
			companies_to_buy_now.add(company)
	return companies_to_buy_now

def main(conn):
# Make a set of companies (from pre-signal)
	watchlist_to_buy = set()
	watchlist_to_sell = set()
	with open(f'Stoch_watchlist_to_buy.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				watchlist_to_buy = set(y.split(';'))
				watchlist_to_buy -= {''}
	with open(f'Stoch_watchlist_to_sell.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				watchlist_to_sell = set(y.split(';'))
				watchlist_to_sell -= {''}

# Data updating
	watchlists = watchlist_to_buy | watchlist_to_sell
	count = 1
	for company in watchlists:
		percentage = int((count/len(watchlists))*30)
		if count < len(watchlists):
			print(' ['+'█'*percentage+' '*(30 - percentage)+']', f'{count}/{len(watchlists)} Searching trade signals for {company}', ' '*5, end='\r')
			count += 1
		else:
			print(' ['+'█'*percentage+' '*(30 - percentage)+']', f'{count}/{len(watchlists)} Complete. {company}', ' '*20)
		requesting(conn, company)
		global new_price_data
		data_adding(new_price_data, company)
	new_price_data = []

# Search real signals
	print('Companies with real signal to BUY:', stoch_real_signal_to_buy(watchlist_to_buy))
	print('Companies with real signal to SELL:', stoch_real_signal_to_sell(watchlist_to_sell))
	return (watchlist_to_buy, watchlist_to_sell)

# In case of testing:
if __name__ == '__main__':
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	main(c)
	c.disconnect()

