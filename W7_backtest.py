# + max losses
# + count of deals, the shortest and the longest deals
import csv

import make_candlestick_chart
import settings
from indicators import stochastic
from strategy import default_strategy as ds
import trade_signals_watcher
import utils


def main(list_with_price_data, strategy):
	buy_and_hold_profitability = 0
	buy_and_hold_quantity = None
	open_order_price = None
	close_order_price = None
	profit = 0
	want_to_open_position = True
	capital = settings.POSITION_QUANTITY
	capital_by_date = []
	quantity = None
	open_position_type = None
	history = []
	history.append(('date', 'action', 'quantity', 'price', 'signal', 'profit'))

	

	for i in range(1, len(list_with_price_data)):
		row = list_with_price_data[i]
		date = row[0]
		open_price = float(row[1])
		high_price = float(row[2])
		low_price = float(row[3])
		close_price = float(row[4])
		
		if row[6] != '' and row[7] != '':
			K = float(row[6])
			D = float(row[7])
		else:
			K = ''
			D = ''

		buy_signal = trade_signals_watcher.buy(row, strategy[0], strategy[1], strategy[2])
		sell_signal = trade_signals_watcher.sell(row, strategy[5], strategy[6], strategy[7])
		stop_loss = strategy[3]
		take_profit = strategy[4]
		if i < len(list_with_price_data) - 1:
			market_price = (abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2)
		# it's not correct, but it must be the closest price to market_price

		if i == 1:
			buy_and_hold_quantity = int(capital / open_price)
		if i == len(list_with_price_data) - 1:
			buy_and_hold_profitability = (close_price * buy_and_hold_quantity - settings.POSITION_QUANTITY) / settings.POSITION_QUANTITY * 100

# OPEN POSITIONS functional

		if open_position_type == None: # no open positions
			capital_by_date.append((date, capital, 2))

	# BUY
			if buy_signal[0] == 'buy':	# signal to buy
				if buy_signal[1] == 'MKT' and i < len(list_with_price_data) - 1:
					open_order_price = market_price
					open_position_type = 'long'
					quantity = int(capital / open_order_price)
					history.append((list_with_price_data[i+1][0], 'long', quantity, open_order_price, ''))
					#capital_by_date.append((list_with_price_data[i+1][0], capital))
	
	# SELL
			if sell_signal[0] == 'sell' and open_position_type != 'long':	# signal to sell
				if sell_signal[1] == 'MKT' and i < len(list_with_price_data) - 1:
					open_order_price = market_price
					open_position_type = 'short'
					quantity = -1 * int(capital / open_order_price)
					history.append((list_with_price_data[i+1][0], 'short', quantity, open_order_price, ''))
					#capital_by_date.append((list_with_price_data[i+1][0], capital))

# CLOSE POSITIONS functional
		else:	# checking open position if it is signal to close

	# close LONG
			if open_position_type == 'long':
				if date == history[-1][0]:
					capital_by_date.append((date, capital, 2))
				else:
					capital_by_date.append((date, close_price * quantity, 2))

		# close long by SL/TP
				if stop_loss != None and take_profit != None:
					
					sl = open_order_price - ((stop_loss / 100) * open_order_price)
					if low_price <= sl:
						if open_price <= sl:	 # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = sl
						profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append((date, 'closed by SL', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital, 2))
						open_position_type = None
					
					tp = (take_profit / 100 + 1) * open_order_price				
					if high_price >= tp and open_position_type != None:
						if open_price >= tp:	 # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = tp
						profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append((date, 'closed by TP', quantity, close_order_price, profit))	
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital, 2))
						open_position_type = None
		# close long by SIGNAL
				if sell_signal[0] == 'sell' and open_position_type != None and i < len(list_with_price_data) - 1:
					if sell_signal[1] == 'MKT':
						close_order_price = market_price
						profit = (close_order_price - open_order_price) * quantity - (0.0065 * 2)*10	# comission + *10 smth wrong
						capital += profit
						history.append((list_with_price_data[i+1][0], 'closed by strategy', quantity, close_order_price, profit))			
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital, 2))
						open_position_type = None
	
		# + open opposite position
						open_order_price = market_price
						open_position_type = 'short'
						quantity = -1 * int(capital / open_order_price)
						history.append((list_with_price_data[i+1][0], 'short', quantity, open_order_price, '', ''))


	# close SHORT
			if open_position_type == 'short':
				if date == history[-1][0]:
					capital_by_date.append((date, capital, 2))
				else:
					capital_by_date.append((date, capital * 2 + (close_price * quantity), 2))
		
		# close short by SL/TP				
				if stop_loss != None and take_profit != None:
					sl = open_order_price + ((stop_loss / 100) * open_order_price)
					if high_price >= sl:
						if open_price >= sl:	# if opens with gap
							close_order_price = open_price
						else:
							close_order_price = sl
						profit = (open_order_price - close_order_price) * abs(quantity) - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append((date, 'closed by SL', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital, 2))
						open_position_type = None
					tp = (1 - take_profit / 100) * open_order_price
					if low_price <= tp and open_position_type != None:
						if open_price <= tp: # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = tp
						profit = (open_order_price - close_order_price) * abs(quantity) - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append((date, 'closed by TP', quantity, close_order_price, profit))		
						open_position_type = None
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital, 2))
		# close short by SIGNAL
				if buy_signal[0] == 'buy' and open_position_type != None and i < len(list_with_price_data) - 1:	# signal to buy
					if buy_signal[1] == 'MKT':
						close_order_price = market_price
						profit = (open_order_price - close_order_price) * abs(quantity) - (0.0065 * 2)*10		# comission + *10 smth wrong
						capital += profit
						history.append((list_with_price_data[i+1][0], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital, 2))
						open_position_type = None
		# + open opposite position
						open_order_price = market_price
						open_position_type = 'long'
						quantity = int(capital / open_order_price)
						history.append((list_with_price_data[i+1][0], 'long', quantity, open_order_price, '', ''))

		if i == len(list_with_price_data) - 1 and open_position_type != None:
			if open_position_type == 'long':
				profit = (close_price - open_order_price) * quantity - (0.0065 * 2)*10		# comission + *10 smth wrong
			if open_position_type == 'short':
				profit = (open_order_price - close_order_price) * abs(quantity) - (0.0065 * 2)*10		# comission + *10 smth wrong
			capital += profit
			history.append((date, 'now', quantity, close_price, '', profit))
	
	profitability = (capital_by_date[-1][1] - capital_by_date[0][1]) / capital_by_date[0][1] * 100
	return (profitability, history, buy_and_hold_profitability, capital_by_date)


if __name__ == '__main__':
	company = 'TSLA'
	list_with_price_data = utils.get_price_data(company)
	try:
		strategy = (None, None, 1, 4.5, 9.0, None, None, 0, (3, 18, 7))
		#(None,None,1,4.5,9.0,None,None,-1,(3, 4, 11))	#utils.the_best_known_strategy(company)
	except:
		strategy = ds.strategy
	stoch_parameters = (strategy[8][0], strategy[8][1], strategy[8][2])
	list_with_price_data = stochastic.main(list_with_price_data, stoch_parameters)
	profit, history, buy_and_hold_profitability, capital_by_date = main(list_with_price_data, strategy)

	for row in history:
		print(row)
	print(f'\nProfitability: {round(profit, 1)}%')
	print(f'\nBuy and hold profitability: {round(buy_and_hold_profitability, 1)}%')
	make_candlestick_chart.main(list_with_price_data, history, capital_by_date, company)

