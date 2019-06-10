import csv

def get_data(stock_ticker, path):
	list_with_price_data=[]
	with open(f'{path}{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)	# list with entire our csv-file
	return list_with_price_data

def fast_K_list(list_with_price_data, period, slow_average_period, fast_average_period):	# list_with_price_data must include: [date, open, close, high, low, volume]
	fast_K_list = []
	for i in range(1, slow_average_period+fast_average_period-1):
		close_price = float(list_with_price_data[-i][2])
		lowest_price_for_period = float(list_with_price_data[-i][4])
		highest_price_for_period = float(list_with_price_data[-i][3])
		for row in list_with_price_data[-period-i:-i]:
			if float(row[4]) < lowest_price_for_period:
				lowest_price_for_period = float(row[4])
			if float(row[3]) > highest_price_for_period:
				highest_price_for_period = float(row[3])
		fast_K = (close_price - lowest_price_for_period) / (highest_price_for_period - lowest_price_for_period) * 100
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

def main(stock_ticker, path_to_data='historical_data/short_term/', period=26, slow_average_period=26, fast_average_period=9):
	try:
		prices = get_data(stock_ticker, path_to_data)
		if len(prices) >= period + slow_average_period + fast_average_period - 2:
			fast_Ks = fast_K_list(prices, period, slow_average_period, fast_average_period)
			fastaverage = fast_average(fast_Ks, slow_average_period, fast_average_period)[-1]
			slowaverage = slow_average(fast_average(fast_Ks, slow_average_period, fast_average_period), slow_average_period)
			return fastaverage, slowaverage
		else:
			return 'ERROR: not enough price data for stochastic with this periods'
	except(FileNotFoundError):
		return 'ERROR: File with data did not found'

# In order to testing:
if __name__ == '__main__':
	print(main('GE', 'historical_data/short_term/', 26, 26, 9))
