import csv
import time

from ib.opt import Connection

import stochastic
import updater

def get_watchlists():	# Make a set of companies (from pre-signal)
	watchlist_to_buy = set()
	watchlist_to_sell = set()
	with open(f'Stoch_watchlist_to_buy.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				watchlist_to_buy = set(y.split(';'))
				watchlist_to_buy -= {''}
	with open(f'Stoch_watchlist_to_sell.csv', 'r', encoding='utf-8') as file:
		for x in csv.reader(file):
			for y in x:
				watchlist_to_sell = set(y.split(';'))
				watchlist_to_sell -= {''}
	return (watchlist_to_buy, watchlist_to_sell)

def stoch_real_signal_to_buy(set_of_companies):
	companies_to_buy_now = set()
	for company in set_of_companies:
		if stochastic.main(company)[0] - stochastic.main(company)[1] >= 4:	# %K > %D
			companies_to_buy_now.add(company)
	return companies_to_buy_now

def stoch_real_signal_to_sell(set_of_companies):
	companies_to_sell_now = set()
	for company in set_of_companies:
		if stochastic.main(company)[1] - stochastic.main(company)[0] >= 4:	# %K < %D
			companies_to_sell_now.add(company)
	return companies_to_sell_now

def main(conn):
	watchlist_to_buy = get_watchlists()[0]
	watchlist_to_sell = get_watchlists()[1]
	watchlists = watchlist_to_buy | watchlist_to_sell
	
	updater.main(conn, watchlists)
	companies_to_buy_now = stoch_real_signal_to_buy(watchlist_to_buy)
	companies_to_sell_now = stoch_real_signal_to_sell(watchlist_to_sell)
	return (companies_to_buy_now, companies_to_sell_now)

# In case of testing:
if __name__ == '__main__':
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

