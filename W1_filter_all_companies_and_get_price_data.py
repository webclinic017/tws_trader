import csv

from ib.opt import Connection

import filter_apply_and_collect_price_data_for_company
import utils
import write_indicators_in_price_data

def set_of_all_companies():
	all_companies=set()
	with open('./companylist.csv', 'r', encoding='utf-8') as company_list:
		for line in csv.reader(company_list):
			all_companies.add(line[0].replace(' ', ''))

	useless_companies=set()
	for company in all_companies:
		for bad_symbol in ('.', '^', '~'):
				if bad_symbol in company:
					useless_companies.add(company)
	my_companies = all_companies - useless_companies
	return my_companies

def main(conn):
	duration = '6 M'
	set_of_companies = set_of_all_companies()
	count = 1
	for company in set_of_companies:
		filter_apply_and_collect_price_data_for_company.main(conn, company, duration)
		write_indicators_in_price_data.main(company)
		utils.print_loading(count, len(set_of_companies), company)
		count += 1

	companies_with_data = set()
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = set(y.split(';'))
				companies_with_data -= {''}

	print(f'\nFrom {len(set_of_companies)} was choosen only {len(companies_with_data)} companies and historical data for choosen companies was collected.')

# in case of testing:
if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
	#	utils.clear_all_about_collected_price_data()
		main(conn)
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

