import csv

from indicators import stochastic
import utils


def rewrite_csv_with_prices(new_price_data, stock_ticker, bar_size):
	with open(f'historical_data/{stock_ticker} {bar_size}.csv', 'w', encoding='utf-8') as csvfile:
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


def main(stock_ticker, stoch_parameters, bar_size):
	prices = utils.get_price_data(stock_ticker, bar_size)
	prices = delete_columns_with_indicator(prices)
	prices_with_indicators = stochastic.main(prices, stoch_parameters)
	rewrite_csv_with_prices(prices_with_indicators, stock_ticker, bar_size)

# In order to testing:
if __name__ == '__main__':
	bar_size = '30 mins'
	main('EA', (19,12,5), bar_size)

