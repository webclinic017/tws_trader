# ВОПРОС: Как лучше определить локальный минимум?
import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc
from yahoo_historical import Fetcher


def make_plots(quotes, volumes, new_volumes, now, count):
	fig = plt.figure()
	ax_main = fig.add_subplot(1, 2, 1)
	candlestick_ohlc(ax_main, quotes, width=0.3, colorup='g', colordown='r')
	ax_main.plot(now[0], now[1], 'k<', label='sell trades')	# sell
	ax_main.grid(True)
	ax_main.set_ylim(0,max(volumes[1])*1.1)

	ax_volumes = fig.add_subplot(1, 2, 2)
	ax_volumes.plot(new_volumes[0], new_volumes[1], color='green', linewidth=0.7)
	ax_volumes.plot(volumes[0], volumes[1], linewidth=0.7)
	ax_volumes.plot([0], now[1], 'k>', label='sell trades')
	ax_volumes.grid(True)
	ax_volumes.set_ylim(0,max(volumes[1])*1.1)
	ax_volumes.set_xlim(0,max(volumes[0])*1.2)
	plt.show()
	# plt.savefig(f'volume_plots/{count}.png')

	plt.clf()
	plt.cla()
	plt.close(fig)


def update_volume_profile(list_with_price_data, step, historical_volume_profile):
	the_lowest_price = min(historical_volume_profile[1])
	the_highest_price = 0
	for row in list_with_price_data[1:]:
		if float(row[2]) > the_highest_price:
			the_highest_price = float(row[2])
	x_list=[]	# volumes
	y_list=[]	# prices
	price = the_lowest_price
	while price <= the_highest_price:
		y_list.append(price)
		volume_sum = 0
		for row in list_with_price_data:
			if row[2] != 'high' and float(row[2]) >= price >= float(row[3]):
				volume_sum += int(round(float(row[5]), 0))
		x_list.append(volume_sum/1000)
		price += step
	new_x_list=[]
	for i, val in enumerate(historical_volume_profile[1]):
		if val in y_list:
			new_volume = historical_volume_profile[0][i] + x_list[y_list.index(val)]
			new_x_list.append(new_volume)
		else:
			new_x_list.append(historical_volume_profile[0][i])
		# to see apart what added to volume profile
		# if val in y_list:
		# 	new_x_list.append(x_list[y_list.index(val)]*10)
		# else:
		# 	new_x_list.append(0)


	# how much in % has volume profile changed
	# new_added_list = []
	# for i in range(len(new_x_list)):
	# 	try:
	# 		new_added = ((new_x_list[i] - volumes[0][i]) / volumes[0][i]) * 1000
	# 		new_added_list.append(new_added)
	# 		print(volumes[1][i], ':', round(new_added, 1), '%')
	# 	except:
	# 		new_added_list.append(0)
	return (new_x_list, historical_volume_profile[1])


def historical_volumes(end_date):
	req = Fetcher("TSLA", [2000,1,1], end_date)
	data = req.getHistorical()
	the_highest_price = data['High'].max()
	the_lowest_price = data['Low'].min()
	step = (the_highest_price - the_lowest_price) / 100
	x_list=[]	# volumes
	y_list=[]	# prices

	price = the_lowest_price
	while price <= the_highest_price:
		y_list.append(price)
		volume_sum = 0
		for i in range(data.shape[0]):
			if data.loc[i,'High'] >= price >= data.loc[i,'Low']:
				volume_sum += data.loc[i,'Volume']
		x_list.append(volume_sum/127000)
		price += step
	return (x_list, y_list), step


def signal(price_now, historical_volume_profile, volume_profile_locator):
	price_difference = 999999999
	closest_price_index = None
	for i, x in enumerate(historical_volume_profile[1]):
		if abs(x-price_now) < price_difference:
			price_difference = abs(x-price_now)
			closest_price_index = i
	volume_profile_radius = min([len(historical_volume_profile[1][:closest_price_index]), 
										len(historical_volume_profile[1][closest_price_index:])
										])
	if volume_profile_locator / 2 < volume_profile_radius:
		volume_profile_radius = int(volume_profile_locator / 2)
	# print(volume_profile_radius)
	# print(price_now)
	# print(closest_price_index)
	# print(historical_volume_profile[1][closest_price_index], historical_volume_profile[0][closest_price_index])
	max_volume_below = 0
	max_volume_above = 0
	start = closest_price_index - volume_profile_radius
	end = closest_price_index + volume_profile_radius + 1
	for i, val in enumerate(historical_volume_profile[1][start:end]):
		if price_now >= val and historical_volume_profile[0][i+start] > max_volume_below:
			max_volume_below = historical_volume_profile[0][i+start]
		if price_now <= val and historical_volume_profile[0][i+start] > max_volume_above:
			max_volume_above = historical_volume_profile[0][i+start]
	# 	print([i, val, historical_volume_profile[0][i+start], max_volume_above, max_volume_below])
	# 	print(start, end)
	# print(max_volume_above)
	# print(price_now)
	# print(max_volume_below)
	if max_volume_below <= max_volume_above and volume_profile_radius > 0:
		# print('buy')
		return 'buy'
	if max_volume_below > max_volume_above and volume_profile_radius > 0:
		# print('sell')
		return 'sell'
	else:
		return 0


def buy_signal(last_row, historical_volume_profile, volume_profile_locator=None):
	price_now = float(last_row[4])
	if volume_profile_locator == None:
		return 'buy'
	else:
		return signal(price_now, historical_volume_profile, volume_profile_locator)


def sell_signal(last_row, historical_volume_profile, volume_profile_locator=None):
	price_now = float(last_row[4])
	if volume_profile_locator == None:
		return 'sell'
	else:
		return signal(price_now, historical_volume_profile, volume_profile_locator)


# In case of testing:
def main(company, list_with_price_data):
	
	first_date = list_with_price_data[1][0]
	end_date = [int(first_date[:4]), int(first_date[4:6]), int(first_date[6:8])]
	historical_volume_profile, step = historical_volumes(end_date)

	for count in range(1310,1311):		#	1,len(list_with_price_data),10):
		new_volumes = update_volume_profile(list_with_price_data[1:count+1], step, historical_volume_profile)
		price_now = float(list_with_price_data[count][4])
		now = ([count+20],[price_now])
		quotes = []
		count1 = 1
		for row in list_with_price_data[1:]:
			quotes.append((count1, float(row[1]), float(row[2]), float(row[3]), float(row[4])))
			count1 += 1
		volume_profile_locator = 10
		signal(price_now, historical_volume_profile, volume_profile_locator)


		make_plots(quotes, historical_volume_profile, new_volumes, now, count)

if __name__ == '__main__':
	company = 'TSLA'
	bar_size = '30 mins'
	list_with_price_data=[]
	import csv
	with open(f'./historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)
	main(company, list_with_price_data)


# Варианты стратегий:

# 2) от локального минимума в сторону локального (абсолютного) максимума (нужно определить диапазон поиска локального минимума)

# 3) от текущей цены выше и ниже на N цен проверяем максимумы этих объемов. Цена будет стремиться туда, где совокупный объем выше.


# 4) если между двумя ценами разница суммарных объемов не превышает параметр N, то значит это "площадка справедливой цены".
# цена задерживается на этом уровне













