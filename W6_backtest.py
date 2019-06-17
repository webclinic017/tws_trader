import csv
#import time
from datetime import datetime

#from ib.opt import message, Connection
#import orders_checking

def get_data(stock_ticker):
	list_with_price_data=[]
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)
	return list_with_price_data

def signal_to_open_position(K, D):
	if K > D:
		return (1, 'MKT')	# 1 means buy
	return (0, 0)

def signal_to_close_position(buy_price, price, K, D):
	if K < 20:
		return 1
	return 0		# + price: TP, SL or market

def backtest(list_with_price_data, i1, i2):
	buy_price = None
	profit = 0
	open_position = False
	min_capital = 0
	waiting_for_the_next_candle = False
	order_type = None
	
	for row in list_with_price_data[1:]:
		date = row[0]
		open_price = float(row[1])
		high_price = float(row[2])
		low_price = float(row[3])
		close_price = float(row[4])
		K = float(row[6])
		D = float(row[7])

		if open_position == False: # no open positions
			(signal, order_type) = signal_to_open_position(K, D)
			if waiting_for_the_next_candle == False: # do not waiting for next row
				if signal == 1:	# signal to buy
					waiting_for_the_next_candle = True # wait for the next row
			else:
				if order_type == 'MKT':
					buy_price = round((abs(close_price + open_price) / 2), 2)	# it's not correct, but it must be the closest price to market
					print(f'{date}: bought with price ${buy_price}')
					open_position = True
					if buy_price > min_capital + profit:
						min_capital = buy_price
					waiting_for_the_next_candle = False

		else:
			diff = ((high_price - buy_price) / buy_price) * 100
			# if D >= 80:
			# #	print(f'+ {date}: close at {close_price}')
			# 	open_position = False
			# 	profit += (close_price - buy_price)
			
			# if diff >= i1:
			# 	open_position = False
			# 	profit += (high_price - buy_price) - (0.0065 * 2)*10	# comission + *10 smth wrong
			# 	print(f'+ {date}: close at {high_price}, profit: {round(profit)}')
			# if diff <= -i2:
			# 	open_position = False
			# 	profit += (low_price - buy_price) - (0.0065 * 2)*10		# comission + *10 smth wrong
			# 	print(f'- {date}: close at {low_price}, profit: {round(profit)}')
			
			if signal_to_close_position(buy_price, close_price, K, D) == 1:
				open_position = False
				profit += (close_price - buy_price) - (0.0065 * 2)*10		# comission + *10 smth wrong
				print(f'- {date}: close at {low_price}, profit: {round(profit)}')				


	if open_position == True:
		profit += (close_price - buy_price) - (0.0065 * 2)*10		# comission + *10 smth wrong
		print(f'Last price: ${close_price}, profit: {round(profit)}')
	return (min_capital, round(profit, 1))

def find_optimum_strategy(list_with_price_data):
	buy_price = None
	profit = 0
	open_position = False
	in_watchlist = False

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


print(backtest(get_data(company), 5, 7))


# сделать 2 файла - backtest конкретной стратегии и finder - подбор лучших коэффициентов


# tws при потере связи чтобы чаще восстанавливаться пробовала
