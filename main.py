# TO DO list:
# - отработать все ошибки при выполнении ордеров!!! Bracket order - !!!
	# Orders SL TP rejected by system: parent order partially or fully filled
# - если сработал SL/TP - надо отменить другой ордер (TP или SL)
# - убрать закрытие позиции, сделать 1 bracket order
# - добавить мультиинструментальность

from datetime import datetime, timedelta
import time

from indicators import volume_profile, stochastic, SMA, RS
import settings
import signals
import utils
import W4_checking_account
import W6_position_manager


def print_status(info):
	print(f'''
Time:		{time.strftime('%H:%M', time.gmtime())}                                    
Signal:		{info[0]}                                                      
Open position:	{info[1]}                                          
Price data row:	{info[2]}                                          
Order id:	{info[3]}                                               
Strategy:	{info[4]}
''')


def print_waiting():
	working_schedule = utils.get_working_shedule('30 mins')
	# reset date in time now:
	time_now_str = datetime.strftime(datetime.now(), '%H:%M')
	time_now = datetime.strptime(time_now_str, '%H:%M')
	times_to_await = []
	for sheduled_time in working_schedule:
		sheduled_time = datetime.strptime(sheduled_time, '%H:%M')
		if time_now > sheduled_time:
			sheduled_time += timedelta(days=1)
		time_to_await = sheduled_time - time_now # + timedelta(seconds=60)
		times_to_await.append(time_to_await)
	time_to_await = min(times_to_await)
	hours_to_await = time_to_await.seconds//(60*60)
	minutes_to_await = (time_to_await.seconds//60)%60
	for count in range(4):
		print(f'  The next update will be in {hours_to_await} hours {minutes_to_await} minute(s){"."*count}     ', end='')
		print('\033[F'*1)
		time.sleep(1)


def main():
	company = settings.company
	strategy = utils.the_best_known_strategy(company)
	working_schedule = utils.get_working_shedule(strategy['bar_size'])

	utils.update_price_data(company, strategy['bar_size'])
	historical_data = utils.request_historical_data(company)
	price_data = utils.get_price_data(company, strategy['bar_size'])
	price_data = utils.put_indicators_to_price_data(price_data, strategy, historical_data)

	open_position_type = W4_checking_account.what_position_is_open_now_for(company)
	time.sleep(7)
	orderId = W4_checking_account.next_valid_order_Id()
	time.sleep(3)
	available_funds = W4_checking_account.available_funds()
	time.sleep(3)

	buy_signal, sell_signal = signals.check(price_data, strategy)

	print_status(((buy_signal, sell_signal), open_position_type, price_data[-1], orderId, strategy))

	last_close_price = price_data[-1]['Close']
	quantity = int((available_funds * settings.POSITION_QUANTITY) / last_close_price)
	
	if not open_position_type:
		if buy_signal and not sell_signal:
			print(f'Buying {company}')
			action = 'buy'
			stop_loss = round(last_close_price * (1 - strategy[action]['SL'] / 100), 2)
			take_profit = round(last_close_price * (1 + strategy[action]['TP'] / 100), 2)
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
		if sell_signal and not buy_signal:
			print(f'Selling {company}')
			action = 'sell'
			stop_loss = round(last_close_price * (1 + strategy[action]['SL'] / 100), 2)
			take_profit = round(last_close_price * (1 - strategy[action]['TP'] / 100), 2)
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	if open_position_type == 'long':
		if sell_signal and not buy_signal:
			print('Closing long by signal...')
			W6_position_manager.close_position(company, orderId)
			orderId += 1
			time.sleep(30)
			action = 'sell'
			stop_loss = round(last_close_price * (1 + strategy[action]['SL'] / 100), 2)
			take_profit = round(last_close_price * (1 - strategy[action]['TP'] / 100), 2)
			print('...and open short')
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	if open_position_type == 'short':
		if buy_signal and not sell_signal:
			print('Closing short by signal...')
			W6_position_manager.close_position(company, orderId)
			orderId += 1
			time.sleep(30)
			action = 'buy'
			stop_loss = round(last_close_price * (1 - strategy[action]['SL'] / 100), 2)
			take_profit = round(last_close_price * (1 + strategy[action]['TP'] / 100), 2)
			print('...and open long')
			W6_position_manager.place_bracket_order(company, action, stop_loss, take_profit, quantity, orderId)
	time.sleep(60)
	print_waiting()
	while True:
		time_now_str = datetime.strftime(datetime.now(), '%H:%M')
		weekday = datetime.strftime(datetime.now(), '%w')
		if weekday not in ('6', '0'):
			print_waiting()
			if time_now_str in working_schedule:
				time.sleep(15)
				main()
		else:
			print('  Wait till stock exchange will be open.                  ')
			print('\033[F'*2)
			time.sleep(60)


if __name__ == "__main__":
	try:
		main()
	except(KeyboardInterrupt):
		print('\nBye!')
	except():
		print('ERROR!')

