import csv

import matplotlib.pyplot as plt
from mpl_finance import candlestick_ohlc


def make_plots(quotes, points):
	fig = plt.figure()
	ax_main = fig.add_subplot(1, 1, 1)
	candlestick_ohlc(ax_main, quotes, width=0.3, colorup='g', colordown='r')
	ax_main.plot(points[0], points[1], 'k^')
	ax_main.grid(True)

	# ax_volumes = fig.add_subplot(1, 2, 2)
	# ax_volumes.plot(new_volumes[0], new_volumes[1], color='green', linewidth=0.7)
	# ax_volumes.plot(volumes[0], volumes[1], linewidth=0.7)
	# ax_volumes.plot([0], now[1], 'k>', label='sell trades')
	# ax_volumes.grid(True)
	# ax_volumes.set_ylim(0,max(volumes[1])*1.1)
	# ax_volumes.set_xlim(0,max(volumes[0])*1.2)
	plt.show()

	plt.clf()
	plt.cla()
	plt.close(fig)


def get_price_data(company, bar_size):
	price_data=[]
	with open(f'./historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			if row[0] != 'date':
				formated_row = []
				formated_row.append(row[0])
				formated_row.append(float(row[1]))
				formated_row.append(float(row[2]))
				formated_row.append(float(row[3]))
				formated_row.append(float(row[4]))
				formated_row.append(int(row[5]))
				if row[6] != '' and row[7] != '':
					formated_row.append(round(float(row[6]), 1))
					formated_row.append(round(float(row[7]), 1))
				else:
					formated_row.append('')
					formated_row.append('')
				price_data.append(formated_row)
	return price_data


def hammer_candlestick(price_data):
	if len(price_data) >= 2:
		previous_row = price_data[-2]
		now_row = price_data[-1]
		prev_open = previous_row[1]
		prev_close = previous_row[4]
		now_open = now_row[1]
		now_high = now_row[2]
		now_low = now_row[3]
		now_close = now_row[4]
		if prev_close < prev_open:	# and prev_close > now_close:
			# green hammer
			if now_close > now_open:
				now_body = now_close - now_open
				now_shadow_below = now_open - now_low
				now_shadow_above = now_high - now_close
				if (now_shadow_below / now_body) > 2.5 and (now_shadow_above == 0 or (now_body / now_shadow_above) > 2):
					return True
			# red hammer
			if now_close < now_open:
				now_body = now_open - now_close
				now_shadow_below = now_close - now_low
				now_shadow_above = now_high - now_open
				if (now_shadow_below / now_body) > 2.5 and (now_shadow_above == 0 or (now_body / now_shadow_above) > 2):
					return True
	return False


def hanging_man_candlestick(price_data):
	if len(price_data) >= 2:
		previous_row = price_data[-2]
		now_row = price_data[-1]
		prev_open = previous_row[1]
		prev_close = previous_row[4]
		now_open = now_row[1]
		now_high = now_row[2]
		now_low = now_row[3]
		now_close = now_row[4]
		if prev_close > prev_open:	# and prev_close > now_close:
			# green hanging man
			if now_close > now_open:
				now_body = now_close - now_open
				now_shadow_below = now_open - now_low
				now_shadow_above = now_high - now_close
				if (now_shadow_below / now_body) > 2.5 and (now_shadow_above == 0 or (now_body / now_shadow_above) > 2):
					return True
			# red hanging man
			if now_close < now_open:
				now_body = now_open - now_close
				now_shadow_below = now_close - now_low
				now_shadow_above = now_high - now_open
				if (now_shadow_below / now_body) > 2.5 and (now_shadow_above == 0 or (now_body / now_shadow_above) > 2):
					return True
	return False


def signal(price_data):
	if hammer_candlestick(price_data):
		return 1.
	if hanging_man_candlestick(price_data):
		return -1.
	return 0.


# In case of testing to create new patterns:
def main(price_data):
	points = [[],[]]
	count = 1
	for i in range(1, len(price_data)):
		if hanging_man_candlestick(price_data[:i+1]):
			print(i+1, price_data[i+1], 'HAMMER')
			count += 1
			points[0].append(i+1)
			points[1].append(price_data[i][3]-1.3)
	quotes = []
	count1 = 1
	for row in price_data:
		quotes.append((count1, row[1], row[2], row[3], row[4]))
		count1 += 1
	make_plots(quotes, points)


if __name__ == '__main__':
	company = 'TSLA'
	bar_size = '30 mins'
	price_data = get_price_data(company, bar_size)
	main(price_data)



