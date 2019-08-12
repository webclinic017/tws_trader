import csv
import time

from ib.opt import message, Connection

from settings import ACCOUNT_NUMBER, TWS_CONNECTION


# it takes <7 secs
def what_position_is_open_now_for(company, try_count=1):
# Register messages with positions from TWS
	open_positions = []
	def get_open_positions_info(msg):
		open_positions.append({'Company': msg.contract.m_symbol, 'Quantity': msg.pos})
# Write positionses info in scv
	def create_csv_with_open_positions(open_positions):
		with open('tmp_data/!MyPositions.csv', 'w', encoding='utf-8') as csvfile:
			fieldnames = ('Company', 'Quantity')
			a = csv.DictWriter(csvfile, fieldnames, delimiter=';')
			a.writeheader()
			for row in open_positions:
				a.writerow(row)
# Requesting positions from TWS
	TWS_CONNECTION.connect()
	TWS_CONNECTION.register(get_open_positions_info, message.position)
	TWS_CONNECTION.reqPositions()
	time.sleep(2)
	create_csv_with_open_positions(open_positions)
	TWS_CONNECTION.cancelPositions()
	TWS_CONNECTION.disconnect()
# Get positions ids from csv
	def read_positions_from_csv():
		open_positions = []
		with open('tmp_data/!MyPositions.csv', 'r', encoding='utf-8') as csvfile:
			fieldnames = ('Company', 'Quantity')
			a = csv.DictReader(csvfile, fieldnames, delimiter=';')
			for row in a:
				open_positions.append(row)
		return open_positions
	open_positions = read_positions_from_csv()
# Read positions
	companies_in_position = []
	for position in open_positions:
		if position.get('Company') != 'Company':
			companies_in_position.append(position.get('Company'))
# If there are "several positions" for single company - TWS makes error. 
	if len(companies_in_position) > len(set(companies_in_position)):
# Try to correct data 3 times
		if try_count <= 3:
			try_count += 1
			what_position_is_open_now_for(company, try_count)
		else:
			position = input(f'There is problem with getting info about position type for {company}. Please, enter position type here, is it \'None\', \'short\' or \'long\': ')
			if position == 'None':
				return None
			else:
				return position
	else:
		for position in open_positions:
			if position.get('Company', 'NO') == 'NO':
				return None
			else:
				if position.get('Company') == company:
					if int(position.get('Quantity')) == 0:
						return None
					if int(position.get('Quantity')) > 0:
						return 'long'
					if int(position.get('Quantity')) < 0:
						return 'short'

# It takes <3 secs
def orders_ids_are_open_now_for(company):
# Register messages with orders from TWS
	open_orders = []
	def get_open_orders_info(msg):
		open_orders.append({'OrderId': msg.orderId,
							'Company': msg.contract.m_symbol,
							'Quantity': msg.order.m_totalQuantity,
							'OrderType': msg.order.m_orderType
							})
# Write order's info in scv
	def create_csv_with_open_orders(open_orders):
		with open('tmp_data/!MyOrders.csv', 'w', encoding='utf-8') as csvfile:
			fieldnames = ('OrderId', 'Company', 'Quantity', 'OrderType')
			a = csv.DictWriter(csvfile, fieldnames, delimiter=';')
			a.writeheader()
			for row in open_orders:
				a.writerow(row)
# Requesting orders from TWS
	TWS_CONNECTION.connect()
	TWS_CONNECTION.register(get_open_orders_info, message.openOrder)
	TWS_CONNECTION.reqAllOpenOrders()
	time.sleep(2)
	create_csv_with_open_orders(open_orders)
	TWS_CONNECTION.disconnect()
# Get orders ids from csv
	orders_ids = []
	with open('tmp_data/!MyOrders.csv', 'r', encoding='utf-8') as csvfile:
			fieldnames = ('OrderId', 'Company', 'Quantity', 'OrderType')
			a = csv.DictReader(csvfile, fieldnames, delimiter=';')
			for row in a:
				if row.get('Company') == company:
					orders_ids.append(int(row.get('OrderId')))
	return tuple(orders_ids)


def get_next_order_id(msg):
	with open('tmp_data/!NextValidId.csv', 'w', encoding='utf-8') as csvfile:
		csvfile.write(str(msg.orderId))


def next_valid_order_Id():
	TWS_CONNECTION.connect()
	TWS_CONNECTION.register(get_next_order_id, message.nextValidId)
	TWS_CONNECTION.reqPositions()
	time.sleep(2)
	TWS_CONNECTION.cancelPositions()
	TWS_CONNECTION.disconnect()
	orderid = None
	with open('tmp_data/!NextValidId.csv', 'r', encoding='utf-8') as file:
		for next_id in csv.reader(file):
			orderid = next_id[0]
	return int(orderid) + 1


buying_power_total = []
def caching(msg):
	if msg.key == 'BuyingPower':
		buying_power_total.append(float(msg.value))


def buying_power():
	global buying_power_total
	TWS_CONNECTION.connect()
	TWS_CONNECTION.register(caching, message.updateAccountValue)
	TWS_CONNECTION.reqAccountUpdates(True, ACCOUNT_NUMBER)
	time.sleep(2)
	TWS_CONNECTION.disconnect()
	return float(buying_power_total[0])


availablefunds = []
def caching2(msg):
	if msg.key == 'AvailableFunds':
		availablefunds.append(float(msg.value))


def available_funds():
	global availablefunds
	TWS_CONNECTION.connect()
	TWS_CONNECTION.register(caching2, message.updateAccountValue)
	TWS_CONNECTION.reqAccountUpdates(True, ACCOUNT_NUMBER)
	time.sleep(1)
	TWS_CONNECTION.disconnect()
	return float(next(iter(availablefunds), 0))


# In case of testing:
if __name__ == '__main__':
	company = 'TSLA'
	print(f'Open position for {company}:', open_position(company))
	print('Next valid order id:', next_valid_order_Id())
	print('Buying power:', buying_power())

