# ВОПРОС: Как лучше определить зубцы на графике? провалы

import csv

import matplotlib.pyplot as plt
import pandas as pd

def main(stock_ticker, duration, bar_size):
	min_max_prices=[]
	with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			min_max_prices.append(row[3])
			min_max_prices.append(row[4])
	min_max_prices = sorted(min_max_prices, key=float)

	volume_level={}
	for x in min_max_prices:
		volume_level[x] = 0
		with open(f'historical_data/{stock_ticker} for {duration} by {bar_size}.csv', 'r', encoding='utf-8') as data_file:
			for row in csv.reader(data_file, delimiter=';'):
				if float(row[3]) >= float(x) >= float(row[4]):
					volume_level[x] += int(row[5])

	a = pd.DataFrame.from_dict(volume_level, orient='index')
	# what can I do with this ?

	x_list=[]	# volumes
	y_list=[]	# prices
	for x in a.iloc[:,0]:
		x_list.append(x)
	for y in a.index:
		y_list.append(y)

	print(f"Для {stock_ticker} максимальные объемы сделок пришлись на цену ${y_list[x_list.index(max(x_list))]}")
	total_volumes = 0
	for z in range(0, len(y_list)):
		total_volumes += float(x_list[z])*float(y_list[z])
	print(f"Для {stock_ticker} средняя цена сделки за рассматриваемый париод составила ${round(total_volumes/sum(x_list),2)}")

	plt.plot(x_list, y_list)
	plt.show()

# In case of testing:
if __name__ == '__main__':
	main('AAPL', '1 Y', '10 mins')
