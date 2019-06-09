import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import message, Connection

from all_companies import set_of_all_companies
import get_historical_data
import settings

# STRUCTURE:
# 1. Historical data collect for chosen timeframe: make db
#	- make new list of companies (only with data) ??
# 2. Update dp everery [time] for every single timeframe of db data
# 3. Historical data analysis:
#	3.1 Filters make new watch-list:
#		- not penny-stock
#		- not low volume
#	3.2 Analysis:
#		- volume analysis: signals db
#		- comare signals and range watchlist by signal force
# 4. Make trading decisions
# 5. Trading

if __name__ == "__main__":

# 1. Historical data collect:
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	for company in set_of_all_companies():
		get_historical_data.main(conn, company)
	conn.disconnect()

# 2. Historical data update:

#	file = open('ergerg.csv')
#	print(file)






# 3. Historical data analysis:
#	company = 'GE'
#	get_historical_data.main(company, '3 Y', '1 day')
#	volume_analysis.main(company, '3 Y', '1 day')

'''
# 4. Make trading decisions

# Get account info:
	def prt_msg(msg):
		if msg.key == 'BuyingPower' and msg.currency == 'USD':
			print(f"Buying Power: ${msg.value}")
		if msg.key == 'TotalCashValue' and msg.currency == 'USD':
			print(f'Total: ${msg.value}')
		if msg.key == 'GrossPositionValue' and msg.currency == 'USD':
			print(f'Gross positions value: ${msg.value}')
		if msg.key == 'UnrealizedPnL' and msg.currency == 'USD':
			print(f'Unrealized P&L: ${msg.value}')			

	conn = settings.connection
#	conn.registerAll(print)	# this is for errors searching
	conn.register(prt_msg,
					message.updateAccountValue
				#	, message.updatePortfolio
					)
	conn.connect()
	conn.reqAccountUpdates(True, settings.ACCOUNT_NUMBER)
	time.sleep(4)
	conn.disconnect()
'''

# 5. Trading functional:
#	conn = Connection.create(port=7497, clientId=0)
#	contract = create_contract('FB', 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print_message_from_ib)
#	conn.connect()
#	order = create_LMT_order('LMT', 1, 'BUY', 100)
#	tws_conn.placeOrder(order_id, contract, order)
#	time.sleep(5)
#	conn.disconnect()
