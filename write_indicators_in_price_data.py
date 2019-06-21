import csv

from indicators import stochastic

def get_data(stock_ticker):
	list_with_price_data=[]
	with open(f'historical_data/{stock_ticker}.csv', 'r', encoding='utf-8') as data_file:
		for row in csv.reader(data_file, delimiter=';'):
			list_with_price_data.append(row)	# list with entire our csv-file
	return list_with_price_data

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
				row.remove(row[i])
			i -= 1
		i += 1
	return prices

def main(stock_ticker):
	prices = get_data(stock_ticker)
	prices = delete_columns_with_indicator(prices)
	prices_with_indicators = stochastic.main(prices)
	rewrite_csv_with_prices(prices_with_indicators, stock_ticker)

# In order to testing:
if __name__ == '__main__':
	main('TSLA')

