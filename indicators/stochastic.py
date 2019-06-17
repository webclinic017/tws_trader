def fast_K_list(list_with_price_data, period, slow_average_period, fast_average_period):	# list_with_price_data must include: [date, open, close, high, low, volume]
	fast_K_list = []																		# list_with_price_data must include: [date, open, high, low, close, volume]
	for i in range(1, slow_average_period+fast_average_period-1):
		close_price = float(list_with_price_data[-i][4])
		lowest_price_for_period = float(list_with_price_data[-i][3])
		highest_price_for_period = float(list_with_price_data[-i][2])
		for row in list_with_price_data[-period-i:-i]:
			if float(row[3]) < lowest_price_for_period:
				lowest_price_for_period = float(row[3])
			if float(row[2]) > highest_price_for_period:
				highest_price_for_period = float(row[2])
		if highest_price_for_period != lowest_price_for_period:
			fast_K = (close_price - lowest_price_for_period) / (highest_price_for_period - lowest_price_for_period) * 100
		else:
			fast_K = 50
		fast_K_list.insert(0, round(fast_K, 2))
	return fast_K_list

def fast_average(fast_K_list, slow_average_period, fast_average_period):	# fast_average = SMA of the fast_K
	fast_average_list = []
	for i in range(1, slow_average_period+1):
		slow_k = sum(fast_K_list[-fast_average_period-i:-i]) / fast_average_period
		fast_average_list.insert(0, round(slow_k, 2))
	return fast_average_list

def slow_average(fast_average_list, slow_average_period):	# slow_average = SMA of the fast_average
	slow_average = sum(fast_average_list) / slow_average_period
	return round(slow_average, 2)

def main(prices, parameters=(26, 26, 9)):
	
	period = parameters[0]
	slow_average_period = parameters[1]
	fast_average_period = parameters[2]

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
			prices[-i].append(0)
			prices[-i].append(0)
	return prices

# In order to testing:
if __name__ == '__main__':
	import csv
	stock_ticker = 'EA'
	prices=[]
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			prices.append(row)	# list with entire our csv-file
	for row in main(prices)[-1:]:
		print(row)

