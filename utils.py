from ib.ext.Contract import Contract

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

