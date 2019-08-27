# HOW TO IMPORT ALL MODULES FROM INDICATORS AND THEN REFERENCE TO EACH OF IT ???!!!
from os.path import dirname, basename, join
import glob

from indicators import japanese_candlesticks
from indicators import RS
from indicators import SMA
from indicators import stochastic
from indicators import volume_profile
from indicators import weekday


# Get list of all indicators
modules = glob.glob(join(dirname(__file__), 'indicators', '*.py'))
all_indicators = [basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]


def certain_signal(price_data, strategy_indicators, action):
	signal = 0.
	for indicator in all_indicators:
		ind_signal = getattr(globals()[indicator], 'signal')(price_data, strategy_indicators[f'{indicator}'], action)
		ind_weight = strategy_indicators[f'{indicator}']['weight']
		signal += ind_signal * ind_weight
	return signal


def check(price_data, strategy):
	buy_signal = certain_signal(price_data, strategy['buy'], 'buy')
	sell_signal = certain_signal(price_data, strategy['sell'], 'sell')
	quantity_of_indicators = len(all_indicators)
	if buy_signal - sell_signal >= quantity_of_indicators:
		return (True, False)
	if sell_signal - buy_signal >= quantity_of_indicators:
		return (False, True)
	return (False, False)
