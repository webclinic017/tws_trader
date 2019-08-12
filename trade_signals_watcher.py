from indicators import stochastic, weekday, volume_profile, japanese_candlesticks, SMA


def signal(price_data, historical_volume_profile, strategy):
	last_row = price_data[-1]
	last_datetime = price_data[-1][0][:10]
	signal_1 = stochastic.signal(last_row,
									strategy['K_level_to_buy'], strategy['D_level_to_buy'], strategy['KD_difference_to_buy'],
									strategy['K_level_to_sell'], strategy['D_level_to_sell'], strategy['KD_difference_to_sell']
									)
	signal_2 = weekday.signal(last_datetime,
										strategy['Weekday_buy'],
										strategy['Weekday_sell'])
	signal_3 = volume_profile.signal(last_row,
													historical_volume_profile,
													strategy['Volume_profile_locator'])
	signal_4 = japanese_candlesticks.signal(price_data)

	signal_5 = SMA.signal(price_data)

	weight = [float(x) for x in strategy['Indicators_combination'].split('-')]
	signal = weight[1]*signal_1 + weight[2]*signal_2 + weight[3]*signal_3 + weight[4]*signal_4 + weight[5]*signal_5

	if signal >= weight[0]:
		return 'buy'
	if signal <= -weight[0]:
		return 'sell'
	else:
		return 0.
