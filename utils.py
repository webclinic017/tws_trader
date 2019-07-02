from ib.ext.Contract import Contract

import csv
import time


def create_contract_from_ticker(symbol, sec_type='STK', exch='SMART', prim_exch='SMART', curr='USD'):
	contract = Contract()
	contract.m_symbol = symbol
	contract.m_secType = sec_type
	contract.m_exchange = exch
	contract.m_primaryExch = prim_exch
	contract.m_currency = curr
	return contract


def SEs_should_work_now():
	hours_now = int(time.strftime("%H", time.gmtime()))
	work_day = int(time.strftime("%w", time.gmtime()))
	if work_day == 6 or work_day == 7: # if it is weekend
		work_day = False
		return False
	else:
		if hours_now < 13 or hours_now > 19: # if it is not 16-22 hours MSK
			return False
		else:
			return True


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


def get_price_data(stock_ticker):
	list_with_price_data=[]
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)
	return list_with_price_data


def the_best_known_strategy(company):
	the_best_strategy = {}
	with open(f'!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				the_best_strategy['K_level_to_buy'] = x[4]
				the_best_strategy['D_level_to_buy'] = x[5]
				the_best_strategy['KD_difference_to_buy'] = x[6]
				the_best_strategy['stop_loss'] = x[7]
				the_best_strategy['take_profit'] = x[8]
				the_best_strategy['K_level_to_sell'] = x[9]
				the_best_strategy['D_level_to_sell'] = x[10]
				the_best_strategy['KD_difference_to_sell'] = x[11]
				the_best_strategy['Stoch_parameters'] = x[12]
	for key, value in the_best_strategy.items():
		if value != '':
			the_best_strategy[key] = eval(value)
		else:
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
	return max_drawdown

