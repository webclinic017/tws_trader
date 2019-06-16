import csv

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
