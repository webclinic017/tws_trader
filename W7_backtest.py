# + count of deals, the shortest and the longest deals

import make_candlestick_chart
import settings
from indicators import stochastic, volume_profile, SMA, RS
import signals
import utils


def main(price_data, strategy):
	open_order_price = None
	profit = 0
	capital = 100000
	capital_by_date = []
	quantity = None
	open_position_type = None
	history = []
	history.append(('date', 'action', 'quantity', 'price', 'signal', 'profit'))

	for i in range(len(price_data)):
		row = price_data[i]
		date = row['Datetime']
		open_price = row['Open']
		high_price = row['High']
		low_price = row['Low']
		close_price = row['Close']
		if i < len(price_data) - 1: # if not the last row
			market_price = price_data[i+1]['Open']	#(abs(price_data[i+1][2] + price_data[i+1][3])) / 2
		# it's not correct, but it must be the closest price to market_price

		signal = signals.check(price_data[:i + 1], strategy['indicators'])

# OPEN POSITIONS functional
		if open_position_type == None: # no open positions
			capital_by_date.append((date, capital + profit))
	# BUY
			if signal == 'buy':
				if i < len(price_data) - 1:
					open_order_price = market_price * 1.002
					open_position_type = 'long'
					quantity = int(capital / open_order_price)
					history.append((price_data[i+1]['Datetime'], 'long', quantity, open_order_price, ''))
	
	# SELL
			if signal == 'sell':
				if i < len(price_data) - 1:
					open_order_price = market_price*0.998
					open_position_type = 'short'
					quantity = -1 * int(capital / open_order_price)
					history.append((price_data[i+1]['Datetime'], 'short', quantity, open_order_price, ''))
# CLOSE POSITIONS functional
		else:	# checking open position if it is signal to close
	# close LONG
			if open_position_type == 'long':
				if date == history[-1][0]:
					capital_by_date.append((date, capital + profit))
				else:
					capital_by_date.append((date, close_price * quantity + profit))

		# close long by SL/TP
				if strategy['stop_loss']:
					sl = open_order_price - ((strategy['stop_loss'] / 100) * open_order_price)
					if low_price <= sl:
						if open_price <= sl:	 # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = sl
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit += (close_order_price - open_order_price) * quantity - comission
						history.append((date, 'closed by SL', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital + profit))
						open_position_type = None
				if strategy['take_profit'] and open_position_type:
					tp = (strategy['take_profit'] / 100 + 1) * open_order_price				
					if high_price >= tp and open_position_type != None:
						if open_price >= tp:	 # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = tp
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit += (close_order_price - open_order_price) * quantity - comission
						history.append((date, 'closed by TP', quantity, close_order_price, profit))	
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital + profit))
						open_position_type = None
		# close long by SIGNAL
				if signal == 'sell':
					if open_position_type != None and i < len(price_data) - 1:
						close_order_price = market_price*0.998
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit += (close_order_price - open_order_price) * quantity - comission
						history.append((price_data[i+1]['Datetime'], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital + profit))
						# Open opposite position
						open_order_price = market_price*0.998
						open_position_type = 'short'
						quantity = -1 * int(capital / open_order_price)
						history.append((price_data[i+1]['Datetime'], 'short', quantity, open_order_price, '', ''))

	# close SHORT
			if open_position_type == 'short':
				if date == history[-1][0]:
					capital_by_date.append((date, capital + profit))
				else:
					capital_by_date.append((date, capital * 2 + (close_price * quantity) + profit))
		
		# close short by SL/TP				
				if strategy['stop_loss']:
					sl = open_order_price + ((strategy['stop_loss'] / 100) * open_order_price)
					if high_price >= sl:
						if open_price >= sl:	# if opens with gap
							close_order_price = open_price
						else:
							close_order_price = sl
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit += (open_order_price - close_order_price) * abs(quantity) - comission
						history.append((date, 'closed by SL', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital + profit))
						open_position_type = None
				if strategy['take_profit'] and open_position_type:
					tp = (1 - strategy['take_profit'] / 100) * open_order_price
					if low_price <= tp and open_position_type != None:
						if open_price <= tp: # if opens with gap
							close_order_price = open_price
						else:
							close_order_price = tp
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit += (open_order_price - close_order_price) * abs(quantity) - comission
						history.append((date, 'closed by TP', quantity, close_order_price, profit))		
						open_position_type = None
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital + profit))
		# close short by SIGNAL
				if signal == 'buy':
					if open_position_type != None and i < len(price_data) - 1:
						close_order_price = market_price*1.002
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit += (open_order_price - close_order_price) * abs(quantity) - comission
						history.append((price_data[i+1]['Datetime'], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital + profit))
						open_position_type = None
			# + open opposite position
						open_order_price = market_price*1.002
						open_position_type = 'long'
						quantity = int(capital / open_order_price)
						history.append((price_data[i+1]['Datetime'], 'long', quantity, open_order_price, '', ''))

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
	return (profitability, history, capital_by_date)


if __name__ == '__main__':
	company = settings.company
	try:
		strategy = utils.the_best_known_strategy(company)
	except:
		strategy = {'company': 'TSLA',
				'profit': 180,
				'max_drawdown': 12,
				'buy_and_hold_profitability': -35,
				'bar_size': '30 mins',
				'stop_loss': 15,
				'take_profit': 10,
	            'indicators': {
					'stochastic': {
						'weight': 10,   # 10
						'K_level_to_buy': None,
						'D_level_to_buy': (19, 29),
						'KD_difference_to_buy': 1,
						'K_level_to_sell': None,
						'D_level_to_sell': None,
						'KD_difference_to_sell': 0,
						'stoch_period': 19,
						'stoch_slow_avg': 12,
						'stoch_fast_avg': 5
					},
	                'weekday': {
	                    'weight': 3,    # 3
	                    'Weekday_buy': 1,
	                    'Weekday_sell': 345
	                },
		            'volume_profile': {
						'weight': 4,    # 4
			            'locator': 14
		            },
		            'japanese_candlesticks': {
			            'weight': 5     # 5
		            },
					'SMA': {
						'weight': 4,    # 4
						'period': 32
					},
		            'RS': {
			            'weight': 0,
			            'ZZ_movement': 10,
			            'close_index': 3
		            }
	            }
		}
	historical_data = utils.request_historical_data(company)
	price_data = utils.get_price_data(company, strategy['bar_size'])
	price_data = stochastic.update(price_data,
	                               strategy['indicators']['stochastic']['stoch_period'],
				                   strategy['indicators']['stochastic']['stoch_slow_avg'],
				                   strategy['indicators']['stochastic']['stoch_fast_avg'])
	price_data = SMA.update(price_data, strategy['indicators']['SMA']['period'])
	price_data = volume_profile.update(price_data, strategy['indicators']['volume_profile']['locator'], historical_data)
	price_data = RS.update(price_data, strategy['indicators']['RS'], historical_data)

	profit, history, capital_by_date = main(price_data, strategy)
	max_drawdown = utils.max_drawdown_calculate(capital_by_date)
	for row in history:
		print(row)
	print(f'\nProfitability: {round(profit, 1)}%, max drawdown: {round(max_drawdown, 1)}%')
	buy_and_hold_profitability = ((price_data[-1]['Close'] - price_data[0]['Open']) / price_data[0]['Open']) * 100
	print(f'\nBuy and hold profitability: {round(buy_and_hold_profitability, 1)}%')
	# make_candlestick_chart.main(price_data, history, capital_by_date, company)
