from indicators import stochastic, weekday, volume_profile


def signal(list_with_price_data, historical_volume_profile, strategy):
	last_row = list_with_price_data[-1]
	stoch_signal = stochastic.signal(last_row,
									strategy['K_level_to_buy'], strategy['D_level_to_buy'], strategy['KD_difference_to_buy'],
									strategy['K_level_to_sell'], strategy['D_level_to_sell'], strategy['KD_difference_to_sell']
									)
	weekday_signal = weekday.signal(last_row,
										strategy['Weekday_buy'],
										strategy['Weekday_sell'])
	volume_profile_signal = volume_profile.signal(last_row,
													historical_volume_profile,
													strategy['Volume_profile_locator'])
	# if weekday_signal == 0:
	# 	weekday_signal = 'buy'
	# if volume_profile_signal == 0:
	# 	volume_profile_signal = 'buy'

# And-and
	if strategy['Indicators_combination'] == 'S*W*V':
		if set((stoch_signal, weekday_signal, volume_profile_signal)) == {'buy',}:
			return 'buy'
		if set((stoch_signal, weekday_signal, volume_profile_signal)) == {'sell',}:
			return 'sell'
# Or-and
	if strategy['Indicators_combination'] == 'S+W*V':
		if stoch_signal == 'buy' or set((weekday_signal, volume_profile_signal)) == {'buy',}:
			return 'buy'
		if stoch_signal == 'sell' or set((weekday_signal, volume_profile_signal)) == {'sell',}:
			return 'sell'
# And-or
	if strategy['Indicators_combination'] == 'S*W+V':
		if set((stoch_signal, weekday_signal)) == {'buy',} or volume_profile_signal == 'buy':
			return 'buy'
		if set((stoch_signal, weekday_signal)) == {'sell',} or volume_profile_signal == 'sell':
			return 'sell'
# Or-or
	if strategy['Indicators_combination'] == 'S+W+V':
		if 'buy' in (stoch_signal, weekday_signal, volume_profile_signal):
			return 'buy'
		if 'sell' in (stoch_signal, weekday_signal, volume_profile_signal):
			return 'sell'

	return 0






