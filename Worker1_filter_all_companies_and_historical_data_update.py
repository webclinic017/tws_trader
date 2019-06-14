import csv

from ib.opt import Connection

import rare2_filter_companies_and_collect_historical_data
from rare1_all_companies import set_of_all_companies

def main(conn):
	set_of_companies = set_of_all_companies()
	count = 1
	for company in set_of_companies:
		percentage = int((count/len(set_of_companies))*30)
		if count < len(set_of_companies):
			print(' ['+'█'*percentage+' '*(30 - percentage)+']', f'{count}/{len(set_of_companies)} Requesting data for {company}', ' '*5, end='\r')
			count += 1
		else:
			print(' ['+'█'*percentage+' '*(30 - percentage)+']', f'{count}/{len(set_of_companies)} Updating complete!', ' '*27)
		rare2_filter_companies_and_collect_historical_data.main(conn, company)

	companies_with_data = set()
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = set(y.split(';'))
				companies_with_data -= {''}

	print(f'\nFrom {len(set_of_companies)} was choosen only {len(companies_with_data)} companies and historical data for choosen companies was collected.')

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

