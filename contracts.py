from ib.ext.Contract import Contract

# классы контрактов с неофициальной библиотекой
class Forex(Contract):
	
	def __init__(self, currency_1, currency_2):
		super().__init__()
		self.m_symbol = currency_1
		self.m_secType = 'CASH'
		self.m_currency = currency_2
		self.m_exchange = 'IDEALPRO'
		self.historical_data_type = 'MIDPOINT'


class Stock(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_symbol = symbol
		self.m_secType = 'STK'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		# self.m_primaryExch = ''
		self.historical_data_type = 'TRADES'


class Index(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_symbol = symbol
		self.m_secType = 'IND'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.historical_data_type = 'TRADES'


class CFD(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_symbol = symbol
		self.m_secType = 'CFD'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.historical_data_type = 'MIDPOINT'


class Futures(Contract):

	def __init__(self, symbol, expiration):
		super().__init__()
		self.m_symbol = symbol
		self.m_secType = 'FUT'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.m_expiry = expiration
		self.m_localSymbol = ''
		self.m_multiplier = ''
		self.historical_data_type = 'TRADES'


class Option(Contract):

	def __init__(self, symbol, expiration, strike:float, right):
		super().__init__()
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
		self.historical_data_type = 'TRADES'


class OptionPut(Option):

	def __init__(self, symbol, expiration, strike:float):
		super().__init__(symbol, expiration, strike, 'P')


class OptionCall(Option):

	def __init__(self, symbol, expiration, strike: float):
		super().__init__(symbol, expiration, strike, 'C')


class FuturesOption(Contract):

	def __init__(self, symbol, expiration, strike:float, right):
		super().__init__()
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
		self.historical_data_type = 'TRADES'


class Bond(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_symbol = symbol 		# enter CUSIP as symbol
		self.m_secType = 'BOND'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.m_conId = 0
		self.historical_data_type = 'TRADES'


class Fund(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_symbol = symbol
		self.m_secType = 'FUND'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.historical_data_type = 'MIDPOINT'


class Commodity(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_symbol = symbol
		self.m_secType = 'CMDTY'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.historical_data_type = 'MIDPOINT'


class Warrant(Contract):

	def __init__(self, symbol):
		super().__init__()
		self.m_localSymbol = symbol
		self.m_secType = 'IOPT'
		self.m_currency = 'USD'
		self.m_exchange = 'SMART'
		self.historical_data_type = 'TRADES'
