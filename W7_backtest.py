# + count of deals, the shortest and the longest deals

import make_candlestick_chart
import settings
from indicators import stochastic
from indicators import volume_profile
import trade_signals_watcher
import utils


def main(list_with_price_data, strategy, historical_volume_profile, step):
	buy_and_hold_profitability = 0
	buy_and_hold_quantity = None
	open_order_price = None
	close_order_price = None
	profit = 0
	want_to_open_position = True
	capital = 100000 * settings.POSITION_QUANTITY / 100
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
		if i < len(list_with_price_data) - 1:
			market_price = (abs(float(list_with_price_data[i+1][2]) + float(list_with_price_data[i+1][3])) / 2)
		# it's not correct, but it must be the closest price to market_price
		if i == 1:
			buy_and_hold_quantity = int(capital / open_price)
		if i == len(list_with_price_data) - 1:
			buy_and_hold_profitability = (close_price * buy_and_hold_quantity - (100000 * settings.POSITION_QUANTITY / 100)) / (100000 * settings.POSITION_QUANTITY / 100) * 100

		signal = trade_signals_watcher.signal(list_with_price_data[:i+1], historical_volume_profile, strategy)

# OPEN POSITIONS functional
		if open_position_type == None: # no open positions
			capital_by_date.append((date, capital))
	# BUY
			if signal == 'buy':
				if i < len(list_with_price_data) - 1:
					open_order_price = market_price
					open_position_type = 'long'
					quantity = int(capital / open_order_price)
					history.append((list_with_price_data[i+1][0], 'long', quantity, open_order_price, ''))
	
	# SELL
			if signal == 'sell':
				if i < len(list_with_price_data) - 1:
					open_order_price = market_price
					open_position_type = 'short'
					quantity = -1 * int(capital / open_order_price)
					history.append((list_with_price_data[i+1][0], 'short', quantity, open_order_price, ''))
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
					if open_position_type != None and i < len(list_with_price_data) - 1:
						close_order_price = market_price
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (close_order_price - open_order_price) * quantity - comission
						capital += profit
						history.append((list_with_price_data[i+1][0], 'closed by strategy', quantity, close_order_price, profit))			
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
		
			# + open opposite position
						open_order_price = market_price
						open_position_type = 'short'
						quantity = -1 * int(capital / open_order_price)
						history.append((list_with_price_data[i+1][0], 'short', quantity, open_order_price, '', ''))

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
					if open_position_type != None and i < len(list_with_price_data) - 1:
						close_order_price = market_price
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (open_order_price - close_order_price) * abs(quantity) - comission
						capital += profit
						history.append((list_with_price_data[i+1][0], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
			# + open opposite position
						open_order_price = market_price
						open_position_type = 'long'
						quantity = int(capital / open_order_price)
						history.append((list_with_price_data[i+1][0], 'long', quantity, open_order_price, '', ''))

		if i == len(list_with_price_data) - 1 and open_position_type != None:
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
	try:
		strategy = utils.the_best_known_strategy(company)
	except:
		#TSLA;203.89400549999928;12.0595401895667;-28.706049999999994;;(19, 29);1;4;8.5;;;0;(19, 12, 5)
		strategy = {'bar_size': '30 mins',
					'Indicators_combination': '+S+W+V',
					'K_level_to_buy': None,
					'D_level_to_buy': (20, 30),
					'KD_difference_to_buy': 1,
					'stop_loss': 4,
					'take_profit': 8.5,
					'K_level_to_sell': None,
					'D_level_to_sell': None,
					'KD_difference_to_sell': 0,
					'Stoch_parameters': (19, 12, 5),
					'Volume_profile_locator': None
					}
	list_with_price_data = utils.get_price_data(company, strategy['bar_size'])
	list_with_price_data = stochastic.main(list_with_price_data, strategy['Stoch_parameters'])

	first_date = list_with_price_data[1][0]
	end_date = [int(first_date[:4]), int(first_date[4:6]), int(first_date[6:8])]
	historical_volume_profile, step = volume_profile.historical_volumes(end_date)


	profit, history, buy_and_hold_profitability, capital_by_date = main(list_with_price_data, strategy, historical_volume_profile, step)
	max_drawdown = utils.max_drawdown_calculate(capital_by_date)
	for row in history:
		print(row)
	print(f'\nProfitability: {round(profit, 1)}%, max drawdown: {round(max_drawdown, 1)}%')
	print(f'\nBuy and hold profitability: {round(buy_and_hold_profitability, 1)}%')
	make_candlestick_chart.main(list_with_price_data, history, capital_by_date, company)

