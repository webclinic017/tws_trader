import time

def signal(price_data, strategy_indicator, *args):
	weekday = tuple(str(strategy_indicator['weekday']))
	date = price_data[-1]['Datetime'].replace('-', '')[:8]
	date = time.strptime(date, '%Y%m%d')
	day = time.strftime("%w", date)
	if day in weekday:
		return 1.
	return 0.
