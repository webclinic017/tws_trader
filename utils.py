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
	if work_day == 1 or work_day == 6: # if it is weekend
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
	best_strategy = None
	with open(f'!BestStrategies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file, delimiter=';'):
			if x[0] == company:
				best_strategy = [
								x[3],	# K level to open
								x[4],	# D level to open
								x[5],	# KD difference to open
								x[6],	# Stop loss
								x[7],	# Take profit
								x[8],	# K level to close
								x[9],	# D level to close
								x[10]	#KD difference to close
								]
	for i in range(len(best_strategy)):
		if best_strategy[i] != '':
			best_strategy.insert(i, eval(best_strategy.pop(i)))
		else:
			best_strategy.pop(i)
			best_strategy.insert(i, None)
	best_strategy = tuple(best_strategy)
	return best_strategy

