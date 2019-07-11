import csv
from datetime import datetime
import time

from ib.opt import Connection, message

from settings import TWS_CONNECTION, company
import update_stochastic_in_price_data
import utils


new_price_data = []
def new_price_data_list(msg):
	if 'finished' not in msg.date:
		new_price_data.append(f'{msg.date};{float(msg.open)};{float(msg.high)};{float(msg.low)};{float(msg.close)};{int(msg.volume)}')


def data_adding(new_price_data, stock_ticker, bar_size):
	last_date = None
	with open(f'historical_data/{stock_ticker} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		last_date = list(csv.reader(data_file, delimiter=';'))[-1][0]	# last date in collected data
	
	# for x in new_price_data:
	# 	print(x)
	i = -1	# index of the last row in file with data
	for row in new_price_data:
		if last_date in row:
			i = new_price_data.index(row)	# new prices since next from this index in new_price_data
			# print(i)
	if i != -1 and new_price_data != []:
		with open(f'historical_data/{stock_ticker} {bar_size}.csv', 'a', encoding='utf-8') as data_file:
			fieldnames = ('date', 'open', 'high', 'low', 'close', 'volume')
			a = csv.writer(data_file, fieldnames, delimiter=';')
			for row in new_price_data[i+1:]:
				a.writerow(row.split(';'))


def error_handler(msg):
	if msg.errorCode == 2104 or msg.errorCode == 2106:
		pass
	elif msg.errorCode == 2103 or msg.errorCode == 504:
		print(msg)
		print('CONNECTION ERROR!')
		exit()
	else:
		print(msg)


def duration_calculate(company, bar_size):
	last_date = None
	with open(f'historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		last_date = list(csv.reader(data_file, delimiter=';'))[-1][0]	# last date in collected data
	last_date = datetime.strptime(last_date, "%Y%m%d  %H:%M:%S")
	now = datetime.now()
	difference = now - last_date
	duration = f"{difference.days + 2} D" # difference + today + last_date (IB counts date, datetime count 24-hours)
	return duration


def requesting(company, duration, bar_size):
	my_contract = utils.create_contract_from_ticker(company)
	TWS_CONNECTION.connect()
	# TWS_CONNECTION.registerAll(print)	# this is for errors searching
	TWS_CONNECTION.register(new_price_data_list, message.historicalData)
	TWS_CONNECTION.register(error_handler, message.Error)
	TWS_CONNECTION.reqHistoricalData(1,	# tickerId, A unique identifier which will serve to identify the incoming data.
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
	time.sleep(5)
	TWS_CONNECTION.disconnect()


def main(company, stoch_parameters, bar_size):
	duration = duration_calculate(company, bar_size)
	requesting(company, duration, bar_size)
	global new_price_data
	data_adding(new_price_data, company, bar_size)
	update_stochastic_in_price_data.main(company, stoch_parameters, bar_size)	# updates whole data! Needs to modify to work faster.
	new_price_data = []


# # In case of testing:
if __name__ == "__main__":
	try:
		# company = settings.company
		bar_size = '30 mins'
		main(company, (26,26,9), bar_size)
	except():
		print('FATAL ERROR!')

