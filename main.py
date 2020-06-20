
from settings.py import PORT, CLIENT_ID


TWS_CONNECTION = Connection.create(port=PORT, clientId=CLIENT_ID)  # your port from TWS settings



def main():
	pass


if __name__ == "__main__":
	try:
		main()
	except(KeyboardInterrupt):
		print('\nBye!')
	except():
		print('ERROR!')

