



def signal_to_open_position(row):

	date = row[0]
	open_price = float(row[1])
	high_price = float(row[2])
	low_price = float(row[3])
	close_price = float(row[4])
	volume = int(row[5])
	K = float(row[6])
	D = float(row[7])


	if K > D:
		return ('buy', 'MKT')	# 1 means buy
	return (0, 0)

def signal_to_close_position(row):

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
	return ('close', 'SL-TP', 5, 1)	# (..., ..., sl%, tp%)
	return (0, 0)		# + price: TP, SL or market























