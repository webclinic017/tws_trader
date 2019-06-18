



def signal_to_open_position(row, K_level, D_level, KD_difference):	# levels - turple(min, max)

	date = row[0]
	open_price = float(row[1])
	high_price = float(row[2])
	low_price = float(row[3])
	close_price = float(row[4])
	volume = int(row[5])
	K = float(row[6])
	D = float(row[7])
	
	if K_level[0] <= K <= K_level[1]:
		if D_level[0] <= D <= D_level[1]:
			if KD_difference != None:
				if KD_difference != 0:
					if (int(K - D) / 5) * KD_difference * 1000 > 0:
						return ('buy', 'MKT')
				elif KD_difference == 0:
					if (int(K - D) / 5) == 0:
						return ('buy', 'MKT')
			else:	# KD_difference == None
				return ('buy', 'MKT')
	return (0, 0)

def signal_to_close_position(row, sl, tp):

	date = row[0]
	open_price = float(row[1])
	high_price = float(row[2])
	low_price = float(row[3])
	close_price = float(row[4])
	volume = int(row[5])
	K = float(row[6])
	D = float(row[7])
	
	# if K < 20:
	# 	return ('close', 'MKT')
	return ('close', 'SL-TP', sl, tp)
	return (0, 0)		# + price: TP, SL or market


# KD_difference means K-D:
# K 100, D 0: 100	K > D
# K 80, D 20: 60	K > D
# K 52, D 48: 4		equal (0)
# K 48, D 52: 4		equal (0)
# K 20, D 80: -60	K < D
# K 0, D 100: -100	K < D















