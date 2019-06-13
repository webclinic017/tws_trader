import csv
import time

from ib.opt import Connection

import making_watchlist_of_interesting_companies
import updater

def main(c):
	companies_with_data = set()
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = set(y.split(';'))
				companies_with_data -= {''}

	updater.main(c, companies_with_data)	 # N.B.: 1 D updating depth!

	making_watchlist_of_interesting_companies.main()

if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
		main(conn)
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

