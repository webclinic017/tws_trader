# ВОПРОС: Как лучше определить локальный минимум?

import csv

#import matplotlib.pyplot as plt
import pandas as pd

def max_volume_level(stock_ticker, path):
	min_max_prices=[]
	with open(f'{path}{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			min_max_prices.append(row[3])
			min_max_prices.append(row[4])
	min_max_prices = sorted(min_max_prices, key=float)

	volume_level={}
	for x in min_max_prices:
		volume_level[x] = 0
		with open(f'{path}{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
			for row in csv.reader(data_file, delimiter=';'):
				if float(row[3]) >= float(x) >= float(row[4]):
					volume_level[x] += int(round(float(row[5]), 0))

	a = pd.DataFrame.from_dict(volume_level, orient='index')
	# what can I do with this ?

	x_list=[]	# volumes
	y_list=[]	# prices
	for x in a.iloc[:,0]:
		x_list.append(x)
	for y in a.index:
		y_list.append(y)

	return y_list[x_list.index(max(x_list))], max(x_list)
# 	total_volumes = 0
# 	for z in range(0, len(y_list)):
# 		total_volumes += float(x_list[z])*float(y_list[z])
# #	print(f"Для {stock_ticker} средняя цена сделки за рассматриваемый париод составила ${round(total_volumes/sum(x_list),2)}")

#	plt.plot(x_list, y_list)
#	plt.show()






	

	# volume_differents=[]
	# for z in range(1, len(x_list)):
	# 	vol_dif = x_list[z]-x_list[z-1]
	# 	volume_differents.append(abs(vol_dif))
	# print(y_list[volume_differents.index(max(volume_differents))])

	# for z in volume_level.items():
	# 	print(z)

# In case of testing:
if __name__ == '__main__':
	stock_ticker = 'CAKE'

	with open(f'historical_data/long_term/!Companies.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			for stock_ticker in row:
				print(stock_ticker, max_volume_level(stock_ticker, 'historical_data/long_term/')[0], round(max_volume_level(stock_ticker, 'historical_data/long_term/')[1]/36))
				print(stock_ticker, max_volume_level(stock_ticker, 'historical_data/middle_term/')[0], round(max_volume_level(stock_ticker, 'historical_data/middle_term/')[1]/6))
				print(stock_ticker, max_volume_level(stock_ticker, 'historical_data/short_term/')[0], max_volume_level(stock_ticker, 'historical_data/short_term/')[1])
	#			print(f"{path} Для {stock_ticker} максимальные объемы сделок пришлись на цену ${y_list[x_list.index(max(x_list))]}")


# Варианты стратегий:
# 1) цена близко к абсолютному максимуму: покупаем в направлении к абсолютному максимуму
# 1.1) в заданных различных таймфреймах абсолютный макс сливается в одну линию

# 2) от локального минимума в сторону локального (абсолютного) максимума (нужно определить диапазон поиска локального минимума)

# Стандартные:
# Стохастик или ROC
















