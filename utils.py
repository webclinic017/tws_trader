import ast
import csv
from datetime import datetime, timedelta
import os
import pickle
import time

from ib.ext.Contract import Contract
import pandas as pd
import pytz
import yfinance as yf
from yahoo_historical import Fetcher

from indicators import RS
from indicators import SMA
from indicators import stochastic
from indicators import volume_profile


def first_run():
	if not os.path.exists('tmp_data'):
		os.makedirs('tmp_data')
	if not os.path.isfile('tmp_data/!BestStrategies.pkl'):
		open('tmp_data/!BestStrategies.pkl', 'w+', encoding='utf-8').close()
	if not os.path.exists('historical_data'):
		os.makedirs('historical_data')


def create_contract_from_ticker(symbol, sec_type='STK', exch='SMART', prim_exch='SMART', curr='USD'):
	contract = Contract()
	contract.m_symbol = symbol
	contract.m_secType = sec_type
	contract.m_exchange = exch
	contract.m_primaryExch = prim_exch
	contract.m_currency = curr
	return contract


def get_working_shedule(bar_size):
	working_shedule = []
	interval = None
	if bar_size.split()[1] == 'mins':
		interval = int(bar_size.split()[0])
	if bar_size.split()[1][:4] == 'hour':
		interval = int(bar_size.split()[0])*60
	if bar_size.split()[1] == 'day':
		interval = 24*60
	open_time = datetime.strptime('16:30', '%H:%M')
	close_time = datetime.strptime('23:00', '%H:%M')
	time = open_time
	while open_time <= time <= close_time:
		working_shedule.append(datetime.strftime(time, '%H:%M'))
		time += timedelta(minutes=interval)
	return working_shedule


def print_loading(done_number, total_number, company):
	percentage = int((done_number/total_number)*30)
	if done_number < total_number:
		print(f'  {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number} Requesting data for {company}', ' '*5, end='\r')
	else:
		time_now = time.strftime("%m/%d/%Y %I:%M %p", time.gmtime())
		print(f' {int(round(percentage*3.33, 0))}% |'+'█'*percentage+' '*(30 - percentage)+'|', f'{done_number}/{total_number} Updating complete!', time_now)


def get_price_data(company, bar_size):
	price_data = []
	with open(f'historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.DictReader(data_file, delimiter=';'):
			for key, value in row.items():
				if key != 'Datetime':
					row[key] = ast.literal_eval(value)
			price_data.append(row)
	return price_data

def request_historical_data(company):
# Get now date in [int(year), int(month), int(day)] format
	now = time.strftime('%Y,%m%,%d', time.gmtime())
	now = now.split(',')
	now_date = []
	for item in now:
		now_date.append(int(item))

# This is NOT correct! But it shows the best profitability
	now_date = [2019,1,14]

	req = Fetcher(company, [2000,1,1], now_date)
	return req.getHistorical()


def the_best_known_strategy(company):
	the_best_strategy = None
	strategies = []
	with open(f'tmp_data/!BestStrategies-exp.pkl', 'rb') as file:
		while True:
			try:
				strategies.append(pickle.load(file))
			except EOFError:
				break
	for strategy in strategies:
		try:
			if strategy['company'] == company:
				the_best_strategy = strategy
		except(KeyError):
			return None
	return the_best_strategy


def max_drawdown_calculate(capital_by_date):
	max_drawdown = 0
	for i in range(0,len(capital_by_date)-1):
		capital = capital_by_date[:len(capital_by_date)-i]
		max_capital = max(tuple(x[1] for x in capital))
		max_capital_date_index = None
		for row in capital:
			if max_capital == row[1]:
				max_capital_date_index = capital.index(row)	
		if max_capital == capital[-1][1]:
			min_capital_since_max_capital = max_capital
		else:
			min_capital_since_max_capital = min(tuple(x[1] for x in capital[max_capital_date_index+1:]))
		new_max_drawdown = (max_capital - min_capital_since_max_capital) / max_capital * 100
		if new_max_drawdown > max_drawdown:
			max_drawdown = new_max_drawdown
	return -max_drawdown


def update_price_data(company, bar_size):
	y_interval = {'1 min': '1m', '2 mins': '2m', '5 mins': '5m', '15 mins': '15m', '30 mins': '30m',
					'1 hour': '1h', '1 day': '1d', '1 week': '1wk', '1 month': '1mo'}
	data = yf.Ticker(company).history(interval=y_interval[bar_size]).iloc[:,:-2] # excluding Dividends and Stock Splits
	filename = f'historical_data/{company} {bar_size}.csv'
	if not os.path.isfile(filename): # create new file
		data.to_csv(filename, mode='a', sep=';')
	else: # update
		last_date = pd.read_csv(filename, index_col=0, sep=';').index[-1]
		new_price_data = data.loc[last_date:,:].iloc[1:]
		interval = None
		if bar_size.split()[1] == 'mins':
			interval = int(bar_size.split()[0])
		if bar_size.split()[1][:4] == 'hour':
			interval = int(bar_size.split()[0])*60
		if bar_size.split()[1] == 'day':
			interval = 24*60
		new_last_date = data.index[-1].to_pydatetime()
		time_now_in_EST = datetime.now(pytz.timezone('US/Eastern'))
		difference = (time_now_in_EST - new_last_date)
		difference = difference.seconds//3600
		if difference < interval:
			new_price_data = new_price_data.iloc[:-1]
		new_price_data.to_csv(filename, mode='a', header=False, sep=';')


def put_indicators_to_price_data(price_data, strategy, historical_data):
	for action in ('buy', 'sell'):
		price_data = stochastic.update(price_data,
		                               strategy[f'{action}']['stochastic']['stoch_period'],
		                               strategy[f'{action}']['stochastic']['stoch_slow_avg'],
		                               strategy[f'{action}']['stochastic']['stoch_fast_avg'],
		                               action
		                               )
		price_data = SMA.update(price_data,
		                        strategy[f'{action}']['SMA']['period'],
		                        action)
		price_data = RS.update(price_data,
		                       strategy[f'{action}']['RS'],
		                       historical_data,
		                       action)
	price_data = volume_profile.update(price_data,
	                                   strategy[f'{action}']['volume_profile']['locator'],
	                                   historical_data)
	return price_data
