import csv
#import time
from datetime import datetime

import settings
import strategy
import utils

def main(list_with_price_data, stop_loss, take_profit, K_level, D_level, KD_difference):
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
		open_signal = strategy.signal_to_open_position(row, K_level, D_level, KD_difference)
		close_signal = strategy.signal_to_close_position(row, stop_loss, take_profit)

		if want_to_open_position: # no open positions
			if open_signal[0] == 'buy':	# signal to buy
				if open_signal[1] == 'MKT':
					open_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					want_to_open_position = False
					quantity = int(capital / open_order_price)
					history.append(f'{date}: bought {quantity} at ${open_order_price}')
		else:
			if close_signal[0] == 'close':
				if close_signal[1] == 'MKT':
					close_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
					capital += profit
					history.append(f'{date}: close at ${close_order_price}, profit: ${round(profit)}')				
					want_to_open_position = True
				if close_signal[1] == 'SL-TP':
					sl = open_order_price - ((stop_loss / 100) * open_order_price)
					tp = (take_profit / 100 + 1) * open_order_price
					if low_price <= sl:
						close_order_price = round(sl, 2)
						profit = round((close_order_price - open_order_price) * quantity - (0.0065 * 2)*10, 2)		# comission + *10 smth wrong
						capital += profit
						history.append(f'{date}: close at ${close_order_price}, profit: -${abs(round(profit))}')				
						want_to_open_position = True
					if high_price >= tp:
						close_order_price = round(tp, 2)
						profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append(f'{date}: close at ${close_order_price}, profit: ${round(profit)}')				
						want_to_open_position = True
		if i == len(list_with_price_data) - 1 and want_to_open_position == False:
			profit = (close_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
			capital += profit
			history.append(f'{date}: Last price: ${close_price}, potencial profit: {round(profit)}')
	
	profitability = round((capital - settings.POSITION_QUANTITY) / settings.POSITION_QUANTITY * 100, 1)
	
	return (profitability, history)

if __name__ == '__main__':
	company = 'AAPL'
	list_with_price_data = utils.get_price_data(company)
	stop_loss = 1
	take_profit = 7.5
	K_level = (0,100)
	D_level = (0,100)
	KD_difference = 0
	profit, history = main(list_with_price_data, stop_loss, take_profit, K_level, D_level, KD_difference)
	for row in history:
		print(row)
	print(f'\nProfitability: {profit}%')

