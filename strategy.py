
class test_strategy:
# None - does not matter

# KD_difference means K-D:
# K 100, D 0: 100	K > D
# K 80, D 20: 60	K > D
# K 52, D 48: 4		equal (0)
# K 48, D 52: 4		equal (0)
# K 20, D 80: -60	K < D
# K 0, D 100: -100	K < D

# K_level and D_level should be a turple(1,100) # not (0,100) cause if stoch can't be counted I returned 0. Now I fix it (now it should be -1), but in price data still 0

# Open position conditions
	K_level_to_open = None # turple (1,100)
	D_level_to_open = None
	KD_difference_to_open = 0	# K > D: 1; K == D: 0; K < D: -1; None
	
# Close position conditions
	# Mandatory:
	stop_loss = 1
	take_profit = 7.5

	# Optional:
	K_level_to_close = None
	D_level_to_close = None
	KD_difference_to_close = None	# K > D: 1; K == D: 0; K < D: -1; None



















