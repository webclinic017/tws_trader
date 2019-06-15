import csv
import time

from ib.opt import message, Connection

import settings

open_positions = []
def get_open_positions_info(msg):
	open_positions.append(f'{msg.contract.m_symbol};{msg.pos}')

def get_order_id(msg):
	with open('!NextValidId.csv', 'w', encoding='utf-8') as csvfile:
		csvfile.write(str(msg.orderId))

def create_csv_with_open_positions(open_positions):
	with open('!MyPositions.csv', 'w', encoding='utf-8') as csvfile:
		fieldnames = ('Ticker', 'Quantity')
		delimiter=';'
		a = csv.writer(csvfile, fieldnames, delimiter=delimiter)
		for row in open_positions:
			a.writerow(row.split(';'))

def main(c):
	global open_positions
	c.register(get_open_positions_info, message.position)
	c.register(get_order_id, message.nextValidId)
	c.reqPositions()
	time.sleep(2)
	create_csv_with_open_positions(open_positions)

	companies_in_position = set()
	for row in open_positions:
		if int(row.split(';')[1]) != 0:
			companies_in_position.add(row.split(';')[0])

	orderid = None
	with open('!NextValidId.csv', 'r', encoding='utf-8') as file:
		for next_id in csv.reader(file):
			orderid = next_id[0]

	return (companies_in_position, orderid)

	open_positions = []


# In case of testing:
if __name__ == '__main__':
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	c.registerAll(print)
	print(main(c))
	c.disconnect()

