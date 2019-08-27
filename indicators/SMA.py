def update(price_data, SMA_period):
	for row in price_data[:SMA_period - 1]:
		row['SMA'] = None
	for i, row in enumerate(price_data[SMA_period-1:]):
		sum = 0
		for rewieving_row in price_data[i:SMA_period+i]:
			close_price = rewieving_row['Close']
			sum += close_price
		average = sum / SMA_period
		row['SMA'] = average
	return price_data


def signal(price_data, *args):
	time_lag = 3
	try:
		previous_high = price_data[-time_lag]['High']
		previous_low = price_data[-time_lag]['Low']
		previous_close = price_data[-time_lag]['Close']
		previous_SMA = price_data[-time_lag]['SMA']
	except(IndexError):
		return 0.
	now_high = price_data[-1]['High']
	now_low = price_data[-1]['Low']
	now_close = price_data[-1]['Close']
	now_SMA = price_data[-1]['SMA']
	if previous_SMA:
		a = (now_low - now_SMA) / now_low
		if (now_low - now_SMA) > 0.05 and previous_high < previous_SMA:
			return 1.
		if (now_SMA - now_high) > 0.05 and previous_low > previous_SMA:
			return -1.
	return 0.
