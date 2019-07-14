from indicators import stochastic, weekday, volume_profile

# this functions get list of price data in format: [date, open, high, low, close, volume, stoch %K, stoch %D]
# and return (0, 0) or signal to buy/sell


def buy(list_with_price_data, historical_volume_profile, strategy):
	last_row = list_with_price_data[-1]
	stoch_signal = stochastic.buy_signal(last_row,
										strategy['K_level_to_buy'],
										strategy['D_level_to_buy'],
										strategy['KD_difference_to_buy'])
	weekday_signal = weekday.buy_signal(last_row,
										strategy['Weekday_buy'])
	volume_profile_signal = volume_profile.buy_signal(last_row, historical_volume_profile,
										strategy['Volume_profile_locator'])
	return (stoch_signal, weekday_signal, volume_profile_signal)


def sell(list_with_price_data, historical_volume_profile, strategy):
	last_row = list_with_price_data[-1]
	stoch_signal = stochastic.sell_signal(last_row,
										strategy['K_level_to_sell'],
										strategy['D_level_to_sell'],
										strategy['KD_difference_to_sell'])
	weekday_signal = weekday.sell_signal(last_row,
										strategy['Weekday_sell'])
	volume_profile_signal = volume_profile.sell_signal(last_row, historical_volume_profile,
										strategy['Volume_profile_locator'])
	return (stoch_signal, weekday_signal, volume_profile_signal)
	
