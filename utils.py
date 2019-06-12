from ib.ext.Contract import Contract

def create_contract_from_ticker(symbol, sec_type='STK', exch='SMART', prim_exch='SMART', curr='USD'):
	contract = Contract()
	contract.m_symbol = symbol
	contract.m_secType = sec_type
	contract.m_exchange = exch
	contract.m_primaryExch = prim_exch
	contract.m_currency = curr
	return contract

