# + count of deals, the shortest and the longest deals

import make_candlestick_chart
import settings
from indicators import stochastic, volume_profile, SMA
import trade_signals_watcher
import utils


def main(price_data, strategy, historical_volume_profile, step):
	buy_and_hold_profitability = 0
	buy_and_hold_quantity = None
	open_order_price = None
	close_order_price = None
	profit = 0
	want_to_open_position = True
	capital = 100000 * settings.POSITION_QUANTITY
	capital_by_date = []
	quantity = None
	open_position_type = None
	history = []
	history.append(('date', 'action', 'quantity', 'price', 'signal', 'profit'))

	for i in range(len(price_data)):
		row = price_data[i]
		date = row[0]
		open_price = row[1]
		high_price = row[2]
		low_price = row[3]
		close_price = row[4]
		if i < len(price_data) - 1: # if not the last row
			market_price = price_data[i+1][1]	#(abs(price_data[i+1][2] + price_data[i+1][3])) / 2
		# it's not correct, but it must be the closest price to market_price
		if i == 1:
			buy_and_hold_quantity = int(capital / open_price)
		if i == len(price_data) - 1:
			buy_and_hold_profitability = (close_price * buy_and_hold_quantity - (100000 * settings.POSITION_QUANTITY)) / (100000 * settings.POSITION_QUANTITY) * 100

		signal = trade_signals_watcher.signal(price_data[:i+1], historical_volume_profile, strategy)

# OPEN POSITIONS functional
		if open_position_type == None: # no open positions
			capital_by_date.append((date, capital))
	# BUY
			if signal == 'buy':
				if i < len(price_data) - 1:
					open_order_price = market_price*1.002
					open_position_type = 'long'
					quantity = int(capital / open_order_price)
					history.append((price_data[i+1][0], 'long', quantity, open_order_price, ''))
	
	# SELL
			if signal == 'sell':
				if i < len(price_data) - 1:
					open_order_price = market_price*0.998
					open_position_type = 'short'
					quantity = -1 * int(capital / open_order_price)
					history.append((price_data[i+1][0], 'short', quantity, open_order_price, ''))
# CLOSE POSITIONS functional
		else:	# checking open position if it is signal to close
	# close LONG
			if open_position_type == 'long':
				if date == history[-1][0]:
					capital_by_date.append((date, capital))
				else:
					capital_by_date.append((date, close_price * quantity))

		# close long by SL/TP
				if strategy['stop_loss'] != None and strategy['take_profit'] != None:
					
					sl = open_order_price - ((strategy['stop_loss'] / 100) * open_order_price)
					if low_price <= sl:
						if open_price <= sl:	 # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = sl
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (close_order_price - open_order_price) * quantity - comission
						capital += profit
						history.append((date, 'closed by SL', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
					
					tp = (strategy['take_profit'] / 100 + 1) * open_order_price				
					if high_price >= tp and open_position_type != None:
						if open_price >= tp:	 # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = tp
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (close_order_price - open_order_price) * quantity - comission
						capital += profit
						history.append((date, 'closed by TP', quantity, close_order_price, profit))	
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
		# close long by SIGNAL
				if signal == 'sell':
					if open_position_type != None and i < len(price_data) - 1:
						close_order_price = market_price*0.998
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (close_order_price - open_order_price) * quantity - comission
						capital += profit
						history.append((price_data[i+1][0], 'closed by strategy', quantity, close_order_price, profit))			
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
		
			# + open opposite position
						open_order_price = market_price*0.998
						open_position_type = 'short'
						quantity = -1 * int(capital / open_order_price)
						history.append((price_data[i+1][0], 'short', quantity, open_order_price, '', ''))

	# close SHORT
			if open_position_type == 'short':
				if date == history[-1][0]:
					capital_by_date.append((date, capital))
				else:
					capital_by_date.append((date, capital * 2 + (close_price * quantity)))
		
		# close short by SL/TP				
				if strategy['stop_loss'] != None and strategy['take_profit'] != None:
					sl = open_order_price + ((strategy['stop_loss'] / 100) * open_order_price)
					if high_price >= sl:
						if open_price >= sl:	# if opens with gap
							close_order_price = open_price
						else:
							close_order_price = sl
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (open_order_price - close_order_price) * abs(quantity) - comission
						capital += profit
						history.append((date, 'closed by SL', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
					tp = (1 - strategy['take_profit'] / 100) * open_order_price
					if low_price <= tp and open_position_type != None:
						if open_price <= tp: # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = tp
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (open_order_price - close_order_price) * abs(quantity) - comission
						capital += profit
						history.append((date, 'closed by TP', quantity, close_order_price, profit))		
						open_position_type = None
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
		# close short by SIGNAL
				if signal == 'buy':
					if open_position_type != None and i < len(price_data) - 1:
						close_order_price = market_price*1.002
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (open_order_price - close_order_price) * abs(quantity) - comission
						capital += profit
						history.append((price_data[i+1][0], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
			# + open opposite position
						open_order_price = market_price*1.002
						open_position_type = 'long'
						quantity = int(capital / open_order_price)
						history.append((price_data[i+1][0], 'long', quantity, open_order_price, '', ''))

		if i == len(price_data) - 1 and open_position_type != None:
			comission = (0.0035 * 2) * quantity
			if comission < 0.35:
				comission = 0.35
			if open_position_type == 'long':
				profit = (close_price - open_order_price) * quantity - comission
			if open_position_type == 'short':
				profit = (open_order_price - close_price) * abs(quantity) - comission
			capital += profit
			history.append((date, 'now', quantity, close_price, '', profit))
	
	profitability = (capital_by_date[-1][1] - capital_by_date[0][1]) / capital_by_date[0][1] * 100
	return (profitability, history, buy_and_hold_profitability, capital_by_date)


if __name__ == '__main__':
	company = settings.company
	# try:
	# 	strategy = utils.the_best_known_strategy(company)
	# except:
	strategy = {'bar_size': '30 mins',
				'Indicators_combination': '5-10-3-4-5-4',
				'K_level_to_buy': None,
				'D_level_to_buy': (19, 29),
				'KD_difference_to_buy': 1,
				'stop_loss': 4,
				'take_profit': 10,
				'K_level_to_sell': None,
				'D_level_to_sell': None,
				'KD_difference_to_sell': 0,
				'Stoch_parameters': (19, 12, 5),
				'Weekday_buy': 1,
				'Weekday_sell': None,
				'Volume_profile_locator': 14,
				'SMA_period': 100
				}
	# TSLA;180.4;-8.8;-26.0;30 mins;5-10-3-4-5-4;;(19, 29);1;4;10;;;0;(19, 12, 5);1;;14;100
	price_data = utils.get_price_data(company, strategy['bar_size'])
	price_data = stochastic.update(price_data, strategy['Stoch_parameters'])
	price_data = SMA.update(price_data, strategy['SMA_period'])
	
	# price_data_df = utils.get_price_data_df(company, strategy['bar_size'])
	# price_data_df = stochastic.update_df(price_data_df, strategy['Stoch_parameters'])
	
	first_date = price_data[0][0]
	end_date = [int(first_date[:4]), int(first_date[4:6]), int(first_date[6:8])]
	historical_volume_profile, step = volume_profile.historical_volumes(company, end_date)
	profit, history, buy_and_hold_profitability, capital_by_date = main(price_data, strategy, historical_volume_profile, step)
	max_drawdown = utils.max_drawdown_calculate(capital_by_date)
	for row in history:
		print(row)
	print(f'\nProfitability: {round(profit, 1)}%, max drawdown: {round(max_drawdown, 1)}%')
	print(f'\nBuy and hold profitability: {round(buy_and_hold_profitability, 1)}%')
	# make_candlestick_chart.main(price_data, history, capital_by_date, company)
