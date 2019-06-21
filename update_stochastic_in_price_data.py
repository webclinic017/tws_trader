import csv

from indicators import stochastic
import utils


def rewrite_csv_with_prices(new_price_data, stock_ticker):
	with open(f'historical_data/{stock_ticker}.csv', 'w', encoding='utf-8') as csvfile:
		a = csv.writer(csvfile, delimiter=';')
		for row in new_price_data:
			a.writerow(row)


def delete_columns_with_indicator(prices): 	# m.b. with pandas.DataFrame it would be easier ?!
	i = 0	# column number
	for title in range(0,len(prices[0])):
		title = prices[0][i]
		if '%' in title:
			x = 0	# row number
			for row in prices:
				try:
					row.remove(row[i])
				except(IndexError):	# if new prices was added without indicator's values
					continue
			i -= 1
		i += 1
	return prices


def main(stock_ticker, parameters=(26, 26, 9)):
	prices = utils.get_price_data(stock_ticker)
	prices = delete_columns_with_indicator(prices)
	prices_with_indicators = stochastic.main(prices, parameters)
	rewrite_csv_with_prices(prices_with_indicators, stock_ticker)

# In order to testing:
if __name__ == '__main__':
	main('EA')
