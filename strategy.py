class default_strategy:
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
	KD_difference_to_open = 1	# K > D: 1; K == D: 0; K < D: -1; None
	
# Close position conditions
	# Strongly recommend:
	stop_loss = 2
	take_profit = 7

	# Optional:
	K_level_to_close = None
	D_level_to_close = None
	KD_difference_to_close = -1	# K > D: 1; K == D: 0; K < D: -1; None
	strategy = (K_level_to_open,
							D_level_to_open,
							KD_difference_to_open,
							stop_loss,
							take_profit,
							K_level_to_close,
							D_level_to_close,
							KD_difference_to_close
							)

#{'profit': 175.4, 'buy_and_hold_profitability': -28.7, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': 1, 'stop_loss': 4.5, 'take_profit': 9.0, 'K_level_to_close': None, 'D_level_to_close': None, 'KD_difference_to_close': 0, 'Stoch_parameters': (3, 18, 7), 'company': 'TSLA'}

'''
FLEX
	Max profit: 49.3% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 23.5%
{'profit': 49.3, 'K_level_to_open': (20, 80), 'D_level_to_open': (20, 80), 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (20, 80), 'D_level_to_close': (20, 80), 'KD_difference_to_close': -1}

PTEN
	Max profit: 34.0% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 8.4%
{'profit': 34.0, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': -1, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (1, 20), 'D_level_to_close': None, 'KD_difference_to_close': None}

ALC
	Max profit: 12.6% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 1.3%
{'profit': 12.6, 'K_level_to_open': (20, 80), 'D_level_to_open': (80, 100), 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': None, 'D_level_to_close': (80, 100), 'KD_difference_to_close': 0}

ETM
	Max profit: 52.2% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 3.4%
{'profit': 52.2, 'K_level_to_open': (80, 100), 'D_level_to_open': None, 'KD_difference_to_open': 1, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (1, 20), 'D_level_to_close': None, 'KD_difference_to_close': None}

NAVI
	Max profit: 63.8% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 56.0%
{'profit': 63.8, 'K_level_to_open': (20, 80), 'D_level_to_open': None, 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (20, 80), 'D_level_to_close': (20, 80), 'KD_difference_to_close': 1}

ISBC
	Max profit: 17.2% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 4.4%
{'profit': 17.2, 'K_level_to_open': (80, 100), 'D_level_to_open': None, 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (80, 100), 'D_level_to_close': None, 'KD_difference_to_close': None}

DATA
	Max profit: 66.8% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 36.9%
{'profit': 66.8, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': 1, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (80, 100), 'D_level_to_close': None, 'KD_difference_to_close': None}

VIAV
	Max profit: 61.6% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
Buy and hold profitability: 32.2%
{'profit': 61.6, 'K_level_to_open': (20, 80), 'D_level_to_open': (20, 80), 'KD_difference_to_open': -1, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': None, 'D_level_to_close': (80, 100), 'KD_difference_to_close': -1}

EC
	Max profit: 43.3% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1
ПРОВЕРИТЬ!!!!!!!!!!!  Buy and hold profitability: -92.9%
{'profit': 43.3, 'K_level_to_open': (80, 100), 'D_level_to_open': None, 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': None, 'D_level_to_close': (1, 20), 'KD_difference_to_close': None}

AAPL
Buy and hold profitability: 23.9%
{'profit': 56.2, 'K_level_to_open': None, 'D_level_to_open': (40, 60), 'KD_difference_to_open': -1, 'stop_loss': 3.5, 'take_profit': 10, 'K_level_to_close': None, 'D_level_to_close': (1, 20), 'KD_difference_to_close': None}


IMTE
	Max profit: 41.8% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1



Buy and hold profitability: -90.1%

{'profit': 41.8, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': -1, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (20, 80), 'D_level_to_close': (20, 80), 'KD_difference_to_close': -1}
BPOPN
	Max profit: 31.2% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1



Buy and hold profitability: -34.9%

{'profit': 31.2, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': -1, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': (20, 80), 'D_level_to_close': (20, 80), 'KD_difference_to_close': -1}




AMH
	Max profit: 34.8% Calculating: 2, 10, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1



Buy and hold profitability: 0.3%

{'profit': 34.8, 'K_level_to_open': (20, 80), 'D_level_to_open': (20, 80), 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 10, 'K_level_to_close': None, 'D_level_to_close': (20, 80), 'KD_difference_to_close': 1}

AMD

 AMD incorrect data

NVDA
	61.8% vs. 10.5%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 10.5%

{'profit': 61.8, 'buy_and_hold_profitability': 10.5, 'K_level_to_open': (20, 80), 'D_level_to_open': None, 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 6, 'K_level_to_close': None, 'D_level_to_close': None, 'KD_difference_to_close': 0, 'company': 'NVDA'}
AMZN
	57.8% vs. 15.0%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 15.0%

{'profit': 57.8, 'buy_and_hold_profitability': 15.0, 'K_level_to_open': (20, 80), 'D_level_to_open': None, 'KD_difference_to_open': 1, 'stop_loss': 4, 'take_profit': 6, 'K_level_to_close': (20, 80), 'D_level_to_close': (20, 80), 'KD_difference_to_close': 1, 'company': 'AMZN'}
WMT
	35.5% vs. 19.7%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 19.7%

{'profit': 35.5, 'buy_and_hold_profitability': 19.7, 'K_level_to_open': (20, 80), 'D_level_to_open': (20, 80), 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 7, 'K_level_to_close': (20, 80), 'D_level_to_close': None, 'KD_difference_to_close': 1, 'company': 'WMT'}
GE

 GE incorrect data

C
	47.5% vs. 24.0%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 24.0%

{'profit': 47.5, 'buy_and_hold_profitability': 24.0, 'K_level_to_open': (20, 80), 'D_level_to_open': None, 'KD_difference_to_open': None, 'stop_loss': 4, 'take_profit': 8, 'K_level_to_close': (20, 80), 'D_level_to_close': (80, 100), 'KD_difference_to_close': None, 'company': 'C'}
KO
	25.8% vs. 2.9%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 2.9%

{'profit': 25.8, 'buy_and_hold_profitability': 2.9, 'K_level_to_open': (1, 20), 'D_level_to_open': None, 'KD_difference_to_open': None, 'stop_loss': 2, 'take_profit': 7, 'K_level_to_close': (80, 100), 'D_level_to_close': None, 'KD_difference_to_close': -1, 'company': 'KO'}
MS

 MS incorrect data

GM

 GM incorrect data

TWTR
	56.3% vs. 12.7%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 12.7%

{'profit': 56.3, 'buy_and_hold_profitability': 12.7, 'K_level_to_open': (20, 80), 'D_level_to_open': None, 'KD_difference_to_open': 1, 'stop_loss': 2, 'take_profit': 8, 'K_level_to_close': None, 'D_level_to_close': (20, 80), 'KD_difference_to_close': 0, 'company': 'TWTR'}
QQQ
	25.8% vs. 3.1%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 3.1%

{'profit': 25.8, 'buy_and_hold_profitability': 3.1, 'K_level_to_open': (20, 80), 'D_level_to_open': None, 'KD_difference_to_open': -1, 'stop_loss': 3, 'take_profit': 6, 'K_level_to_close': None, 'D_level_to_close': (1, 20), 'KD_difference_to_close': 1, 'company': 'QQQ'}
IBM
	31.9% vs. 17.8%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 17.8%

{'profit': 31.9, 'buy_and_hold_profitability': 17.8, 'K_level_to_open': None, 'D_level_to_open': (20, 80), 'KD_difference_to_open': -1, 'stop_loss': 2, 'take_profit': 8, 'K_level_to_close': None, 'D_level_to_close': None, 'KD_difference_to_close': 1, 'company': 'IBM'}
BA
	38.9% vs. 14.1%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 14.1%

{'profit': 38.9, 'buy_and_hold_profitability': 14.1, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': -1, 'stop_loss': 2, 'take_profit': 8, 'K_level_to_close': None, 'D_level_to_close': (20, 80), 'KD_difference_to_close': 0, 'company': 'BA'}
GS
	38.1% vs. 16.2%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 16.2%

{'profit': 38.1, 'buy_and_hold_profitability': 16.2, 'K_level_to_open': None, 'D_level_to_open': (1, 100), 'KD_difference_to_open': 0, 'stop_loss': 3, 'take_profit': 7, 'K_level_to_close': None, 'D_level_to_close': None, 'KD_difference_to_close': None, 'company': 'GS'}


EBAY
	64.7% vs. 38.0%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 38.0%

{'profit': 64.7, 'buy_and_hold_profitability': 38.0, 'K_level_to_open': None, 'D_level_to_open': (1, 100), 'KD_difference_to_open': 0, 'stop_loss': 3, 'take_profit': 7, 'K_level_to_close': None, 'D_level_to_close': None, 'KD_difference_to_close': None, 'company': 'EBAY'}
FB
	57.7% vs. 47.0%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 47.0%

{'profit': 57.7, 'buy_and_hold_profitability': 47.0, 'K_level_to_open': None, 'D_level_to_open': None, 'KD_difference_to_open': -1, 'stop_loss': 4, 'take_profit': 8, 'K_level_to_close': (20, 80), 'D_level_to_close': (20, 80), 'KD_difference_to_close': -1, 'company': 'FB'}
T
	337.6% vs. 189.1%. Calculating: 4, 8, (80, 100), (80, 100), 1, (80, 100), (80, 100), 1


Buy and hold profitability: 189.1%

{'profit': 337.6, 'buy_and_hold_profitability': 189.1, 'K_level_to_open': None, 'D_level_to_open': (1, 20), 'KD_difference_to_open': None, 'stop_loss': 3, 'take_profit': 6, 'K_level_to_close': (1, 20), 'D_level_to_close': None, 'KD_difference_to_close': None, 'company': 'T'}
'''















