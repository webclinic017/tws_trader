from indicators import stochastic, weekday, volume_profile, japanese_candlesticks


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
	signal_4 = japanese_candlesticks.signal(price_data,
											strategy['Japanese_candlesticks'])

	weight = [float(x) for x in strategy['Indicators_combination'].split('-')]

	signal = weight[1]*signal_1 + weight[2]*signal_2 + weight[3]*signal_3 + weight[4]*signal_4
	if signal >= weight[0]:
		return 'buy'
	if signal <= -weight[0]:
		return 'sell'
	else:
		return 0.

#### WITHOUT OPPOSITE SIGNALS	
	# buy_signal_1 = None
	# buy_signal_2 = None
	# buy_signal_3 = None
	# buy_signal_4 = None
	
	# sell_signal_1 = None
	# sell_signal_2 = None
	# sell_signal_3 = None
	# sell_signal_4 = None

	# if signal_1 < 0:
	# 	buy_signal_1 = 0
	# else:
	# 	buy_signal_1 = signal_1
	# if signal_2 < 0:
	# 	buy_signal_2 = 0
	# else:
	# 	buy_signal_2 = signal_2
	# if signal_3 < 0:
	# 	buy_signal_3 = 0
	# else:
	# 	buy_signal_3 = signal_3
	# if signal_4 < 0:
	# 	buy_signal_4 = 0
	# else:
	# 	buy_signal_4 = signal_4

	# buy_signal = weight[1]*buy_signal_1 + weight[2]*buy_signal_2 + weight[3]*buy_signal_3 + weight[4]*buy_signal_4

	# if signal_1 > 0:
	# 	sell_signal_1 = 0
	# else:
	# 	sell_signal_1 = signal_1
	# if signal_2 > 0:
	# 	sell_signal_2 = 0
	# else:
	# 	sell_signal_2 = signal_2
	# if signal_3 > 0:
	# 	sell_signal_3 = 0
	# else:
	# 	sell_signal_3 = signal_3
	# if signal_4 > 0:
	# 	sell_signal_4 = 0
	# else:
	# 	sell_signal_4 = signal_4

	# sell_signal = weight[1]*sell_signal_1 + weight[2]*sell_signal_2 + weight[3]*sell_signal_3 + weight[4]*sell_signal_4

	# if buy_signal > weight[0]:
	# 	return 'buy'
	# if sell_signal < -weight[0]:
	# 	return 'sell'
	# else:
	# 	return 0


	# if strategy['Indicators_combination'] == '1*2*3*4':
	# 	if set((signal_1, signal_2, signal_3, signal_4)) == {'buy',}:
	# 		return 'buy'
	# 	if set((signal_1, signal_2, signal_3, signal_4)) == {'sell',}:
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*2*3+4':
	# 	if set((signal_1, signal_2, signal_3)) == {'buy',} or signal_4 == 'buy':
	# 		return 'buy'
	# 	if set((signal_1, signal_2, signal_3)) == {'sell',} or signal_4 == 'sell':
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*3*4+2':
	# 	if set((signal_1, signal_3, signal_4)) == {'buy',} or signal_2 == 'buy':
	# 		return 'buy'
	# 	if set((signal_1, signal_3, signal_4)) == {'sell',} or signal_2 == 'sell':
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*2*4+3':
	# 	if set((signal_1, signal_2, signal_4)) == {'buy',} or signal_3 == 'buy':
	# 		return 'buy'
	# 	if set((signal_1, signal_2, signal_4)) == {'sell',} or signal_3 == 'sell':
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '2*3*4+1':
	# 	if set((signal_2, signal_3, signal_4)) == {'buy',} or signal_1 == 'buy':
	# 		return 'buy'
	# 	if set((signal_2, signal_3, signal_4)) == {'sell',} or signal_1 == 'sell':
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*2+3*4':
	# 	if set((signal_1, signal_2)) == {'buy',} or set((signal_3, signal_4)) == {'buy',}:
	# 		return 'buy'
	# 	if set((signal_1, signal_2)) == {'sell',} or set((signal_3, signal_4)) == {'sell',}:
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*2+3+4':
	# 	if set((signal_1, signal_2)) == {'buy',} or 'buy' in (signal_3, signal_4):
	# 		return 'buy'
	# 	if set((signal_1, signal_2)) == {'sell',} or 'sell' in (signal_3, signal_4):
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*3+2*4':
	# 	if set((signal_1, signal_3)) == {'buy',} or set((signal_2, signal_4)) == {'buy',}:
	# 		return 'buy'
	# 	if set((signal_1, signal_3)) == {'sell',} or set((signal_2, signal_4)) == {'sell',}:
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*3+2+4':
	# 	if set((signal_1, signal_3)) == {'buy',} or 'buy' in (signal_2, signal_4):
	# 		return 'buy'
	# 	if set((signal_1, signal_3)) == {'sell',} or 'sell' in (signal_2, signal_4):
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*4+2*3':
	# 	if set((signal_1, signal_4)) == {'buy',} or set((signal_2, signal_3)) == {'buy',}:
	# 		return 'buy'
	# 	if set((signal_1, signal_4)) == {'sell',} or set((signal_2, signal_3)) == {'sell',}:
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1*4+2+3':
	# 	if set((signal_1, signal_4)) == {'buy',} or 'buy' in (signal_2, signal_3):
	# 		return 'buy'
	# 	if set((signal_1, signal_4)) == {'sell',} or 'sell' in (signal_2, signal_3):
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '2*3+1+4':
	# 	if set((signal_2, signal_3)) == {'buy',} or 'buy' in (signal_1, signal_4):
	# 		return 'buy'
	# 	if set((signal_2, signal_3)) == {'sell',} or 'sell' in (signal_1, signal_4):
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '2*4+1+3':
	# 	if set((signal_2, signal_4)) == {'buy',} or 'buy' in (signal_1, signal_3):
	# 		return 'buy'
	# 	if set((signal_2, signal_4)) == {'sell',} or 'sell' in (signal_1, signal_3):
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '3*4+1+2':
	# 	if set((signal_3, signal_4)) == {'buy',} or 'buy' in (signal_1, signal_2):
	# 		return 'buy'
	# 	if set((signal_3, signal_4)) == {'sell',} or 'sell' in (signal_1, signal_2):
	# 		return 'sell'
	# if strategy['Indicators_combination'] == '1+2+3+4':
	# 	if 'buy' in (signal_1, signal_2, signal_3, signal_4):
	# 		return 'buy'
	# 	if 'sell' in (signal_1, signal_2, signal_3, signal_4):
	# 		return 'sell'
	# return 0






