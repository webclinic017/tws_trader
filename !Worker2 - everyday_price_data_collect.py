from ib.opt import Connection

import updater

def main(c):
	while True:
		updater.main(c)	 # N.B.: 2 D updating depth!

if __name__ == "__main__":
	conn = Connection.create(port=7497, clientId=0)
	conn.connect()
	try:
		main(conn)
	except(KeyboardInterrupt):
		print('Bye!')
		conn.disconnect()
	except():
		print('ERROR!')
		conn.disconnect()

