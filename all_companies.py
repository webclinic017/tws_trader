import csv

def set_of_all_companies():
	all_companies=set()
	with open('companylist.csv', 'r', encoding='utf-8') as company_list:
		for line in csv.reader(company_list):
			all_companies.add(line[0].replace(' ', ''))

	useless_companies=set()
	for company in all_companies:
		for bad_symbol in ('.', '^', '~'):
				if bad_symbol in company:
					useless_companies.add(company)
	my_companies = all_companies - useless_companies

#	return my_companies

# for test only:
#	my_companies_test = set()
#	for company in my_companies:
#		if company[0] == 'A':
#			my_companies_test.add(company)
#	my_companies = my_companies_test

	return my_companies
