import ibapi.wrapper
import ibapi.client
import ibapi.contract
import threading
import logging
from datetime import datetime
import time

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        level=logging.INFO,
                        filename='test.log'
                        )
    wrp=ibapi.wrapper.EWrapper()
    cln=ibapi.client.EClient(wrp)
    cln.connect("127.0.0.1", 7497, 1)

    # не понимаю как работать с потоком. ИЗУЧИТЬ модуль threading!!
    if cln.isConnected():
        print("Успешно подключились к TWS")
        cln.th = threading.Thread(target=cln.run())
        cln.th.start()
        cln.th.join(timeout=5)
        time_now_for_log=datetime.now().strftime("%m/%d/%Y %I:%M %p")
        logging.info(f"Time: {time_now_for_log}, status: {cln.th.join()}")

    #ibapi.client.EClient.run() # что за метод? ИЗУЧИТЬ!

    contract = ibapi.contract.Contract()
    contract.symbol = "IBKR"
    contract.secType = "STK"
    contract.currency = "USD"
    contract.exchange = "ISLAND"

    time.sleep(60*60*24)
    cln.disconnect()

if __name__=='__main__':
    main()












