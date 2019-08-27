import time

def signal(price_data, strategy_indicator):
	weekdays_to_buy = tuple(str(strategy_indicator['Weekday_buy']))
	weekdays_to_sell = tuple(str(strategy_indicator['Weekday_sell']))
	date = price_data[-1]['Datetime'].replace('-', '')[:8]
	date = time.strptime(date, '%Y%m%d')
	day = time.strftime("%w", date)
	if day in weekdays_to_buy and day in weekdays_to_sell:
		return 0.
	elif day in weekdays_to_buy and day not in weekdays_to_sell:
		return 1.
	elif day not in weekdays_to_buy and day in weekdays_to_sell:
		return -1.
	else:
		return 0.
