from .settings import PORT, CLIENT_ID
from ibapi.client import EClient
from ibapi.wrapper import EWrapper


class IBapi(EWrapper, EClient):
	def __init__(self):
		EClient.__init__(self, self)


app = IBapi()
app.connect('127.0.0.1', PORT, CLIENT_ID)
app.run()

'''
#Uncomment this section if unable to connect
#and to prevent errors on a reconnect
import time
time.sleep(2)
app.disconnect()
'''

# TWS_CONNECTION = Connection.create(port=PORT, clientId=CLIENT_ID)  # your port from TWS settings


def main():
	pass


if __name__ == "__main__":
	try:
		main()
	except(KeyboardInterrupt):
		print('\nBye!')
	except():
		print('ERROR!')
