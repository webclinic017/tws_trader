import logging

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_finance import candlestick_ohlc

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING)


def main(list_with_price_data, history, capital_by_date, company):
	#fig, ax = plt.subplots()
	fig = plt.figure()
	ax_main = fig.add_subplot(2, 1, 1)
	ax_main.set_position([0.05, 0.15, 0.9, 0.7])
	ax_stoch = fig.add_subplot(8, 1, 5)
	ax_stoch.set_position([0.05, 0.05, 0.9, 0.1])

# Capital	
	koef = capital_by_date[0][1] / float(list_with_price_data[1][1])	# history[1][3]
	capital_x = []
	capital_y = []
	dates_dict = {}
	x = 1
	for row in capital_by_date:
		capital_x.append(x)
		dates_dict[row[0]] = x
		x += 1
		capital_y.append(row[1] / koef)
	buy_and_hold_profitability = round((float(list_with_price_data[-1][4]) - float(list_with_price_data[1][1])) / float(list_with_price_data[1][1]) * 100, 1)
	profitability = round((capital_y[-1] - capital_y[0]) / capital_y[0] * 100, 1)
	ax_main.plot(capital_x, capital_y, label=f'capital ({profitability}% vs. {buy_and_hold_profitability}%)', linewidth = 0.7)

# Candlestick chart + stoch
	stoch_time = []
	stoch_K = []
	stoch_D = []
	quotes = []
	for row in list_with_price_data[1:]:
		quotes.append((dates_dict[row[0]], float(row[1]), float(row[2]), float(row[3]), float(row[4])))
		if row[6] != '' and row[7] != '':
			stoch_K.append(float(row[6]))
			stoch_D.append(float(row[7]))
			stoch_time.append(dates_dict[row[0]])
		else:
			stoch_K.append(0)
			stoch_D.append(0)
			stoch_time.append(dates_dict[row[0]])

	candlestick_ohlc(ax_main, quotes, width=0.3, colorup='g', colordown='r')
	ax_stoch.plot(stoch_time, stoch_K, 'g', linewidth=0.4, label='%K')
	ax_stoch.plot(stoch_time, stoch_D, 'k', linewidth=0.5, label='%D')

# Trades
	open_dates = []
	open_prices = []
	sell_dates = []
	sell_prices = []
	close_dates = []
	close_prices = []
	now_date = []
	now_price = []
	for deal in history[1:]:
		if deal[1] == 'long':
			open_prices.append(deal[3])
			open_dates.append(dates_dict[deal[0]])
		if deal[1] == 'short':
			sell_prices.append(deal[3])
			sell_dates.append(dates_dict[deal[0]])
		if 'closed' in deal[1]:
			close_prices.append(deal[3])
			close_dates.append(dates_dict[deal[0]])
		if deal[1] == 'now':
			now_price.append(deal[3])
			now_date.append(dates_dict[deal[0]])
	ax_main.plot(open_dates, open_prices, 'k^', label='buy trades') # buy
	ax_main.plot(sell_dates, sell_prices, 'kv', label='sell trades')	# sell
	ax_main.plot(close_dates, close_prices, 'kx', label='close trades')	# close
	ax_main.plot(now_date, now_price, 'k<', label='now open position')	# now

# Making beauty
	ax_stoch.set_xlabel('Date')
	ax_main.set_ylabel('Price')
	ax_stoch.set_ylabel('Stoch')
	ax_main.legend()
	title = f'{company}\nMy strategy: {profitability}%\nBuy and hold: {buy_and_hold_profitability}%'
	plt.title(title)

	ax_main.xaxis.set_minor_locator(ticker.MultipleLocator(1))
	ax_main.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax_main.yaxis.set_minor_locator(ticker.MultipleLocator(10))
	ax_stoch.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax_main.minorticks_on()
	plt.grid(which='major', linestyle='--')
	ax_main.grid(which='minor', color = 'gray', linestyle = ':')

	plt.show()

