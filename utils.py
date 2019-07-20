import csv
from datetime import datetime, timedelta
import time

from ib.ext.Contract import Contract
import pandas as pd
import pytz
import yfinance as yf

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


def clear_all_about_collected_price_data():
	open('worker1/Errors.csv', "w+").close()
	open('!MyCompanies.csv', "w+").close()
	open('!RejectedCompanies.csv', "w+").close()


def set_with_my_companies():
	companies_with_data = set()
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = set(y.split(';'))
				companies_with_data -= {''}
	return companies_with_data


def get_price_data(company, bar_size):
	price_data=[]
	with open(f'historical_data/{company} {bar_size}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			if row[0] != 'Datetime':
				formated_row = []
				formated_row.append(row[0])
				formated_row.append(float(row[1]))
				formated_row.append(float(row[2]))
				formated_row.append(float(row[3]))
				formated_row.append(float(row[4]))
				formated_row.append(int(row[5]))
				try:
					if row[6] != '' and row[7] != '':
						formated_row.append(round(float(row[6]), 1))
						formated_row.append(round(float(row[7]), 1))
				except:
					formated_row.append('')
					formated_row.append('')
				price_data.append(formated_row)
	return price_data


def get_price_data_df(company, bar_size):
	price_data_df = pd.read_csv(f'historical_data/{company} {bar_size}.csv', index_col=0, sep=';')
	return price_data_df


def the_best_known_strategy(company):
	the_best_strategy = {}
	with open(f'!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				the_best_strategy['bar_size'] = x[4]
				the_best_strategy['Indicators_combination'] = x[5]
				the_best_strategy['K_level_to_buy'] = x[6]
				the_best_strategy['D_level_to_buy'] = x[7]
				the_best_strategy['KD_difference_to_buy'] = x[8]
				the_best_strategy['stop_loss'] = x[9]
				the_best_strategy['take_profit'] = x[10]
				the_best_strategy['K_level_to_sell'] = x[11]
				the_best_strategy['D_level_to_sell'] = x[12]
				the_best_strategy['KD_difference_to_sell'] = x[13]
				the_best_strategy['Stoch_parameters'] = x[14]
				the_best_strategy['Weekday_buy'] = x[15]
				the_best_strategy['Weekday_sell'] = x[16]
				the_best_strategy['Volume_profile_locator'] =  x[17]
				the_best_strategy['Japanese_candlesticks'] = x[18]
	for key, value in the_best_strategy.items():
		if value != '' and key != 'bar_size' and 'Weekday' not in key and key != 'Indicators_combination':
			the_best_strategy[key] = eval(value)
		if value == '':
			the_best_strategy[key] = None
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


def my_range(start, stop, step=0.5):
	float_list = []
	x = start
	while x < stop:
		float_list.append(round(x, 1))
		x += step
	return tuple(float_list)


def update_price_data(company, bar_size):
	y_interval = {'1 min': '1m', '2 mins': '2m', '5 mins': '5m', '15 mins': '15m', '30 mins': '30m',
					'1 hour': '1h', '1 day': '1d', '1 week': '1wk', '1 month': '1mo'}
	data = yf.Ticker(company).history(interval=y_interval[bar_size]).iloc[:,:-2] # excluding Dividends and Stock Splits
	last_date = pd.read_csv(f'historical_data/{company} {bar_size}.csv', index_col=0, sep=';').index[-1]
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
	new_price_data.to_csv(rf'historical_data/{company} {bar_size}.csv', mode='a', header=False, sep=';')

