# + убрать временные пустоты на графике !!!!!!
# + график стохастика

from datetime import datetime
import logging

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_finance import candlestick_ohlc
# import pandas as pd

import settings
import utils

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING)


def main(list_with_price_data, history, capital_by_date, company):
	fig, ax = plt.subplots()

# Capital	
	koef = capital_by_date[0][1] / history[1][3]
	capital_x = []
	capital_y = []
	dates_dict = {}
	x = 1
	for row in capital_by_date:
		# date = datetime.strptime(row[0], "%Y%m%d  %H:%M:%S").timestamp()
		capital_x.append(x)
		dates_dict[row[0]] = x
		x += 1
		capital_y.append(row[1] / koef)
	buy_and_hold_profitability = round((float(list_with_price_data[-1][4]) - float(list_with_price_data[1][1])) / float(list_with_price_data[1][1]) * 100, 1)
	profitability = round((capital_y[-1] - capital_y[0]) / capital_y[0] * 100, 1)
	plt.plot(capital_x, capital_y, label=f'capital ({profitability}% vs. {buy_and_hold_profitability}%)', linewidth = 0.7)

# Candlestick chart
	quotes = []
	for row in list_with_price_data[1:]:
		# date = datetime.strptime(row[0], "%Y%m%d  %H:%M:%S").timestamp()
		quotes.append((dates_dict[row[0]], float(row[1]), float(row[2]), float(row[3]), float(row[4])))
	candlestick_ohlc(ax, quotes, width=0.3, colorup='g', colordown='r')

# Trades
	open_dates = []
	open_prices = []
	close_dates = []
	close_prices = []
	now_date = []
	now_price = []
	for deal in history[1:]:
		if deal[1] == 'buy':
			open_prices.append(deal[3])
			open_dates.append(dates_dict[deal[0]])
		if deal[1] == 'close':
			close_prices.append(deal[3])
			close_dates.append(dates_dict[deal[0]])
		if deal[1] == 'now':
			now_price.append(deal[3])
			now_date.append(dates_dict[deal[0]])
	plt.plot(open_dates, open_prices, 'g^', label='buy trades') # open
	plt.plot(close_dates, close_prices, 'rv', label='close trades')	# close
	plt.plot(now_date, now_price, 'k<', label='now open position')	# now

# Making beauty


	ax.set_xlabel('Date')
	ax.set_ylabel('Price')
	ax.legend(loc=2)
	title = f'{company}\nMy strategy: {profitability}%\nBuy and hold: {buy_and_hold_profitability}%'
	plt.title(title)
#	ax.xaxis_date()
#	ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y.%m.%d"))

	ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))
	ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax.yaxis.set_minor_locator(ticker.MultipleLocator(2))
	ax.minorticks_on()
	plt.grid(which='major', linestyle='--')
	ax.grid(which='minor', color = 'gray', linestyle = ':')
	plt.show()

