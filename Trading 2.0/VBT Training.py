import vectorbt as vbt
import datetime
import numpy as np

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=10)

btc_price = vbt.YFData.download(
    ['BTC-USD','ETH-USD'],
    missing_index='drop',
    interval='60m',
    start=start_date,
    end=end_date).get('Close')

rsi = vbt.RSI.run(btc_price, window=14)

def custom_indicator(close, rsi_window, ma_window):
    rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()
    ma = vbt.MA.run(close, ma_window).ma.to_numpy()
    trend = np.where(rsi > 70, -1, 0)
    trend = np.where( (rsi < 30) & (close<ma), 1, trend)
    return trend


indic = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["rsi_window","ma_window"],
    output_names=["value"]
).from_apply_func(custom_indicator, rsi_window=21, ma_window=50)

res = indic.run(btc_price,
                rsi_window = [10,20,30],
                ma_window = [20,50,200],
                param_product=True)


# print(res.value)

entries = res.value == 1.0
exits = res.value == -1.0

#
# entries = rsi.rsi_crossed_below(30)
# exits = rsi.rsi_crossed_above(70)

pf = vbt.Portfolio.from_signals(btc_price,entries,exits)

print(pf.total_return()>0)

# print(pf.stats())
#
# pf.plot().show()
# print()
