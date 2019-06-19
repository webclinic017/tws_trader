# + max losses
# + count of deals, the shortest and the longest deals

import make_candlestick_chart
import settings
from strategy import test_strategy as ts
import trade_signals_watcher
import utils

def main(list_with_price_data,
		K_level_to_open,
		D_level_to_open,
		KD_difference_to_open,
		stop_loss,
		take_profit,
		K_level_to_close,
		D_level_to_close,
		KD_difference_to_close):
	buy_and_hold_profitability = 0
	buy_and_hold_quantity = None
	open_order_price = None
	close_order_price = None
	profit = 0
	want_to_open_position = True
	capital = settings.POSITION_QUANTITY
	capital_by_date = []
	quantity = None
	history = []
	history.append(('date', 'action', 'quantity', 'price', 'signal', 'profit'))

	for i in range(1, len(list_with_price_data)):
		row = list_with_price_data[i]
		date = row[0]
		open_price = float(row[1])
		high_price = float(row[2])
		low_price = float(row[3])
		close_price = float(row[4])
		K = float(row[6])
		D = float(row[7])
		open_signal = trade_signals_watcher.open_position(row, K_level_to_open, D_level_to_open, KD_difference_to_open)
		close_signal = trade_signals_watcher.close_position(row, K_level_to_close, D_level_to_close, KD_difference_to_close)
		
		if i == 1:
			buy_and_hold_quantity = int(capital / open_price)
		if i == len(list_with_price_data) - 1:
			buy_and_hold_profitability = round((close_price * buy_and_hold_quantity - settings.POSITION_QUANTITY) / settings.POSITION_QUANTITY * 100, 1)

# OPEN POSITIONS functional
		if want_to_open_position: # no open positions
			capital_by_date.append((date, capital))
			if open_signal[0] == 'buy':	# signal to buy
				if open_signal[1] == 'MKT' and i < len(list_with_price_data) - 1:
					open_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					want_to_open_position = False
					quantity = int(capital / open_order_price)
					history.append((list_with_price_data[i+1][0], 'buy', quantity, open_order_price, '', ''))
					capital_by_date.remove((date, capital))
					capital_by_date.append((list_with_price_data[i+1][0], capital))

# CLOSE POSITIONS functional
		else:	# checking open position if it is signal to close
			capital_by_date.append((date, round(close_price * quantity, 2)))
			if stop_loss != None and take_profit != None:
				sl = open_order_price - ((stop_loss / 100) * open_order_price)
				tp = (take_profit / 100 + 1) * open_order_price
				if low_price <= sl:
					if open_price <= sl:
						close_order_price = open_price
					else:
						close_order_price = round(sl, 2)
					profit = round((close_order_price - open_order_price) * quantity - (0.0065 * 2)*10, 2)		# comission + *10 smth wrong
					capital += profit
					history.append((date, 'close', quantity, close_order_price, 'SL', profit))
					want_to_open_position = True
				if high_price >= tp and want_to_open_position == False: # if gap tp = tp (it is not correct, but it is better for estimation - the worst case)
					close_order_price = round(tp, 2)
					profit = round((close_order_price - open_order_price) * quantity - (0.0065 * 2)*10, 2)		# comission + *10 smth wrong
					capital += profit
					history.append((date, 'close', quantity, close_order_price, 'TP', profit))		
					want_to_open_position = True
			if close_signal[0] == 'close' and want_to_open_position == False and i < len(list_with_price_data) - 1:
				if close_signal[1] == 'MKT':
					close_order_price = round((abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2), 2)	# it's not correct, but it must be the closest price to market
					profit = round((close_order_price - open_order_price) * quantity - (0.0065 * 2)*10, 2)		# comission + *10 smth wrong
					capital += profit
					history.append((list_with_price_data[i+1][0], 'close', quantity, close_order_price, 'Strategy', profit))			
					capital_by_date.remove((date, round(close_price * quantity, 2)))
					capital_by_date.append((list_with_price_data[i+1][0], round(close_price * quantity, 2)))
					want_to_open_position = True

		if i == len(list_with_price_data) - 1 and want_to_open_position == False:
			profit = round((close_price - open_order_price) * quantity - (0.0065 * 2)*10, 2)		# comission + *10 smth wrong
			capital += profit
			history.append((date, 'now', quantity, close_price, '', profit))
	
	profitability = round((capital_by_date[-1][1] - capital_by_date[0][1]) / capital_by_date[0][1] * 100, 1)
	return (profitability, history, buy_and_hold_profitability, capital_by_date)


if __name__ == '__main__':
	company = 'KO'
	list_with_price_data = utils.get_price_data(company)

	stop_loss = ts.stop_loss
	take_profit = ts.take_profit
	K_level_to_open = ts.K_level_to_open
	D_level_to_open = ts.D_level_to_open
	KD_difference_to_open = ts.KD_difference_to_open
	K_level_to_close = ts.K_level_to_close
	D_level_to_close = ts.D_level_to_close
	KD_difference_to_close = ts.KD_difference_to_close

	profit, history, buy_and_hold_profitability, capital_by_date = main(list_with_price_data,
							K_level_to_open,
							D_level_to_open,
							KD_difference_to_open,
							stop_loss,
							take_profit,
							K_level_to_close,
							D_level_to_close,
							KD_difference_to_close)
	for row in history:
		print(row)
	print(f'\nProfitability: {profit}%')
	print(f'\nBuy and hold profitability: {buy_and_hold_profitability}%')
	make_candlestick_chart.main(list_with_price_data, history, capital_by_date, company)

