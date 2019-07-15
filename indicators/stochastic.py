def fast_K_list(list_with_price_data, period, slow_average_period, fast_average_period):	# list_with_price_data must include: [date, open, close, high, low, volume]
	fast_K_list = []
	data_length = len(list_with_price_data)																		# list_with_price_data must include: [date, open, high, low, close, volume]
	for i in range(0, slow_average_period+fast_average_period-1):	
		close_price = float(list_with_price_data[data_length-1-i][4])	
		lows_prices = tuple(float(x[3]) for x in list_with_price_data[data_length-period-i:data_length-i])
		highs_prices = tuple(float(x[2]) for x in list_with_price_data[data_length-period-i:data_length-i])		
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


def delete_columns_with_indicator(prices): 	# m.b. with pandas.DataFrame it would be easier ?!
	i = 0	# column number
	for title in range(0,len(prices[0])):
		title = prices[0][i]
		if '%' in title:
			x = 0	# row number
			for row in prices:
				try:
					row.remove(row[i])
				except(IndexError):	# if new prices was added without indicator's values
					continue
			i -= 1
		i += 1
	return prices


def main(prices, parameters=(26, 26, 9)):
	
	period = parameters[0]
	slow_average_period = parameters[1]
	fast_average_period = parameters[2]

	prices = delete_columns_with_indicator(prices)

	prices[0].append(f'%K({period},{slow_average_period},{fast_average_period})')
	prices[0].append(f'%D({period},{slow_average_period},{fast_average_period})')

	for i in range(1,len(prices)):
		reviewing_prices = prices[:-i]
		if len(reviewing_prices) > period + slow_average_period + fast_average_period - 2:
			fast_Ks = fast_K_list(reviewing_prices, period, slow_average_period, fast_average_period)
			fastaverage = fast_average(fast_Ks, slow_average_period, fast_average_period)[-1]
			slowaverage = slow_average(fast_average(fast_Ks, slow_average_period, fast_average_period), slow_average_period)
			prices[-i].append(fastaverage)
			prices[-i].append(slowaverage)
		else:
			prices[-i].append('')
			prices[-i].append('')
	return prices


def signal(row, 
				K_level_to_buy=None, D_level_to_buy=None, KD_difference_to_buy=None,
				K_level_to_sell=None, D_level_to_sell=None, KD_difference_to_sell=None
				):
	date = row[0]
	open_price = float(row[1])
	high_price = float(row[2])
	low_price = float(row[3])
	close_price = float(row[4])
	volume = int(row[5])
	if row[6] != '' and row[7] != '':
		K = float(row[6])
		D = float(row[7])
	else:
		K = ''
		D = ''

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

