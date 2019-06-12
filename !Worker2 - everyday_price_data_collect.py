import csv
import time

from ib.opt import Connection

import updater

def main(c):
	companies_with_data = set()
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = set(y.split(';'))
				companies_with_data -= {''}
	while True:
		updater.main(c, companies_with_data)	 # N.B.: 2 D updating depth!
		time.sleep(60*10)	# Updating every 30 mins (20 mins updatind + 10 mins awaiting)

if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
		main(conn)
	except(KeyboardInterrupt):
		print('\nBye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

