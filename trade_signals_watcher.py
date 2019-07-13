from indicators import stochastic, weekday

# this functions get list of price data in format: [date, open, high, low, close, volume, stoch %K, stoch %D]
# and return (0, 0) or signal to buy/sell


def buy(row, strategy):
	stoch_signal = stochastic.buy_signal(row,
										strategy['K_level_to_buy'],
										strategy['D_level_to_buy'],
										strategy['KD_difference_to_buy'])
	weekday_signal = weekday.buy_signal(row,
										strategy['Weekday_buy'])
	return (stoch_signal, weekday_signal)


def sell(row, strategy):
	stoch_signal = stochastic.sell_signal(row,
										strategy['K_level_to_sell'],
										strategy['D_level_to_sell'],
										strategy['KD_difference_to_sell'])
	weekday_signal = weekday.sell_signal(row,
										strategy['Weekday_sell'])
	return (stoch_signal, weekday_signal)
	
