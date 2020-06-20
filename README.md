## TWS Trader
This project is my trading algorithm.

# Installation
1. Clone this repository:
    ```bash
    https://github.com/SGalich/tws_trader.git
    ```
2. Create virtual environment:
    ```bash
    python3 -m venv env
    ```
3. Activate this environment:
	```bash
	source env/bin/activate
	```
4. Install requirements:
	```bash
	python3 -m pip install -r requirements.txt
	```
5. Install IbPy 2 to work w/ TWS API:
	```bash
	python3 -m pip install IbPy2
	```
6. Than install IB Getaway. You can do it from [here](https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-macosx-x64.dmg).

7. Install API source from [here](http://interactivebrokers.github.io/). Installation instructions are in
the README.md inside the downloaded package. Or you can copy downloaded package inside your project's dir
and run this commands:
    ```
   cd twsapi_macunix/IBJts/source/pythonclient/ && \
   python3 setup.py sdist && \
   python3 setup.py bdist_wheel && \
   python3 -m pip install --upgrade dist/ibapi-9.76.1-py3-none-any.whl && \
   cd ../../../.. && rm -rf twsapi_macunix
   ```
You should change ibapi version from 9.76.1 to those you've downloaded.

8. Create settings.py file with this variables:
	```python3
	from ib.opt import Connection
	ACCOUNT_NUMBER = '123456' # your account number
	TWS_CONNECTION = Connection.create(port=7496, clientId=0)   # your port from TWS settings
	company = 'AAPL' # company you would like to trade with
	```
# Main goal
My purpose is to analyse option prices and trade options w/ low risks and
high potential profits.
