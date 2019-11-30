from ib.ext.Contract import Contract


class PutOption(Contract):

	def __init__(self, company, expiration, strike):
		self.m_symbol = company
		self.m_secType = "OPT"
		self.m_exchange = "SMART"
		self.m_currency = "USD"
		self.m_expiry = expiration
		self.m_strike = strike
		self.m_right = "P"
		self.multiplier = "100"


class CallOption(Contract):

	def __init__(self, company, expiration, strike):
		self.m_symbol = company
		self.m_secType = "OPT"
		self.m_exchange = "SMART"
		self.m_currency = "USD"
		self.m_expiry = expiration
		self.m_strike = strike
		self.m_right = "C"
		self.multiplier = "100"
