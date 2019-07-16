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
		fast_K_list.insert(0, fast_K)

	return tuple(fast_K_list)


def fast_average(fast_K_list, slow_average_period, fast_average_period):	# fast_average = SMA of the fast_K
	fast_average_list = []
	for i in range(1, slow_average_period+1):
		slow_k = sum(fast_K_list[-fast_average_period-i:-i]) / fast_average_period
		fast_average_list.insert(0, slow_k)
	return tuple(fast_average_list)


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


def signal(row, 
				K_level_to_buy=None, D_level_to_buy=None, KD_difference_to_buy=None,
				K_level_to_sell=None, D_level_to_sell=None, KD_difference_to_sell=None
				):
	date = row[0]
	open_price = row[1]
	high_price = row[2]
	low_price = row[3]
	close_price = row[4]
	volume = row[5]
	K = row[6]
	D = row[7]
	if K == '' or D == '':
		return 0
	else:
	# K_level_to_buy only matters
		if K_level_to_buy != None and D_level_to_buy == None and KD_difference_to_buy == None:
			if K_level_to_buy[0] <= K <= K_level_to_buy[1]:
				return 'buy'
	# D_level_to_buy only matters
		if K_level_to_buy == None and D_level_to_buy != None and KD_difference_to_buy == None:
			if D_level_to_buy[0] <= D <= D_level_to_buy[1]:
				return 'buy'
	# KD_difference_to_buy only matters
		if K_level_to_buy == None and D_level_to_buy == None and KD_difference_to_buy != None:
			if KD_difference_to_buy == 0:	# needs to K=D
				if -2.0 < (K - D) < 2.0:
					return 'buy'
			if KD_difference_to_buy == -1:	# needs to K<D
				if (K - D) < -2.0:
					return 'buy'
			if KD_difference_to_buy == 1:	# needs to K>D
				if (K - D) > 2.0:
					return 'buy'	
	# K_level_to_buy and D_level_to_buy only matters
		if K_level_to_buy != None and D_level_to_buy != None and KD_difference_to_buy == None:
			if K_level_to_buy[0] <= K <= K_level_to_buy[1]:
				if D_level_to_buy[0] <= D <= D_level_to_buy[1]:
					return 'buy'
	# K_level_to_buy and KD_difference_to_buy only matters
		if K_level_to_buy != None and D_level_to_buy == None and KD_difference_to_buy != None:
			if K_level_to_buy[0] <= K <= K_level_to_buy[1]:
				if KD_difference_to_buy == 0:	# needs to K=D
					if -2.0 < (K - D) < 2.0:
						return 'buy'
				if KD_difference_to_buy == -1:	# needs to K<D
					if (K - D) < -2.0:
						return 'buy'
				if KD_difference_to_buy == 1:	# needs to K>D
					if (K - D) > 2.0:
						return 'buy'
	# D_level_to_buy and KD_difference_to_buy only matters
		if K_level_to_buy == None and D_level_to_buy != None and KD_difference_to_buy != None:
			if D_level_to_buy[0] <= D <= D_level_to_buy[1]:
				if KD_difference_to_buy == 0:	# needs to K=D
					if -2.0 < (K - D) < 2.0:
						return 'buy'
				if KD_difference_to_buy == -1:	# needs to K<D
					if (K - D) < -2.0:
						return 'buy'
				if KD_difference_to_buy == 1:	# needs to K>D
					if (K - D) > 2.0:
						return 'buy'
	# all parameters to buy matters
		if K_level_to_buy != None and D_level_to_buy != None and KD_difference_to_buy != None:
			if K_level_to_buy[0] <= K <= K_level_to_buy[1]:
				if D_level_to_buy[0] <= D <= D_level_to_buy[1]:
					if KD_difference_to_buy == 0:	# needs to K=D
						if -2.0 < (K - D) < 2.0:
							return 'buy'
					if KD_difference_to_buy == -1:	# needs to K<D
						if (K - D) < -2.0:
							return 'buy'
					if KD_difference_to_buy == 1:	# needs to K>D
						if (K - D) > 2.0:
							return 'buy'
	# no one matters:
		if K_level_to_buy == None and D_level_to_buy == None and KD_difference_to_buy == None:
			return 0

	# K_level_to_sell only matters
		if K_level_to_sell != None and D_level_to_sell == None and KD_difference_to_sell == None:
			if K_level_to_sell[0] <= K <= K_level_to_sell[1]:
				return 'sell'
	# D_level_to_sell only matters
		if K_level_to_sell == None and D_level_to_sell != None and KD_difference_to_sell == None:
			if D_level_to_sell[0] <= D <= D_level_to_sell[1]:
				return 'sell'
	# KD_difference_to_sell only matters
		if K_level_to_sell == None and D_level_to_sell == None and KD_difference_to_sell != None:
			if KD_difference_to_sell == 0:	# needs to K=D
				if -2.0 < (K - D) < 2.0:
					return 'sell'
			if KD_difference_to_sell == -1:	# needs to K<D
				if (K - D) < -2.0:
					return 'sell'
			if KD_difference_to_sell == 1:	# needs to K>D
				if (K - D) > 2.0:
					return 'sell'
	# K_level_to_sell and D_level_to_sell only matters
		if K_level_to_sell != None and D_level_to_sell != None and KD_difference_to_sell == None:
			if K_level_to_sell[0] <= K <= K_level_to_sell[1]:
				if D_level_to_sell[0] <= D <= D_level_to_sell[1]:
					return 'sell'
	# K_level_to_sell and KD_difference_to_sell only matters
		if K_level_to_sell != None and D_level_to_sell == None and KD_difference_to_sell != None:
			if K_level_to_sell[0] <= K <= K_level_to_sell[1]:
				if KD_difference_to_sell == 0:	# needs to K=D
					if -2.0 < (K - D) < 2.0:
						return 'sell'
				if KD_difference_to_sell == -1:	# needs to K<D
					if (K - D) < -2.0:
						return 'sell'
				if KD_difference_to_sell == 1:	# needs to K>D
					if (K - D) > 2.0:
						return 'sell'
	# D_level_to_sell and KD_difference_to_sell only matters
		if K_level_to_sell == None and D_level_to_sell != None and KD_difference_to_sell != None:
			if D_level_to_sell[0] <= D <= D_level_to_sell[1]:
				if KD_difference_to_sell == 0:	# needs to K=D
					if -2.0 < (K - D) < 2.0:
						return 'sell'
				if KD_difference_to_sell == -1:	# needs to K<D
					if (K - D) < -2.0:
						return 'sell'
				if KD_difference_to_sell == 1:	# needs to K>D
					if (K - D) > 2.0:
						return 'sell'
	# all parameters matters
		if K_level_to_sell != None and D_level_to_sell != None and KD_difference_to_sell != None:
			if K_level_to_sell[0] <= K <= K_level_to_sell[1]:
				if D_level_to_sell[0] <= D <= D_level_to_sell[1]:
					if KD_difference_to_sell == 0:	# needs to K=D
						if -2.0 < (K - D) < 2.0:
							return 'sell'
					if KD_difference_to_sell == -1:	# needs to K<D
						if (K - D) < -2.0:
							return 'sell'
					if KD_difference_to_sell == 1:	# needs to K>D
						if (K - D) > 2.0:
							return 'sell'
	# no one matters:
		if K_level_to_sell == None and D_level_to_sell == None and KD_difference_to_sell == None:
			return 0

	return 0

