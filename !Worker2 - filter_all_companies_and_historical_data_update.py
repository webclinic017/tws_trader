from ib.opt import Connection

import rare2_filter_companies_and_collect_historical_data
from rare1_all_companies import set_of_all_companies

def main(conn):
	i = 1
	for company in set_of_all_companies():
		print(f'{i}/{len(set_of_all_companies())}')
		i += 1
		rare2_filter_companies_and_collect_historical_data.main(conn, company)

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

