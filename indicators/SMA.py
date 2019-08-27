def update(price_data, SMA_period, action):
	for row in price_data[:SMA_period - 1]:
		row[f'SMA {action}'] = None
	for i, row in enumerate(price_data[SMA_period-1:]):
		sum = 0
		for rewieving_row in price_data[i:SMA_period+i]:
			close_price = rewieving_row['Close']
			sum += close_price
		average = sum / SMA_period
		row[f'SMA {action}'] = average
	return price_data


def signal(price_data, *args):
	action = args[1]
	time_lag = 3
	try:
		previous_high = price_data[-time_lag]['High']
		previous_low = price_data[-time_lag]['Low']
		previous_close = price_data[-time_lag]['Close']
		previous_SMA = price_data[-time_lag][f'SMA {action}']
	except(IndexError):
		return 0.
	now_high = price_data[-1]['High']
	now_low = price_data[-1]['Low']
	now_SMA = price_data[-1][f'SMA {action}']
	if previous_SMA:
		if action == 'buy' and (now_low - now_SMA) > 0.05 and (previous_SMA - previous_high) > 0.05:
			return 1.
		if action == 'sell' and (now_SMA - now_high) > 0.05 and (previous_low - previous_SMA) > 0.05:
			return 1.
	return 0.
