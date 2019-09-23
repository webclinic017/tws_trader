import make_candlestick_chart
import settings
import signals
import utils

BAD_LUCK = 0.002
COMISSION = 0.0035  #   per share

def main(strategy, price_data):
	profit = 0
	capital = 100000
	position = 0
	history = []
	history.append(('date', 'action', 'quantity', 'price', 'signal', 'profit'))
	for i in range(len(price_data) - 1):
		row = price_data[i]
		date = row['Datetime']
		open_price = row['Open']
		high_price = row['High']
		low_price = row['Low']
		market_price = price_data[i + 1]['Open']  # (abs(price_data[i+1][2] + price_data[i+1][3])) / 2
		# it's not correct, but it must be the closest price to market_price
		market_to_buy = market_price * (1 + BAD_LUCK)
		market_to_sell = market_price * (1 - BAD_LUCK)
		buy_signal, sell_signal = signals.check(price_data[:i + 1], strategy)

		# OPEN NEW POSITIONS
		if not position:  # no open positions
			# BUY
			if buy_signal and not sell_signal:
				deal_price = market_to_buy
				position = capital / deal_price
				profit -= position * COMISSION
				sl = deal_price - ((strategy['buy']['SL'] / 100) * deal_price)
				tp = (strategy['buy']['TP'] / 100 + 1) * deal_price
				history.append((price_data[i + 1]['Datetime'], 'long', position, deal_price, ''))
			# SELL
			if sell_signal and not buy_signal:
				deal_price = market_to_sell
				position = -1 * int(capital / deal_price)
				profit -= -position * COMISSION
				sl = deal_price + ((strategy['sell']['SL'] / 100) * deal_price)
				tp = (1 - strategy['sell']['TP'] / 100) * deal_price
				history.append((price_data[i + 1]['Datetime'], 'short', position, deal_price, '', ''))
		# CLOSE POSITIONS (and OPEN if it is signal)
		else:  # checking open position if it is signal to close
			# close LONG
			if position > 0.:
				# close long by SL
				if low_price <= sl:
					if open_price <= sl:  # if opens with gap
						sl = open_price
					profit += (sl - deal_price) * position - position * COMISSION
					history.append((date, 'closed by SL', position, sl, profit))
					position = 0
				# close long by TP
				if high_price >= tp and position:
					if open_price >= tp:  # if opens with gap
						tp = open_price
					profit += (tp - deal_price) * position - position * COMISSION
					history.append((date, 'closed by TP', position, tp, profit))
					position = 0
				# close long by SIGNAL
				if sell_signal and position:
					profit += (market_to_sell - deal_price) * position - position * COMISSION
					history.append((price_data[i + 1]['Datetime'], 'closed by strategy', position, market_to_sell, profit))
					# Open short
					deal_price = market_to_sell
					position = -1 * int(capital / deal_price)
					profit -= -position * COMISSION
					sl = deal_price + ((strategy['sell']['SL'] / 100) * deal_price)
					tp = (1 - strategy['sell']['TP'] / 100) * deal_price
					history.append((price_data[i + 1]['Datetime'], 'short', position, deal_price, '', ''))
			# close SHORT
			if position < 0.:
				# close short by SL
				if high_price >= sl:
					if open_price >= sl:  # if opens with gap
						sl = open_price
					profit += (deal_price - sl) * abs(position) + position * COMISSION
					history.append((date, 'closed by SL', position, sl, profit))
					position = 0
				# close short by TP
				if low_price <= tp and position:
					if open_price <= tp:  # if opens with gap
						tp = open_price
					profit += (deal_price - tp) * abs(position) + position * COMISSION
					history.append((date, 'closed by TP', position, tp, profit))
					position = 0
				# close short by SIGNAL
				if buy_signal and position:
					profit += (deal_price - market_to_buy) * abs(position) + position * COMISSION
					history.append((price_data[i + 1]['Datetime'], 'closed by strategy', position, market_to_buy, profit))
					# Open long
					deal_price = market_to_buy
					position = capital / deal_price
					profit -= position * COMISSION
					sl = deal_price - ((strategy['buy']['SL'] / 100) * deal_price)
					tp = (strategy['buy']['TP'] / 100 + 1) * deal_price
					history.append((price_data[i + 1]['Datetime'], 'long', position, deal_price, ''))
		price_data[i]['Capital'] = capital + profit

	last_quantity = history[-1][2]
	last_deal_price = history[-1][3]
	if history[-1][1] == 'long':
		profit += (price_data[-1]['Close'] - last_deal_price) * last_quantity - COMISSION * last_quantity
	if history[-1][1] == 'short':
		profit += (last_deal_price - price_data[-1]['Close']) * abs(last_quantity) - COMISSION * last_quantity
	price_data[-1]['Capital'] = capital + profit
	history.append((price_data[-1]['Datetime'], 'now', last_quantity, price_data[-1]['Close'], '', profit))
	profitability = (price_data[-1]['Capital'] - price_data[0]['Capital']) / price_data[0]['Capital'] * 100
	return profitability, history, price_data


if __name__ == '__main__':
	company = settings.company
	# company = 'GBTC'
	try:
		strategy = utils.the_best_known_strategy2(company)
	except:
		strategy = {
			'company': company,
	        'bar_size': '30 mins',
	        'buy': {
	            'TP': 15,
	            'SL': 15,
	            'stochastic': {
		            'weight': 10,  # 10
		            'K_min': 19,
		            'K_max': 29.,
		            'D_min': 0.,
		            'D_max': 100.,
		            'KD_difference': 'K>D',
		            'stoch_period': 19,
		            'stoch_slow_avg': 12,
		            'stoch_fast_avg': 5
	            },
	            'weekday': {
		            'weight': 3,  # 3
		            'weekday': 1,
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
	            'TP': 15,
	            'SL': 15,
	            'stochastic': {
		            'weight': 10,  # 10
		            'K_min': 19,
		            'K_max': 29,
		            'D_min': 0,
		            'D_max': 100,
		            'KD_difference': 'K=D',
		            'stoch_period': 19,
		            'stoch_slow_avg': 12,
		            'stoch_fast_avg': 5
	            },
	            'weekday': {
		            'weight': 3,  # 3
		            'weekday': 345
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
	historical_data = utils.request_historical_data(strategy['company'])
	price_data = utils.get_price_data(strategy['company'], strategy['bar_size'])
	price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)
	profit, history, price_data = main(strategy, price_data)
	max_drawdown = utils.max_drawdown_calculate(price_data)
	print(strategy)
	for row in history:
		print(row)
	print(f'\nProfitability: {round(profit, 1)}%, max drawdown: {round(max_drawdown, 1)}%')
	buy_and_hold_profitability = ((price_data[-1]['Close'] - price_data[0]['Open']) / price_data[0]['Open']) * 100
	print(f'\nBuy and hold profitability: {round(buy_and_hold_profitability, 1)}%')
	make_candlestick_chart.main(price_data, history, company)
