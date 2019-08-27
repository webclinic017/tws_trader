# + count of deals, the shortest and the longest deals

import make_candlestick_chart
import settings
from indicators import stochastic, volume_profile, SMA, RS
import signals
import utils


def main(price_data, strategy):
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
		date = row['Datetime']
		open_price = row['Open']
		high_price = row['High']
		low_price = row['Low']
		close_price = row['Close']
		if i < len(price_data) - 1:  # if not the last row
			market_price = price_data[i + 1]['Open']  # (abs(price_data[i+1][2] + price_data[i+1][3])) / 2
		# it's not correct, but it must be the closest price to market_price

		buy_signal = signals.check(price_data[:i + 1], strategy['buy'], 'buy')
		sell_signal = signals.check(price_data[:i + 1], strategy['sell'], 'sell')

		# OPEN POSITIONS functional
		if open_position_type == None:  # no open positions
			capital_by_date.append((date, capital))
			# BUY
			if buy_signal and not sell_signal:
				if i < len(price_data) - 1:
					open_order_price = market_price * 1.002
					open_position_type = 'long'
					quantity = int(capital / open_order_price)
					history.append((price_data[i + 1]['Datetime'], 'long', quantity, open_order_price, ''))

			# SELL
			if sell_signal and not buy_signal:
				if i < len(price_data) - 1:
					open_order_price = market_price * 0.998
					open_position_type = 'short'
					quantity = -1 * int(capital / open_order_price)
					history.append((price_data[i + 1]['Datetime'], 'short', quantity, open_order_price, ''))
		# CLOSE POSITIONS functional
		else:  # checking open position if it is signal to close
			# close LONG
			if open_position_type == 'long':
				if date == history[-1][0]:
					capital_by_date.append((date, capital))
				else:
					capital_by_date.append((date, close_price * quantity))

				# close long by SL/TP
				if strategy['stop_loss']:
					sl = open_order_price - ((strategy['stop_loss'] / 100) * open_order_price)
					if low_price <= sl:
						if open_price <= sl:  # if opens with gap
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
				if strategy['take_profit'] and open_position_type:
					tp = (strategy['take_profit'] / 100 + 1) * open_order_price
					if high_price >= tp and open_position_type != None:
						if open_price >= tp:  # if opens with gap
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
				if sell_signal:
					if open_position_type != None and i < len(price_data) - 1:
						close_order_price = market_price * 0.998
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (close_order_price - open_order_price) * quantity - comission
						capital += profit
						history.append(
							(price_data[i + 1]['Datetime'], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None

						# + open opposite position
						open_order_price = market_price * 0.998
						open_position_type = 'short'
						quantity = -1 * int(capital / open_order_price)
						history.append((price_data[i + 1]['Datetime'], 'short', quantity, open_order_price, '', ''))

			# close SHORT
			if open_position_type == 'short':
				if date == history[-1][0]:
					capital_by_date.append((date, capital))
				else:
					capital_by_date.append((date, capital * 2 + (close_price * quantity)))

				# close short by SL/TP
				if strategy['stop_loss']:
					sl = open_order_price + ((strategy['stop_loss'] / 100) * open_order_price)
					if high_price >= sl:
						if open_price >= sl:  # if opens with gap
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
				if strategy['take_profit'] and open_position_type:
					tp = (1 - strategy['take_profit'] / 100) * open_order_price
					if low_price <= tp and open_position_type != None:
						if open_price <= tp:  # if opens with gap
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
				if buy_signal:
					if open_position_type != None and i < len(price_data) - 1:
						close_order_price = market_price * 1.002
						comission = (0.0035 * 2) * quantity
						if comission < 0.35:
							comission = 0.35
						profit = (open_order_price - close_order_price) * abs(quantity) - comission
						capital += profit
						history.append(
							(price_data[i + 1]['Datetime'], 'closed by strategy', quantity, close_order_price, profit))
						capital_by_date.pop(-1)
						capital_by_date.append((date, capital))
						open_position_type = None
						# + open opposite position
						open_order_price = market_price * 1.002
						open_position_type = 'long'
						quantity = int(capital / open_order_price)
						history.append((price_data[i + 1]['Datetime'], 'long', quantity, open_order_price, '', ''))

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
	# try:
	# 	strategy = utils.the_best_known_strategy(company)
	# except:
	strategy = {'company': 'TSLA',
	            'profit': 180,
	            'max_drawdown': 12,
	            'buy_and_hold_profitability': -35,
	            'bar_size': '30 mins',

	            # put it in buy & sell
	            'stop_loss': 10,
	            'take_profit': 15,

	            'buy': {
		            'stochastic': {
			            'weight': 10,  # 10
			            'K_min': 0.,
			            'K_max': 100.,
			            'D_min': 19.,
			            'D_max': 29.,
			            'KD_difference': 'K>D',
			            'stoch_period': 19,
			            'stoch_slow_avg': 12,
			            'stoch_fast_avg': 5
		            },
		            'weekday': {
			            'weight': 3,  # 3
			            'Weekday': 1,
		            },
		            'volume_profile': {
			            'weight': 4,  # 4
			            'locator': 14
		            },
		            'japanese_candlesticks': {
			            'weight': 5  # 5
		            },
		            'SMA': {
			            'weight': 4,  # 4
			            'period': 32
		            },
		            'RS': {
			            'weight': 0,
			            'ZZ_movement': 10,
			            'close_index': 3
		            }
	            },
	            'sell': {
		            'stochastic': {
			            'weight': 10,  # 10
			            'K_min': 0,
			            'K_max': 100,
			            'D_min': 0,
			            'D_max': 100,
			            'KD_difference': 'K=D',
			            'stoch_period': 19,
			            'stoch_slow_avg': 12,
			            'stoch_fast_avg': 5
		            },
		            'weekday': {
			            'weight': 3,  # 3
			            'Weekday': 345
		            },
		            'volume_profile': {
			            'weight': 4,  # 4
			            'locator': 14
		            },
		            'japanese_candlesticks': {
			            'weight': 5  # 5
		            },
		            'SMA': {
			            'weight': 4,  # 4
			            'period': 32
		            },
		            'RS': {
			            'weight': 0,
			            'ZZ_movement': 10,
			            'close_index': 3
		            }
	            }
	            }
	# strategy = utils.the_best_known_strategy(company)
	# strategy = {'company': 'TSLA', 'profit': 74.5, 'max_drawdown': None, 'buy_and_hold_profitability': -37.8, 'bar_size': '30 mins', 'stop_loss': 4, 'take_profit': 15, 'indicators': {'stochastic': {'K_level_to_buy': None, 'D_level_to_buy': (19, 29), 'KD_difference_to_buy': 1, 'K_level_to_sell': None, 'D_level_to_sell': None, 'KD_difference_to_sell': 0, 'stoch_period': 19, 'stoch_slow_avg': 12, 'stoch_fast_avg': 5, 'weight': 0}, 'weekday': {'Weekday_buy': 1, 'Weekday_sell': 345, 'weight': 0}, 'japanese_candlesticks': {'weight': 0}, 'volume_profile': {'locator': 14, 'weight': 0}, 'SMA': {'period': 32, 'weight': 0}, 'RS': {'ZZ_movement': 10, 'close_index': 4, 'weight': 6}}}
	historical_data = utils.request_historical_data(company)
	price_data = utils.get_price_data(company, strategy['bar_size'])
	for action in ('buy', 'sell'):
		price_data = stochastic.update(price_data,
		                               strategy[f'{action}']['stochastic']['stoch_period'],
		                               strategy[f'{action}']['stochastic']['stoch_slow_avg'],
		                               strategy[f'{action}']['stochastic']['stoch_fast_avg'],
		                               action
		                               )
		price_data = SMA.update(price_data,
		                        strategy[f'{action}']['SMA']['period'],
		                        action)
		price_data = volume_profile.update(price_data,
		                                   strategy[f'{action}']['volume_profile']['locator'],
		                                   historical_data,
		                                   action)
		price_data = RS.update(price_data,
		                       strategy['indicators']['RS'],
		                       historical_data,
		                       action)

	profit, history, capital_by_date = main(price_data, strategy)
	max_drawdown = utils.max_drawdown_calculate(capital_by_date)
	for row in history:
		print(row)
	print(f'\nProfitability: {round(profit, 1)}%, max drawdown: {round(max_drawdown, 1)}%')
	buy_and_hold_profitability = ((price_data[-1]['Close'] - price_data[0]['Open']) / price_data[0]['Open']) * 100
	print(f'\nBuy and hold profitability: {round(buy_and_hold_profitability, 1)}%')
# make_candlestick_chart.main(price_data, history, capital_by_date, company)
