import csv

import matplotlib.pyplot as plt
import pandas as pd

def main(stock_ticker, duration, bar_size):
	min_max_prices=[]
	with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			min_max_prices.append(row[3])
			min_max_prices.append(row[4])
	min_max_prices = sorted(min_max_prices, key=float)	# how can I use it?
	min_price = int(float(min_max_prices[0]))
	max_price = int(float(min_max_prices[-1]))

	volume_level={}
	for x in range(min_price, max_price+1):
		volume_level[x] = 0
		with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'r', encoding='utf-8') as data_file:
			for row in csv.reader(data_file, delimiter=';'):
				if float(row[3]) >= x >= float(row[4]):
					volume_level[x] += int(row[5])

	a = pd.DataFrame.from_dict(volume_level, orient='index')
	# what can I do with this ?

	x_list=[]
	y_list=[]
	for x in a.iloc[:,0]:
		x_list.append(x)
	for y in a.index:
		y_list.append(y)

	plt.plot(x_list, y_list)
	plt.show()

if __name__ == '__main__':
	main('AMZN', '3 Y', '1 day')
