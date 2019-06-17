import csv
#import time
from datetime import datetime

import utils
import strategy

#from ib.opt import message, Connection
#import orders_checking

def get_data(stock_ticker):
	list_with_price_data=[]
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)
	return list_with_price_data

def backtest(list_with_price_data, i1, i2):
	open_order_price = None
	close_order_price = None
	profit = 0
	want_to_open_position = True
	min_capital = 0
	
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
					print(f'{date}: bought with price ${open_order_price}')
					want_to_open_position = False
					if open_order_price > min_capital + profit:
						min_capital = open_order_price
		else:
			if strategy.signal_to_close_position(row)[0] == 'close':
				close_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
				profit += (close_order_price - open_order_price) - (0.0065 * 2)*10		# comission + *10 smth wrong
				print(f'{date}: close at {close_order_price}, profit: {round(close_order_price - open_order_price)}')				
				want_to_open_position = True

	if want_to_open_position == False:
		profit += (close_price - open_order_price) - (0.0065 * 2)*10		# comission + *10 smth wrong
		print(f'Last price: ${close_price}, profit: {round(profit)}')
	profitability = round(profit/min_capital*100, 1)
	return (min_capital, round(profit, 1), profitability)

def find_optimum_strategy(list_with_price_data):
	profit = 0

	float_list = []
	step = 0.5
	x=0.5
	while x <= 15:
		float_list.append(round(x, 1))
		x += step

	for i1 in (5,5.1,5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,6):#float_list:
		for i2 in float_list:
			profit = backtest(list_with_price_data, i1, i2)[1]
			min_capital = backtest(list_with_price_data, i1, i2)[0]
			if profit/min_capital*100 > 15:
				print(f'profit with TP {i1}%, SL {i2}%: ${round(profit, 2)}, ({round(profit/min_capital*100, 1)}%)')

def main(stock_ticker):
	list_with_price_data = get_data(stock_ticker)
	find_optimum_strategy(list_with_price_data)

company = 'EA'
#main(company)

# AAPL: TP 0.1% SL 1.8% - 104%
# TQQQ: TP 5.3% SL 11.2% - 90%


print(backtest(utils.get_price_data(company), 5, 7))


# сделать 2 файла - backtest конкретной стратегии и finder - подбор лучших коэффициентов


# tws при потере связи чтобы чаще восстанавливаться пробовала
