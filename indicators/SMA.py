def delete_columns_with_indicator(price_data): 	# m.b. with pandas.DataFrame it would be easier ?!
	for row in price_data:
		try:
			row.remove(row[8])
		except(IndexError):	# if new price_data was added without indicator's values
			continue
	return price_data


def update(price_data, SMA_period):
	# price_data = delete_columns_with_indicator(price_data)
	for row in price_data[:SMA_period - 1]:
		row.append('')
	for i, row in enumerate(price_data[SMA_period-1:]):
		sum = 0
		for rewieving_row in price_data[i:SMA_period+i]:
			close_price = rewieving_row[4]
			sum += close_price
		average = sum / SMA_period
		row.append(average)
	return price_data


def signal(price_data):
	period = 3
	try:
		previous_high = price_data[-period][2]
		previous_low = price_data[-period][3]
		previous_close = price_data[-period][4]
		previous_SMA = price_data[-period][8]
	except(IndexError):
		return 0.
	now_high = price_data[-1][2]
	now_low = price_data[-1][3]
	now_close = price_data[-1][4]
	now_SMA = price_data[-1][8]
	if previous_SMA:
		if now_low > now_SMA and previous_high < previous_SMA:
			return 1.
		if now_high < now_SMA and previous_low > previous_SMA:
			return -1.
	return 0.
