import pandas as pd

def fast_K_list_from_df(reviewing_prices, period, slow_average_period, fast_average_period):
	fast_K_list = []
	data_length = reviewing_prices.shape[0]
	for i in range(slow_average_period+fast_average_period-1):	
		close_price = reviewing_prices.iloc[data_length-1-i]['Close']
		lowest_price_for_period = reviewing_prices.iloc[data_length-period-i:data_length-i]['Low'].min()
		highest_price_for_period = reviewing_prices.iloc[data_length-period-i:data_length-i]['High'].max()
		if highest_price_for_period != lowest_price_for_period:
			fast_K = ((close_price - lowest_price_for_period) / (highest_price_for_period - lowest_price_for_period)) * 100
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


def price_data_to_DataFrame(price_data):
	import pandas as pd
	indexes = []
	open_p = []
	high_p = []
	low_p = []
	close_p = []
	volume = []
	for x in price_data:
		indexes.append(x[0])
		open_p.append(x[1])
		high_p.append(x[2])
		low_p.append(x[3])
		close_p.append(x[4])
		volume.append(x[5])
	d = {
		'Open': open_p,
		'High': high_p,
		'Low': low_p,
		'Close': close_p,
		'Volume': volume,
		}
	df = pd.DataFrame(data=d, index=indexes)
	df.index.name = 'Datetime'
	return df


def DataFrame_to_price_data(df):
	import pandas as pd
	price_data = [df.columns.tolist()] + df.reset_index().values.tolist()
	price_data.pop(0)
	return price_data


def update(price_data, parameters):
	period = parameters[0]
	slow_average_period = parameters[1]
	fast_average_period = parameters[2]
	price_data_df = price_data_to_DataFrame(price_data)
	for i in range(price_data_df.shape[0]):
		reviewing_prices = price_data_df.iloc[:-i]
		try:
			price_data[-i].pop(6)
			price_data[-i].pop(6)
		except:
			pass
		if reviewing_prices.shape[0] > period + slow_average_period + fast_average_period - 2:
			fast_Ks = fast_K_list_from_df(reviewing_prices, period, slow_average_period, fast_average_period)
			fastaverage = fast_average(fast_Ks, slow_average_period, fast_average_period)[-1]
			slowaverage = slow_average(fast_average(fast_Ks, slow_average_period, fast_average_period), slow_average_period)
			price_data[-i].append(fastaverage)
			price_data[-i].append(slowaverage)

		else:
			price_data[-i].append('')
			price_data[-i].append('')
	return price_data


def update_df(price_data_df, parameters):
	period = parameters[0]
	slow_average_period = parameters[1]
	fast_average_period = parameters[2]
	fastaverage_list = []
	slowaverage_list = []
	for i in range(1, price_data_df.shape[0]+1):
		if price_data_df.iloc[:-i].shape[0] > period + slow_average_period + fast_average_period - 3:
			fast_Ks = fast_K_list_from_df(price_data_df.iloc[:-i], period, slow_average_period, fast_average_period)
			fastaverage = fast_average(fast_Ks, slow_average_period, fast_average_period)[-1]
			slowaverage = slow_average(fast_average(fast_Ks, slow_average_period, fast_average_period), slow_average_period)
			fastaverage_list.append(fastaverage)
			slowaverage_list.append(slowaverage)
		else:
			fastaverage_list.append('')
			slowaverage_list.append('')
	price_data_df['K'] = pd.Series(reversed(fastaverage_list)).values
	price_data_df['D'] = pd.Series(reversed(slowaverage_list)).values
	return price_data_df


def signal(row,
				K_level_to_buy=None, D_level_to_buy=None, KD_difference_to_buy=None,
				K_level_to_sell=None, D_level_to_sell=None, KD_difference_to_sell=None
				):
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


def signal_df(row,
				K_level_to_buy=None, D_level_to_buy=None, KD_difference_to_buy=None,
				K_level_to_sell=None, D_level_to_sell=None, KD_difference_to_sell=None
				):
	K = row['K']
	D = row['D']
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

