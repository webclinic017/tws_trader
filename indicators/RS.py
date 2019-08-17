import csv
import time
from datetime import datetime

from ib.opt import message 	# , Connection
#import orders_checking
import sys
import utils
import main
from indicators import stochastic

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz
from indicators import volume_profile, stochastic, SMA

import hashlib
import W4_checking_account
import W7_backtest
import W8_optimum_finder
import cProfile
import os
import make_candlestick_chart

import logging

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_finance import candlestick_ohlc

# In order to launch without matplotlib debugging:
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)

from settings import TWS_CONNECTION, ACCOUNT_NUMBER
from yahoo_historical import Fetcher

# cProfile.run('W8_optimum_finder.main("TSLA")')
# cProfile.run('main.main("TSLA")')
# cProfile.run('W7_backtest.main2()')


import yfinance as yf




def make_plot(price_data, company):
	#fig, ax = plt.subplots()
	fig = plt.figure()
	ax_main = fig.add_subplot(2, 1, 1)
	ax_main.set_position([0.05, 0.15, 0.9, 0.7])
	ax_stoch = fig.add_subplot(8, 1, 5)
	ax_stoch.set_position([0.05, 0.05, 0.9, 0.1])

# Candlestick chart
	quotes = []
	count = 1
	dates_dict = {}
	for row in price_data:
		quotes.append((count, row[1], row[2], row[3], row[4]))
		dates_dict[row[0]] = count
		count += 1
	candlestick_ohlc(ax_main, quotes, width=0.3, colorup='g', colordown='r')

# Zig-zag points
	ZZ_movement = 20	# %
	gap = 1.5
	ZZ_movement = ZZ_movement / 100	# part
	zz_max_x = []
	zz_max_y = []
	zz_min_x = []
	zz_min_y = []
	x_max = None
	x_min = None
	y_max = None
	y_min = None

	# 1st iteration: finding first point after base point
	base_high =  price_data[0][2]
	base_low = price_data[0][3]
	for row in price_data:
		high = row[2]
		low = row[3]
		if high >= base_low * (1 + ZZ_movement):
			y_max = high
			x_max = dates_dict[row[0]]
			break
		else:
			if low < base_low:
				base_low = low
		if low <= base_high * (1 - ZZ_movement):
			y_min = low
			x_min = dates_dict[row[0]]
			break
		else:
			if high > base_high:
				base_high = high


	def update_max(x_max, y_max):
		x_min = None
		y_min = None
		for row in price_data[x_max+1:]:
			y_base_point = y_max
			high = row[2]
			low = row[3]
			if high > y_max:  # update max point
				y_max = high
				x_max = dates_dict[row[0]]
			else:  # find new x_min
				if low <= y_base_point * (1 - ZZ_movement):  # Complete! We find MAX and can append it to our lists
					zz_max_x.append(x_max)
					zz_max_y.append(y_max + gap)
					# find new max and update min
					y_min = low
					x_min = dates_dict[row[0]]
					break
		return (x_min, y_min)


	def update_min(x_min, y_min):
		x_max = None
		y_max = None
		for row in price_data[x_min+1:]:
			y_base_point = y_min
			high = row[2]
			low = row[3]
			if low < y_min:  # update min point
				x_min = dates_dict[row[0]]
				y_min = low
			else:  # find new x_min
				if high >= y_base_point * (1 + ZZ_movement):  # Complete! We find MIN and can append it to our lists
					zz_min_x.append(x_min)
					zz_min_y.append(y_min - gap)
					x_max = dates_dict[row[0]]
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
	if y_min:  # if 1st point after base is min
		y_max = True
		while y_min and y_max:
			if y_min:
				x_max, y_max = update_min(x_min, y_min)
			if y_max:
				x_min, y_min = update_max(x_max, y_max)


	ax_main.plot(zz_max_x, zz_max_y, 'kv', label='Zig-zag maximums') # zig_zag_max
	ax_main.plot(zz_min_x, zz_min_y, 'k^', label='Zig-zag minimums')	# zig_zag_min
	for i in zz_max_y:
		ax_main.plot([0, len(price_data)], [i, i], 'r:', linewidth=0.7)
	for i in zz_min_y:
		ax_main.plot([0, len(price_data)], [i, i], 'g:', linewidth=0.7)

	ax_main.scatter([5 for i in zz_max_y], zz_max_y, s=5, color='r')  # max allocation
	ax_main.scatter([-10 for i in zz_min_y], zz_min_y, s=5, color='g')  # min allocation
# Simulate trading by ZZ points






		# profit = (close_order_price - open_order_price) * quantity 	# - long
		# profit = (open_order_price - close_order_price) * abs(quantity)	# - short







# Making beauty
	ax_stoch.set_xlabel('Date')
	ax_main.set_ylabel('Price')
	ax_stoch.set_ylabel('Stoch')
	ax_main.legend()
	title = f'{company}'
	plt.title(title)

	ax_main.xaxis.set_minor_locator(ticker.MultipleLocator(1))
	ax_main.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax_main.yaxis.set_minor_locator(ticker.MultipleLocator(10))
	ax_stoch.yaxis.set_major_locator(ticker.MultipleLocator(10))
	ax_main.minorticks_on()
	plt.grid(which='major', linestyle='--')
	ax_main.grid(which='minor', color = 'gray', linestyle = ':')

	plt.show()





company = 'TSLA'
# strategy = utils.the_best_known_strategy(company)
# price_data = utils.get_price_data(company, strategy['bar_size'])
# price_data = stochastic.update(price_data, strategy['Stoch_parameters'])

df = Fetcher(f'{company}', [2000, 1, 1], [2019, 8, 16]).getHistorical()
data = df.loc[:, df.columns != 'Adj Close']

price_data = []
for i, row in data.iterrows():
	price_data.append([row['Date'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume']])

make_plot(price_data, company)










"""
1) Мультиинструментальность
2) УЗнать как генерировать комбинации индикаторов:
- может ли лучшая стратегия состоять из суммы нелучших вариантов индикаторов ?








"""












