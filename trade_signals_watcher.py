def buy(row, K_level=None, D_level=None, KD_difference=None):	# levels - turple(min, max)

	date = row[0]
	open_price = float(row[1])
	high_price = float(row[2])
	low_price = float(row[3])
	close_price = float(row[4])
	volume = int(row[5])
	K = float(row[6])
	D = float(row[7])

	if K == -1 or D == -1:
		return (0, 0)
	else:
	# K_level only matters
		if K_level != None and D_level == None and KD_difference == None:
			if K_level[0] <= K <= K_level[1]:
				return ('buy', 'MKT')
	# D_level only matters
		if K_level == None and D_level != None and KD_difference == None:
			if D_level[0] <= D <= D_level[1]:
				return ('buy', 'MKT')
	# KD_difference only matters
		if K_level == None and D_level == None and KD_difference != None:
			if KD_difference != 0:
				if (int(K - D) / 5) * KD_difference > 0:
					return ('buy', 'MKT')
			elif KD_difference == 0:
				if (int(K - D) / 5) == 0:
					return ('buy', 'MKT')
	# K_level and D_level only matters
		if K_level != None and D_level != None and KD_difference == None:
			if K_level[0] <= K <= K_level[1]:
				if D_level[0] <= D <= D_level[1]:
					return ('buy', 'MKT')
	# K_level and KD_difference only matters
		if K_level != None and D_level == None and KD_difference != None:
			if K_level[0] <= K <= K_level[1]:
				if KD_difference != 0:
					if (int(K - D) / 5) * KD_difference > 0:
						return ('buy', 'MKT')
				elif KD_difference == 0:
					if (int(K - D) / 5) == 0:
						return ('buy', 'MKT')
	# D_level and KD_difference only matters
		if K_level == None and D_level != None and KD_difference != None:
			if D_level[0] <= D <= D_level[1]:
				if KD_difference != 0:
					if (int(K - D) / 5) * KD_difference > 0:
						return ('buy', 'MKT')
				elif KD_difference == 0:
					if (int(K - D) / 5) == 0:
						return ('buy', 'MKT')
	# all parameters matters
		if K_level != None and D_level != None and KD_difference != None:
			if K_level[0] <= K <= K_level[1]:
				if D_level[0] <= D <= D_level[1]:
					if KD_difference != 0:
						if (int(K - D) / 5) * KD_difference > 0:
							return ('buy', 'MKT')
					elif KD_difference == 0:
						if (int(K - D) / 5) == 0:
							return ('buy', 'MKT')

		return (0, 0)

def sell(row, K_level=None, D_level=None, KD_difference=None):

	date = row[0]
	open_price = float(row[1])
	high_price = float(row[2])
	low_price = float(row[3])
	close_price = float(row[4])
	volume = int(row[5])
	K = float(row[6])
	D = float(row[7])

	if K == -1 or D == -1:
		return (0, 0)
	else:	
	# K_level only matters
		if K_level != None and D_level == None and KD_difference == None:
			if K_level[0] <= K <= K_level[1]:
				return ('sell', 'MKT')
	# D_level only matters
		if K_level == None and D_level != None and KD_difference == None:
			if D_level[0] <= D <= D_level[1]:
				return ('sell', 'MKT')
	# KD_difference only matters
		if K_level == None and D_level == None and KD_difference != None:
			if KD_difference != 0:
				if (int(K - D) / 5) * KD_difference > 0:
					return ('sell', 'MKT')
			elif KD_difference == 0:
				if (int(K - D) / 5) == 0:
					return ('sell', 'MKT')
	# K_level and D_level only matters
		if K_level != None and D_level != None and KD_difference == None:
			if K_level[0] <= K <= K_level[1]:
				if D_level[0] <= D <= D_level[1]:
					return ('sell', 'MKT')
	# K_level and KD_difference only matters
		if K_level != None and D_level == None and KD_difference != None:
			if K_level[0] <= K <= K_level[1]:
				if KD_difference != 0:
					if (int(K - D) / 5) * KD_difference > 0:
						return ('sell', 'MKT')
				elif KD_difference == 0:
					if (int(K - D) / 5) == 0:
						return ('sell', 'MKT')
	# D_level and KD_difference only matters
		if K_level == None and D_level != None and KD_difference != None:
			if D_level[0] <= D <= D_level[1]:
				if KD_difference != 0:
					if (int(K - D) / 5) * KD_difference > 0:
						return ('sell', 'MKT')
				elif KD_difference == 0:
					if (int(K - D) / 5) == 0:
						return ('sell', 'MKT')
	# all parameters matters
		if K_level != None and D_level != None and KD_difference != None:
			if K_level[0] <= K <= K_level[1]:
				if D_level[0] <= D <= D_level[1]:
					if KD_difference != 0:
						if (int(K - D) / 5) * KD_difference > 0:
							return ('sell', 'MKT')
					elif KD_difference == 0:
						if (int(K - D) / 5) == 0:
							return ('sell', 'MKT')

		return (0, 0)

