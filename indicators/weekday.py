import time

def signal(date, weekday_buy=None, weekday_sell=None):
	if weekday_buy == None:
		return 0
	else:
		weekday_buy = tuple(str(weekday_buy))
		day = None
		if '-' in date:
			day = time.strptime(date, '%Y-%m-%d')
		if '-' not in date:
			day = time.strptime(date, '%Y%m%d  ')
		weekday = time.strftime("%w", day)
		if weekday in weekday_buy:
			return 'buy'
		else:
			return 0
	if weekday_sell == None:
		return 0
	else:
		weekday_sell = tuple(str(weekday_sell))
		day = None
		if '-' in date:
			day = time.strptime(date, '%Y-%m-%d')
		if '-' not in date:
			day = time.strptime(date, '%Y%m%d  ')
		weekday = time.strftime("%w", day)
		if weekday in weekday_sell:
			return 'sell'
		else:
			return 0
	return 0

