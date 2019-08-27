def fast_K_list(price_data, period, slow_average_period, fast_average_period):
	fast_K_list = []
	data_length = len(price_data)
	for i in range(slow_average_period+fast_average_period-1):	
		close_price = price_data[data_length-1-i]['Close']
		highs_prices = tuple(x['High'] for x in price_data[data_length-period-i:data_length-i])
		lows_prices = tuple(x['Low'] for x in price_data[data_length-period-i:data_length-i])
		lowest_price_for_period = min(lows_prices)
		highest_price_for_period = max(highs_prices)		
		if highest_price_for_period != lowest_price_for_period:
			fast_K = (close_price - lowest_price_for_period) / (highest_price_for_period - lowest_price_for_period) * 100
		else:
			fast_K = 50
		fast_K_list.append(fast_K)
	return tuple(reversed(fast_K_list))


def fast_average(fast_K_list, slow_average_period, fast_average_period):	# fast_average = SMA of the fast_K
	fast_average_list = []
	for i in range(1, slow_average_period+1):
		slow_k = sum(fast_K_list[-fast_average_period-i:-i]) / fast_average_period
		fast_average_list.append(slow_k)
	return tuple(reversed(fast_average_list))


def slow_average(fast_average_list, slow_average_period):	# slow_average = SMA of the fast_average
	slow_average = sum(fast_average_list) / slow_average_period
	return slow_average


def update(price_data, period, slow_average_period, fast_average_period, action):
	for i in range(len(price_data)):
		reviewing_prices = price_data[:-i]
		if len(reviewing_prices) > period + slow_average_period + fast_average_period - 2:
			fast_Ks = fast_K_list(reviewing_prices, period, slow_average_period, fast_average_period)
			fastaverage = fast_average(fast_Ks, slow_average_period, fast_average_period)[-1]
			slowaverage = slow_average(fast_average(fast_Ks, slow_average_period, fast_average_period), slow_average_period)
			price_data[-i][f'%K {action}'] = fastaverage
			price_data[-i][f'%D {action}'] = slowaverage
		else:
			price_data[-i][f'%K {action}'] = None
			price_data[-i][f'%D {action}'] = None
	return price_data


def signal(price_data, strategy_indicator, action):
	K_min = strategy_indicator['K_min']
	K_max = strategy_indicator['K_max']
	D_min = strategy_indicator['D_min']
	D_max = strategy_indicator['D_max']
	KD_difference = strategy_indicator['KD_difference']
	K = price_data[-1][f'%K {action}']
	D = price_data[-1][f'%D {action}']
	cross_level = 2.
	try:
		if K_min <= K <= K_max and D_min <= D <= D_max:
			if KD_difference == 'K=D' and -cross_level < (K - D) < cross_level:
				return 1.
			if KD_difference == 'K<D' and (K - D) < -cross_level:
				return 1.
			if KD_difference == 'K>D' and (K - D) > cross_level:
				return 1.
			if not KD_difference:
				return 1.
	except(TypeError):
		return 0.
	return 0.
