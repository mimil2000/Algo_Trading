import vectorbt as vbt
import datetime
import numpy as np

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=10)

btc_price = vbt.YFData.download(
    'BTC-USD',
    interval='60m',
    start=start_date,
    end=end_date,
    missing_index='drop').get('Close')

rsi = vbt.RSI.run(btc_price, window=14)


def custom_indicator(close, rsi_window=14, ma_window = 50):
    rsi = vbt.RSI.run(close, window=rsi_window).rsi.to_numpy()
    ma = vbt.MA.run(close, ma_window).ma.to_numpy()
    trend = np.where(rsi>70, -1, 0)
    trend = np.where(rsi<30, 1, 0)
    return trend


indic = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["rsi_window","ma_window"],
    output_names=["value"]
).from_apply_func(custom_indicator, rsi_window=21, ma_window=50)

res = indic.run(btc_price,
                rsi_window=21,
                ma_window = 50)


print(res.value)

#
# entries = rsi.rsi_crossed_below(30)
# exits = rsi.rsi_crossed_above(70)

# pf = vbt.Portfolio.from_signals(btc_price,entries,exits)


# print(pf.stats())
#
# pf.plot().show()
# print()
