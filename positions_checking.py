import csv
import time

from ib.opt import message, Connection

import settings

open_positions = []
def get_open_positions_info(msg):
	open_positions.append(f'{msg.contract.m_symbol};{msg.pos}')
	return open_positions

def create_csv_with_open_positions(open_positions):
	with open('!MyPositions.csv', 'w', encoding='utf-8') as csvfile:
		fieldnames = ('Ticker', 'Quantity')
		delimiter=';'
		a = csv.writer(csvfile, fieldnames, delimiter=delimiter)
		for row in open_positions:
			a.writerow(row.split(';'))

# как вызывать эту функцию мимо main? Может ее в класс запихнуть?
def companies_in_position():
	companies_in_position = set()
	for row in open_positions:
		companies_in_dposition.add(row.split(';')[0])
	return companies_in_position

def main(c):
	global open_positions
	c.register(get_open_positions_info, message.position)
	c.reqPositions()
	time.sleep(2)
	create_csv_with_open_positions(open_positions)

	companies_in_position = set()
	for row in open_positions:
		companies_in_position.add(row.split(';')[0])
	return companies_in_position

	open_positions = []

# In case of testing:
if __name__ == '__main__':
	c = Connection.create(port=7497, clientId=0)
	c.connect()
	main(c)
	c.disconnect()

