import utils


def volatility_calculate(prices):
	all_intraday_volatilities = []
	for i in range(1, 270):	# around 270 days
		high_price = float(prices[-i][2])
		low_price = float(prices[-i][3])
		intraday_volatility = abs((high_price - low_price) / low_price) * 100
		all_intraday_volatilities.append(round(intraday_volatility, 1))
	average_intraday_volatility = sum(all_intraday_volatilities) / len(all_intraday_volatilities)

	all_daily_volatilities = []
	for i in range(1, 270):	# around 270 days
		previous_close_price = float(prices[-i-1][4])
		close_price = float(prices[-i][4])
		daily_volatility = abs((previous_close_price - close_price) / close_price) * 100
		all_daily_volatilities.append(round(daily_volatility, 1))
	average_daily_volatility = sum(all_daily_volatilities) / len(all_daily_volatilities)
	return (round(average_intraday_volatility, 1), round(average_daily_volatility, 1))


def sort():
	volatility_dict = dict()
	companies = utils.set_with_my_companies()
	for company in companies:
		prices = utils.get_price_data(company)
		try:
			volatility = volatility_calculate(prices)[0]
			volatility_dict[company] = volatility
#			print(f'{company} - avg. intraday vol-ty: {volatility}%')
		except(ValueError):
#			print(f'{company} sucks!')
			continue
	
	sorted_companies = []
	for x in sorted(volatility_dict.items(), key=lambda item: item[1], reverse=True):
		sorted_companies.append(x[0])
	return sorted_companies


if __name__ == '__main__':
	print(sort()[:10])

	