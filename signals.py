# HOW TO IMPORT ALL MODULES FROM INDICATORS AND THEN REFERENCE TO EACH OF IT ???!!!
from os.path import dirname, basename, join
import glob
modules = glob.glob(join(dirname(__file__), 'indicators', '*.py'))
all_indicators = [basename(f)[:-3] for f in modules if f.endswith('.py') and not f.endswith('__init__.py')]
# for module in all:
# 	__import__(f'indicators.{module}', globals())
#
#  ... ind_signal = getattr(globals()[f'{indicator}'], 'signal')(price_data, strategy_indicators[f'{indicator}'])

from indicators import japanese_candlesticks
from indicators import RS
from indicators import SMA
from indicators import stochastic
from indicators import volume_profile
from indicators import weekday


def check(price_data, strategy_indicators):
	signal = 0
	for indicator in all_indicators:
		ind_signal = getattr(globals()[f'{indicator}'], 'signal')(price_data, strategy_indicators[f'{indicator}'])
		ind_weight = strategy_indicators[f'{indicator}']['weight']
		signal += ind_signal * ind_weight
	quantity_of_indicators = len(all_indicators)
	if signal >= quantity_of_indicators:
		return 'buy'
	if signal <= -quantity_of_indicators:
		return 'sell'
	else:
		return 0.
