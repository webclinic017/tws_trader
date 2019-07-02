import csv
import time

from ib.opt import message, Connection

from settings import ACCOUNT_NUMBER


open_positions = []
def get_open_positions_info(msg):
	open_positions.append({'Company': msg.contract.m_symbol, 'Quantity': msg.pos})


def create_csv_with_open_positions(open_positions):
	with open('!MyPositions.csv', 'w', encoding='utf-8') as csvfile:
		fieldnames = ('Company', 'Quantity')
		a = csv.DictWriter(csvfile, fieldnames, delimiter=';')
		a.writeheader()
		for row in open_positions:
			a.writerow(row)


def read_positions_from_csv():
	open_positions = []
	with open('!MyPositions.csv', 'r', encoding='utf-8') as csvfile:
		fieldnames = ('Company', 'Quantity')
		a = csv.DictReader(csvfile, fieldnames, delimiter=';')
		for row in a:
			open_positions.append(row)
	# print(open_positions)
	return open_positions


def open_position(c, company):
	global open_positions
	c.register(get_open_positions_info, message.position)
	c.reqPositions()
	time.sleep(2)
	if open_positions != []:
		create_csv_with_open_positions(open_positions)
	open_positions = read_positions_from_csv()
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
	open_positions = []


def get_order_id(msg):
	# print(msg.orderId)
	with open('!NextValidId.csv', 'w', encoding='utf-8') as csvfile:
		csvfile.write(str(msg.orderId))
	print(msg.orderId)


def next_valid_order_Id(c):
	c.register(get_order_id, message.nextValidId)
	c.reqPositions()
	time.sleep(2)
	orderid = None
	with open('!NextValidId.csv', 'r', encoding='utf-8') as file:
		for next_id in csv.reader(file):
			orderid = next_id[0]
	return int(orderid)


buying_power_total = []
def printing(msg):
	if msg.key == 'BuyingPower':
		buying_power_total.append(float(msg.value))


def buying_power(c):
	global buying_power_total
	c.register(printing, message.updateAccountValue)
	c.reqAccountUpdates(True, ACCOUNT_NUMBER)
	time.sleep(2)
	return buying_power_total[0]


# In case of testing:
if __name__ == '__main__':
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	# c.registerAll(print)
	company = 'TSLA'
	print(f'Open position for {company}:', open_position(c, company))
	print('Next valid order id:', next_valid_order_Id(c))
	print('Buying power:', buying_power(c))
	c.disconnect()

