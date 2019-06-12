import csv

import stochastic

def get_companies_with_data():
	companies_with_data = set()
	with open(f'!MyCompanies.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				companies_with_data = set(y.split(';'))
				companies_with_data -= {' '}
	return companies_with_data

def stoch_for_companies_now(set_of_companies):
	stoch_for_companies_now = {}
	for company in set_of_companies:
		if company != '':
			stoch_for_companies_now[company] = stochastic.main(company)
	return stoch_for_companies_now

# D <= 20 % or D >= 80 %
def D_below_20(stoch_of_company_now):
	D_below_20_companies = set()
	for company in stoch_of_company_now:
		if stoch_of_company_now[company][1] <= 20:	# %D <= 20
			D_below_20_companies.add(company)
	return D_below_20_companies

def D_above_80(stoch_of_company_now):
	D_above_80_companies = set()
	for company in stoch_of_company_now:
		if stoch_of_company_now[company][1] >= 80:	# %D >= 80
			D_above_80_companies.add(company)
	return D_above_80_companies

# crosses:
def crossing_KD(stoch_of_company_now):
	companies_with_crossing_KD = set()
	for company in stoch_of_company_now:
		if abs(stoch_of_company_now[company][0] - stoch_of_company_now[company][1]) <= 4:	# %K == %D
			companies_with_crossing_KD.add(company)
	return companies_with_crossing_KD

def K_below_D(stoch_of_company_now):
	companies_with_crossing_KD = set()
	for company in stoch_of_company_now:
		if stoch_of_company_now[company][1] - stoch_of_company_now[company][0] >= 2:	# %K < %D
			companies_with_crossing_KD.add(company)
	return companies_with_crossing_KD

def D_below_K(stoch_of_company_now):
	companies_with_crossing_KD = set()
	for company in stoch_of_company_now:
		if stoch_of_company_now[company][0] - stoch_of_company_now[company][1] >= 2:	# %K > %D
			companies_with_crossing_KD.add(company)
	return companies_with_crossing_KD

def main():
	"""This function takes a set of companies and get out 2 sets: companies to buy and companies to sell - sets to observation in order to buy/sell
	due to stochastic oscillator. This information is pre-signal to watch for futher stochastic values.
	to BUY conditions: %K below %D and %D below 20. Real buy signal wll be at the moment when %K will cross %D (%K >= %D).
	to SELL conditions: %D below %K and %D above 80. Real sell signal wll be at the moment when %K will cross %D (%K <= %D).
	Closing positions supposes at crossing %D 80 line (for buy) or 20 (for sale).
	"""
	set_of_companies = get_companies_with_data()
	companies = stoch_for_companies_now(set_of_companies)
	interesting_to_BUY_companies = K_below_D(companies).intersection(D_below_20(companies))
	interesting_to_SELL_companies = D_below_K(companies).intersection(D_above_80(companies))
	with open(f'Stoch_watchlist_to_buy.csv', 'w', encoding='utf-8') as file:
		for company in interesting_to_BUY_companies:
			file.write(company+';')
	with open(f'Stoch_watchlist_to_sell.csv', 'w', encoding='utf-8') as file:
		for company in interesting_to_SELL_companies:
			file.write(company+';')
	return (interesting_to_BUY_companies, interesting_to_SELL_companies)

# In order to testing:
if __name__ == '__main__':
	print(main())

