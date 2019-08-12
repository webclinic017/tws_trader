def fast_K_list(price_data, period, slow_average_period, fast_average_period):
	fast_K_list = []
	data_length = len(price_data)
	for i in range(slow_average_period+fast_average_period-1):	
		close_price = price_data[data_length-1-i][4]
		lows_prices = tuple(x[3] for x in price_data[data_length-period-i:data_length-i])
		highs_prices = tuple(x[2] for x in price_data[data_length-period-i:data_length-i])		
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


def delete_columns_with_indicator(price_data): 	# m.b. with pandas.DataFrame it would be easier ?!
	for row in price_data:
		try:
			row.remove(row[6])
			row.remove(row[6])
		except(IndexError):	# if new price_data was added without indicator's values
			continue
	return price_data

# РАЗОБРАТЬСЯ!!!!!
def update(price_data, parameters):
	period = parameters[0]
	slow_average_period = parameters[1]
	fast_average_period = parameters[2]
	price_data = delete_columns_with_indicator(price_data)
	for i in range(len(price_data)):
		reviewing_prices = price_data[:-i]
		if len(reviewing_prices) > period + slow_average_period + fast_average_period - 2:
			fast_Ks = fast_K_list(reviewing_prices, period, slow_average_period, fast_average_period)
			fastaverage = fast_average(fast_Ks, slow_average_period, fast_average_period)[-1]
			slowaverage = slow_average(fast_average(fast_Ks, slow_average_period, fast_average_period), slow_average_period)
			price_data[-i].append(fastaverage)
			price_data[-i].append(slowaverage)
		else:
			price_data[-i].append('')
			price_data[-i].append('')
	return price_data


def signal(price_data):
	period = 5
	try:
		previous_K = price_data[-period][6]
		previous_D = price_data[-period][7]
	except(IndexError):
		return 0.
	now_K = price_data[-1][6]
	now_D = price_data[-1][7]
	if previous_K and previous_D:
		try:
			if previous_K < previous_D:
				if now_K > now_D:
					return 1.
			if previous_K > previous_D:
				if now_K < now_D:
					return -1.
		except(TypeError):
			print('ERRROR!!!')
	return 0.
