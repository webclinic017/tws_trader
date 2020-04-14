from ib.ext.Contract import Contract


class Forex(Contract):
	
	def __init__(self, currency_1, currency_2):
		self.m_symbol = currency_1
		self.m_secType = 'CASH'
		self.m_currency = currency_2
		self.m_exchange = 'IDEALPRO'


class Stock(Contract):

	def __init__(self, symbol):
		self.m_symbol = symbol
		self.m_secType = 'STK'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		# self.m_exchange = 'ISLAND'
		# self.m_primaryExch = ''


class Index(Contract):

	def __init__(self, symbol):
		self.m_symbol = symbol
		self.m_secType = 'IND'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'


class CFD(Contract):

	def __init__(self, symbol):
		self.m_symbol = symbol
		self.m_secType = 'CFD'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'


class Futures(Contract):

	def __init__(self, symbol, expiration):
		self.m_symbol = symbol
		self.m_secType = 'FUT'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.m_expiry = expiration
		self.m_localSymbol = ''
		self.m_multiplier = ''


class Option(Contract):

	def __init__(self, symbol, expiration, strike:float, right):
		self.m_symbol = symbol
		self.m_secType = 'OPT'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.m_expiry = expiration
		self.m_strike = strike
		self.m_right = right
		self.m_multiplier = '100'
		self.m_localSymbol = ''
		self.m_tradingClass = ''


class OptionPut(Option):

	def __init__(self, symbol, expiration, strike:float):
		super.__init__(symbol, expiration, strike)
		self.m_right = 'P'


class OptionCall(Option):

	def __init__(self, symbol, expiration, strike:float):
		super.__init__(symbol, expiration, strike)
		self.m_right = 'C'


class FuturesOption(Contract):

	def __init__(self, symbol, expiration, strike:float, right):
		self.m_symbol = symbol
		self.m_secType = 'FOP'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.m_expiry = expiration
		self.m_strike = strike
		self.m_right = right
		self.m_multiplier = '100'
		self.m_localSymbol = ''
		self.m_tradingClass = ''


class Bond(Contract):

	def __init__(self, symbol):
		self.m_symbol = symbol 		# enter CUSIP as symbol
		self.m_secType = 'BOND'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.m_conId = 0


class Fund(Contract):

	def __init__(self, symbol):
		self.m_symbol = symbol
		self.m_secType = 'FUND'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'


class Commodity(Contract):

	def __init__(self, symbol):
		self.m_symbol = symbol
		self.m_secType = 'CMDTY'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'


class Warrant(Contract):

	def __init__(self, symbol):
		self.m_localSymbol = symbol
		self.m_secType = 'IOPT'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
