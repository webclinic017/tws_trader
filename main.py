import time

from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import message

from all_companies import set_of_all_companies
import get_historical_data
import settings
import volume_analysis

'''
import logging 
mpl_logger = logging.getLogger('matplotlib') 
mpl_logger.setLevel(logging.WARNING)
'''

if __name__ == "__main__":
# STRUSTURE:
# 1. Updating historical data
# 2. Historical data analysis
# 3. Make trading decisions
# 4. Trading

# 1.1. Historical data collect:
#	for company in set_of_all_companies():
#		get_historical_data.main(company, '3 Y', '1 day')
# 1.2. Historical data update:

# 2. Historical data analysis:
#	company = 'GE'
#	get_historical_data.main(company, '3 Y', '1 day')
#	volume_analysis.main(company, '3 Y', '1 day')

# 3. Get account info:
	def prt_msg(msg):
		print(msg)
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

# 4. Trading functional:
#	conn = Connection.create(port=7497, clientId=0)
#	contract = create_contract('FB', 'STK', 'SMART', 'SMART', 'USD')
#	conn.registerAll(print_message_from_ib)
#	conn.connect()
#	order = create_LMT_order('LMT', 1, 'BUY', 100)
#	tws_conn.placeOrder(order_id, contract, order)
#	time.sleep(5)
#	conn.disconnect()
