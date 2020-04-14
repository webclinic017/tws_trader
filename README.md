## TWS Trader
This project is my trading algorithm.

# Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/SVGalich/tws_trader/tree/version_2
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
	pip3 install -r requirements.txt
	```
5. Install IbPy 2 to work w/ TWS API:
	```bash
	pip3 install IbPy2
	```
6. Than install TWS, open it and go through authetication. Download TWS from here: 
https://www.interactivebrokers.com/en/index.php?f=14099#tws-software

7. Create settings.py file with this variables:
	```python3
	from ib.opt import Connection
	ACCOUNT_NUMBER = '123456' # your account number
	TWS_CONNECTION = Connection.create(port=7496, clientId=0)   # your port from TWS settings
	company = 'AAPL' # company you would like to trade with
	```
# Main goal
My purpose is to analyse option prices and trade options w/ low risks and
high potential profits.
