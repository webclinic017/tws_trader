import logging

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_finance import candlestick_ohlc
from matplotlib.widgets import Cursor

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

from yahoo_historical import Fetcher


def find_zz_points(historical_data, ZZ_movement):
	dates_dict = {}
	count = 1
	for row in historical_data:
		dates_dict[row['Datetime']] = count
		count += 1
	# Zig-zag points
	zz_max_x = []
	zz_max_y = []
	zz_min_x = []
	zz_min_y = []
	x_max = None
	x_min = None
	y_max = None
	y_min = None
	support_points = []
	resistance_points = []
	# 1st iteration: finding first point after base point
	base_high = historical_data[0]['High']
	base_low = historical_data[0]['Low']
	for row in historical_data[1:]:
		high = row['High']
		low = row['Low']
		if high >= base_low * (1 + ZZ_movement):
			y_max = high
			x_max = dates_dict[row['Datetime']]
			break
		if low <= base_high * (1 - ZZ_movement):
			y_min = low
			x_min = dates_dict[row['Datetime']]
			break
		if low < base_low: base_low = low
		if high > base_high: base_high = high
	def update_max(x_max, y_max):
		x_min = None
		y_min = None
		for row in historical_data[x_max:]:
			y_base_point = y_max
			high = row['High']
			low = row['Low']
			if high > y_max:  # update max point
				y_max = high
				x_max = dates_dict[row['Datetime']]
			else:  # find new x_min
				if low <= y_base_point * (1 - ZZ_movement):  # Complete! We find MAX and can append it to our lists
					zz_max_x.append(x_max)
					zz_max_y.append(y_max)
					resistance_points.append({'Datetime': row['Datetime'], 'Price': y_max})
					# find new max and update min
					y_min = low
					x_min = dates_dict[row['Datetime']]
					break
		return (x_min, y_min)
	def update_min(x_min, y_min):
		x_max = None
		y_max = None
		for row in historical_data[x_min:]:
			y_base_point = y_min
			high = row['High']
			low = row['Low']
			if low < y_min:  # update min point
				x_min = dates_dict[row['Datetime']]
				y_min = low
			else:  # find new x_min
				if high >= y_base_point * (1 + ZZ_movement):  # Complete! We find MIN and can append it to our lists
					zz_min_x.append(x_min)
					zz_min_y.append(y_min)
					support_points.append({'Datetime': row['Datetime'], 'Price': y_min})
					x_max = dates_dict[row['Datetime']]
					y_max = high
					break
		return (x_max, y_max)
	if y_max:  # if 1st point after base is max
		y_min = True
		while y_min and y_max:
			if y_max:
				x_min, y_min = update_max(x_max, y_max)
			if y_min:
				x_max, y_max = update_min(x_min, y_min)
			# if x_min > 1295 or x_max > 1295:
			# 	print('ergre')
	if y_min:  # if 1st point after base is min
		y_max = True
		while y_min and y_max:
			if y_min:
				x_max, y_max = update_min(x_min, y_min)
			if y_max:
				x_min, y_min = update_max(x_max, y_max)
	return ((zz_max_x, zz_min_x), (zz_max_y, zz_min_y)), (support_points, resistance_points)



# This is for research:
def make_plot(historical_data, company, strategy_indicator):
	ZZ_movement = strategy_indicator['ZZ_movement'] / 100

	historical_data_as_list = []
	for i, row in historical_data.iterrows():
		historical_data_as_list.append({'Datetime': row['Date'],
		                                'Open': row['Open'],
		                                'High': row['High'],
		                                'Low': row['Low'],
		                                'Close': row['Close'],
		                                'Volume': row['Volume']
		                                })
	fig = plt.figure()
	ax_main = fig.add_subplot(1, 1, 1)
# Candlestick chart
	quotes = []
	volumes = []
	count = 1
	dates_dict = {}
	for row in historical_data_as_list:
		quotes.append((count, row['Open'], row['High'], row['Low'], row['Close']))
		volumes.append(row['Volume']/100000)
		dates_dict[row['Datetime']] = count
		count += 1
	candlestick_ohlc(ax_main, quotes, width=0.3, colorup='g', colordown='r')
# Draw volumes
	ax_main.bar(range(1, len(historical_data_as_list) + 1), volumes, zorder=-3)
	((zz_max_x, zz_min_x), (zz_max_y, zz_min_y)) = find_zz_points(historical_data_as_list, ZZ_movement)[0]
	ax_main.plot(zz_max_x, zz_max_y, 'kv', label='Zig-zag maximums', zorder=-1)  # zig_zag_max
	ax_main.plot(zz_min_x, zz_min_y, 'k^', label='Zig-zag minimums', zorder=-1)  # zig_zag_min
	for i in zz_max_y:
		ax_main.plot([0, len(historical_data_as_list)], [i, i], 'r:', linewidth=0.7, zorder=-2)
	for i in zz_min_y:
		ax_main.plot([0, len(historical_data_as_list)], [i, i], 'g:', linewidth=0.7, zorder=-2)
	ax_main.scatter([-10 for i in zz_max_y], zz_max_y, s=5, color='r')  # max allocation
	ax_main.scatter([-20 for i in zz_min_y], zz_min_y, s=5, color='g')  # min allocation
# Making beauty
	ax_main.set_ylabel('Price')
	ax_main.legend()
	title = f'{company}'
	plt.title(title)
	ax_main.xaxis.set_minor_locator(ticker.MultipleLocator(1))
	ax_main.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax_main.yaxis.set_minor_locator(ticker.MultipleLocator(10))
	ax_main.minorticks_on()
	plt.grid(which='major', linestyle='--')
	ax_main.grid(which='minor', color = 'gray', linestyle = ':')
	cursor = Cursor(ax_main, useblit=True, color='black', linewidth=0.5, ls='--')
	plt.show()



def update(price_data, strategy_indicator, historical_data, action):
	ZZ_movement = strategy_indicator['ZZ_movement'] / 100
	close_index = strategy_indicator['close_index'] / 100
	historical_data_as_list = []
	for i, row in historical_data.iterrows():
		historical_data_as_list.append({'Datetime': row['Date'],
		                                'Open': row['Open'],
		                                'High': row['High'],
		                                'Low': row['Low'],
		                                'Close': row['Close'],
		                                'Volume': row['Volume']
		                                })

	dates_dict = {}
	count = 1
	for row in historical_data_as_list:
		dates_dict[row['Datetime']] = count
		count += 1

	(support_points, resistance_points) = find_zz_points(historical_data_as_list, ZZ_movement)[1]

# Find absolute strength of points
	for i, x in enumerate(support_points):
		strength = 0
		x['Strength'] = strength
		for j in support_points[i+1:]:
			if j['Price'] >= x['Price']:
				strength += 1
				x['Strength'] = strength
			else:
				break
# Calculate relative strength of points
		try:
			x['Strength'] = int((strength / len(support_points[i + 1:])) * 100)
			x['Pre-Volume'] = sum((historical_data_as_list[dates_dict[x['Datetime']]]['Volume'],
								historical_data_as_list[dates_dict[x['Datetime']] - 1]['Volume'],
								historical_data_as_list[dates_dict[x['Datetime']] - 2]['Volume']))
		except(ZeroDivisionError):
			x['Strength'] = 100
			x['Pre-Volume'] = sum((historical_data_as_list[dates_dict[x['Datetime']]]['Volume'],
								historical_data_as_list[dates_dict[x['Datetime']] - 1]['Volume'],
								historical_data_as_list[dates_dict[x['Datetime']] - 2]['Volume']))

	# for x in support_points:
	# 	print(x)







	# fig = plt.figure()
	# ax_main = fig.add_subplot(1, 1, 1)
	# ax_main.scatter([x['Pre-Volume'] for x in support_points], [x['Strength'] for x in support_points], s=5)  # min allocation
	# plt.grid(which='major', linestyle='--')
	# ax_main.grid(which='minor', color = 'gray', linestyle = ':')
	# plt.show()






	# price_data[0]['RS signal'] = 0.
	# i = 1
	# for row in price_data[1:]:
	# 	(zz_max_y_middle, zz_min_y_middle) = find_zz_points(price_data[:i+1], ZZ_movement)[1]
	# 	row['RS signal'] = 0.
	# 	price = price_data[i - 1]['Close']
	# 	high = price_data[i - 1]['High']
	# 	low = price_data[i - 1]['Low']
	# 	try:
	# 		for j in range(1,4):
	# 			# if zz_min_y_middle[-j] * (1 - close_index) <= low <= zz_min_y_middle[-j] * (1 + close_index):
	# 			# 	row['RS signal'] = 1.
	# 			if zz_max_y_middle[-j] * (1 - close_index) <= high <= zz_max_y_middle[-j] * (1 + close_index):
	# 				row['RS signal'] = -1.
	# 			# if zz_min_y_middle[-j] * (1 - close_index) <= low <= zz_min_y_middle[-j] * (1 + close_index):
	# 			# 	row['RS signal'] = 1.
	# 	except(IndexError):
	# 		pass
	# 	i += 1







	def find_clusters_in(iterable, close_index):
		clusters = []
		prev = None
		group = []
		for item in sorted(iterable):
			if not prev or (item - prev) / item <= close_index:
				group.append(item)
			else:
				if len(group) >= 3:
					clusters.append(group)
				group = [item]
			prev = item
		return clusters

	# resistance_clusters = find_clusters_in(zz_max_y_middle, close_index)
	# support_clusters = find_clusters_in(zz_min_y_middle, close_index)

	# for i, x in enumerate(resistance_clusters):
	# 	print(i, x)
	# print('\n')
	# for i, x in enumerate(support_clusters):
	# 	print(i, x)

# IDEAS:
#   - coomon levels. Price above - limit buy, price below - limit sell
#   - NOW: resistance + support (U - universal)

	price_data[0][f'RS signal {action}'] = 0.
	i = 1
	for row in price_data[1:]:
		row[f'RS signal {action}'] = 0.
	# 	support_signal = None
	# 	resistance_signal = None
	# 	price = price_data[i - 1]['Close']
	# 	high = price_data[i - 1]['High']
	# 	low = price_data[i - 1]['Low']
	# 	# Check if price in support zone:
	# 	for support_level in support_clusters:
	# 		if support_level[0] * (1 - close_index) <= low <= support_level[-1] * (1 + close_index):
	# 			support_signal = (1., support_level)
	# 	# Check if price in resistance zone:
	# 	for resistance_level in resistance_clusters:
	# 		if resistance_level[0] * (1 - close_index) <= high <= resistance_level[-1] * (1 + close_index):
	# 			resistance_signal = (-1., resistance_level)
	# 	else:
	# 		if support_signal:
	# 			row['RS signal'] = 1.
	# 		if resistance_signal:
	# 			row['RS signal'] = -1.
	# 	i += 1


		# try:
		# 	diff_to_the_closest_min = min(((row['Close'] - x) for x in zz_min_y_middle if x < row['Close'])) / row['Close']
		# 	diff_to_the_closest_max = min(((x - row['Close']) for x in zz_max_y_middle if x > row['Close'])) / row['Close']
		# except(ValueError):
		# 	row['RS signal'] = 0.
		# 	diff_to_the_closest_min = close_index
		# 	diff_to_the_closest_max = close_index
		#
		# if diff_to_the_closest_min < close_index or diff_to_the_closest_max < close_index:
		# 	if diff_to_the_closest_max > diff_to_the_closest_min:
		# 		row['RS signal'] = 1.
		# 	elif diff_to_the_closest_max < diff_to_the_closest_min:
		# 		row['RS signal'] = -1.
		# 	else:
		# 		row['RS signal'] = 0.
		# else:
		# 	row['RS signal'] = 0.



	return price_data


def signal(price_data, *args):
	action = args[1]
	return price_data[-1][f'RS signal {action}']


if __name__ == '__main__':
	company = 'TSLA'
	bar_size = '30 mins'


	price_data = []
	import ast
	import csv
	def get_price_data(company, bar_size):
		price_data = []
		with open(f'../historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
			for row in csv.DictReader(data_file, delimiter=';'):
				for key, value in row.items():
					if key != 'Datetime':
						row[key] = ast.literal_eval(value)
				price_data.append(row)
		return price_data
	price_data = get_price_data(company, bar_size)
	# for row in price_data[100:105]:
	# 	print(row)
	# print('\n')


	now_date = [2019,8,25]
	historical_data = Fetcher(company, [2019,1,14], now_date).getHistorical()
	historical_data = historical_data.loc[:, historical_data.columns != 'Adj Close']

	print('...')
	strategy_indicator = {'ZZ_movement': 5, 'close_index': 4}

	price_data = update(price_data, strategy_indicator, historical_data)
	# for row in price_data[100:105]:
	# 	print(row)
	#
	# print('...')

	def volume_profile(historical_data):
		the_highest_price = historical_data['High'].max()
		the_lowest_price = historical_data['Low'].min()
		step = (the_highest_price - the_lowest_price) / 100
		x_list = []  # volumes
		y_list = []  # prices
		price = the_lowest_price
		while price <= the_highest_price:
			y_list.append(price)
			volume_sum = 0
			for i in range(historical_data.shape[0]):
				if historical_data.loc[i, 'High'] >= price >= historical_data.loc[i, 'Low']:
					volume_sum += historical_data.loc[i, 'Volume']
			x_list.append(volume_sum / 100000)
			price += step
		volume_profile = (x_list, y_list)
		return volume_profile

	# volume_profile = volume_profile(historical_data)
	make_plot(historical_data, company, strategy_indicator)












