import csv
#import time
from datetime import datetime

import settings
import strategy
import utils

#from ib.opt import message, Connection
#import orders_checking

def get_data(stock_ticker):
	list_with_price_data=[]
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)
	return list_with_price_data

def print_result(backtest_results):
	for x in backtest_results[1]:	# print history
		print(x)
	print(f'\nProfitability for period: {backtest_results[0]}%\n')

def backtest(list_with_price_data):
	open_order_price = None
	close_order_price = None
	profit = 0
	want_to_open_position = True
	capital = settings.POSITION_QUANTITY # посчитать через него!!!!!!!!!!!!!!!!!!!!!
	quantity = None
	min_capital = 1
	history = []

	for i in range(1, len(list_with_price_data)):
		row = list_with_price_data[i]
		date = row[0]
		open_price = float(row[1])
		high_price = float(row[2])
		low_price = float(row[3])
		close_price = float(row[4])
		K = float(row[6])
		D = float(row[7])

		if want_to_open_position: # no open positions
			if strategy.signal_to_open_position(row)[0] == 'buy':	# signal to buy
				if strategy.signal_to_open_position(row)[1] == 'MKT':
					open_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					want_to_open_position = False
					quantity = int(round(capital / open_order_price))
					history.append(f'{date}: bought {quantity} at ${open_order_price}')
		else:
			if strategy.signal_to_close_position(row)[0] == 'close':
				if strategy.signal_to_close_position(row)[1] == 'MKT':
					close_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
					capital += profit
					history.append(f'{date}: close at ${close_order_price}, profit: ${round(close_order_price - open_order_price)}')				
					want_to_open_position = True
				if strategy.signal_to_close_position(row)[1] == 'SL-TP':
					sl = open_order_price - ((strategy.signal_to_close_position(row)[2] / 100) * open_order_price)
					tp = (strategy.signal_to_close_position(row)[2] / 100 + 1) * open_order_price
					if low_price <= sl:
						close_order_price = round(sl, 2)
						profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append(f'{date}: close at ${close_order_price}, profit: -${abs(round(close_order_price - open_order_price))}')				
						want_to_open_position = True
					if high_price >= tp:
						close_order_price = round(tp, 2)
						profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append(f'{date}: close at ${close_order_price}, profit: ${round(close_order_price - open_order_price)}')				
						want_to_open_position = True
		if i == len(list_with_price_data) - 1 and want_to_open_position == False:
			profit = (close_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
			capital += profit
			history.append(f'{date}: Last price: ${close_price}, potencial profit: {round(profit)}')
	
	profitability = round((capital - settings.POSITION_QUANTITY) / settings.POSITION_QUANTITY * 100, 1)
	
	return (profitability, history)

def main(company='EA'):
	сompanies = utils.set_with_my_companies()
	for company in ('A'):	# сompanies:	# 
		print('\n', company, ':','\n')
		list_with_price_data = get_data(company)
		try:
			print_result(backtest(list_with_price_data))
		except(IndexError):
			print('no data yet')

main()
 # пересчитать прибыль от количества которое в настройках
