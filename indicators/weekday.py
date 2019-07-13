import time

def buy_signal(row, weekday_buy=None):
	if weekday_buy == None:
		return 'buy'
	else:
		weekday_buy = tuple(str(weekday_buy))
		day = time.strptime(row[0], '%Y%m%d  %H:%M:%S')
		weekday = time.strftime("%w", day)
		if weekday in weekday_buy:
			return 'buy'
		else:
			return 0


def sell_signal(row, weekday_sell=None):
	if weekday_sell == None:
		return 'sell'
	else:
		weekday_sell = tuple(str(weekday_sell))
		day = time.strptime(row[0], '%Y%m%d  %H:%M:%S')
		weekday = time.strftime("%w", day)
		if weekday in weekday_sell:
			return 'sell'
		else:
			return 0