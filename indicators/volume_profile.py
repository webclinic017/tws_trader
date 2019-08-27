import time

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc



def make_plot(volume_profile):
	fig = plt.figure()
	ax_volumes = fig.add_subplot(1, 1, 1)
	ax_volumes.plot(volume_profile[0], volume_profile[1], linewidth=0.7)
	ax_volumes.grid(True)
	ax_volumes.set_ylim(0, max(volume_profile[1]) * 1.1)
	ax_volumes.set_xlim(0, max(volume_profile[0]) * 1.2)
	plt.show()


def update(price_data, locator, historical_data):
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

	last_day = None
	for row in price_data:
		price_now = row['Close']

		# new_last_day = row[0].replace('-', '')[:4] # one update in a month
		# if new_last_day != last_day:
		# 	last_day = new_last_day
		# 	print(last_day)
		# 	data_for_vol = data.set_index('Date').loc[:last_day].reset_index()
		# 	the_highest_price = data_for_vol['High'].max()
		# 	the_lowest_price = data_for_vol['Low'].min()
		# 	step = (the_highest_price - the_lowest_price) / 100
		# 	x_list = []  # volumes
		# 	y_list = []  # prices
		# 	price = the_lowest_price
		# 	while price <= the_highest_price:
		# 		y_list.append(price)
		# 		volume_sum = 0
		# 		for i in range(data_for_vol.shape[0]):
		# 			if data_for_vol.loc[i, 'High'] >= price >= data_for_vol.loc[i, 'Low']:
		# 				volume_sum += data_for_vol.loc[i, 'Volume']
		# 		x_list.append(volume_sum / 100000)
		# 		price += step
		# 	volume_profile = (x_list, y_list)
			# # make_plot(volume_profile)

		if locator == None:
			row['VP signal'] = None
		else:
			price_difference = 999999999
			closest_price_index = None
			for i, x in enumerate(volume_profile[1]):
				if abs(x-price_now) < price_difference:
					price_difference = abs(x-price_now)
					closest_price_index = i
			volume_profile_radius = min([len(volume_profile[1][:closest_price_index]),
												len(volume_profile[1][closest_price_index:])
												])
			if locator / 2 < volume_profile_radius:
				volume_profile_radius = int(locator / 2)
			volume_below = []
			volume_above = []
			if price_now < volume_profile[1][closest_price_index]:
				start = closest_price_index - volume_profile_radius
				end = closest_price_index + volume_profile_radius
			if price_now > volume_profile[1][closest_price_index]:
				start = closest_price_index - volume_profile_radius + 1
				end = closest_price_index + volume_profile_radius + 1
			for i, val in enumerate(volume_profile[1][start:end]):
				if price_now >= val:
					volume_below.append(volume_profile[0][i + start])
				if price_now < val:
					volume_above.append(volume_profile[0][i + start])
			sum_volume_below = sum(volume_below)
			sum_volume_above = sum(volume_above)
			if volume_profile_radius > 0:
				if sum_volume_below <= sum_volume_above:
					row['VP signal'] = 1.
				if sum_volume_below > sum_volume_above:
					row['VP signal'] = -1.
			else:
				row['VP signal'] = 0.
	return price_data


def signal(price_data, *args):
	return price_data[-1]['VP signal']


if __name__ == '__main__':
	company = 'TSLA'
	bar_size = '30 mins'
	strategy_indicator = {'locator': 14}


	def get_price_data(company, bar_size):
		import csv
		price_data = []
		with open(f'../historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
			for row in csv.reader(data_file, delimiter=';'):
				if row[0] != 'Datetime':
					formated_row = []
					formated_row.append(row[0])
					formated_row.append(float(row[1]))
					formated_row.append(float(row[2]))
					formated_row.append(float(row[3]))
					formated_row.append(float(row[4]))
					formated_row.append(int(row[5]))
					price_data.append(formated_row)
		return price_data


	price_data = get_price_data(company, bar_size)
	price_data = update(price_data, strategy_indicator['locator'], company)
	for row in price_data[:5]:
		print(row)


# NOW: от текущей цены выше и ниже на locator цен проверяем суммы этих объемов. Цена будет стремиться туда, где совокупный объем выше.












































