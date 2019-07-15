from indicators import stochastic, weekday, volume_profile

# this functions get list of price data in format: [date, open, high, low, close, volume, stoch %K, stoch %D]
# and return (0, 0) or signal to buy/sell


def buy(list_with_price_data, historical_volume_profile, strategy):
	last_row = list_with_price_data[-1]
	stoch_signal = stochastic.buy_signal(last_row,
										strategy['K_level_to_buy'],
										strategy['D_level_to_buy'],
										strategy['KD_difference_to_buy'])
	weekday_signal = weekday.signal(last_row,
										strategy['Weekday_buy'],
										strategy['Weekday_sell'])
	volume_profile_signal = volume_profile.signal(last_row, historical_volume_profile,
										strategy['Volume_profile_locator'])
	if weekday_signal == 0:
		weekday_signal = 'buy'
	if volume_profile_signal == 0:
		volume_profile_signal = 'buy'
	return (stoch_signal, weekday_signal, volume_profile_signal)


def sell(list_with_price_data, historical_volume_profile, strategy):
	last_row = list_with_price_data[-1]
	stoch_signal = stochastic.sell_signal(last_row,
										strategy['K_level_to_sell'],
										strategy['D_level_to_sell'],
										strategy['KD_difference_to_sell'])
	weekday_signal = weekday.signal(last_row,
										strategy['Weekday_buy'],
										strategy['Weekday_sell'])
	volume_profile_signal = volume_profile.signal(last_row, historical_volume_profile,
										strategy['Volume_profile_locator'])
	if weekday_signal == 0:
		weekday_signal = 'sell'
	if volume_profile_signal == 0:
		volume_profile_signal = 'sell'
	return (stoch_signal, weekday_signal, volume_profile_signal)
	
