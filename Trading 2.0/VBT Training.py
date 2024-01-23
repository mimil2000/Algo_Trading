import vectorbt as vbt
import datetime
import numpy as np
import pandas as pd

end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=10)

btc_price = vbt.YFData.download(
    ['BTC-USD','ETH-USD'],
    missing_index='drop',
    interval='60m',
    start=start_date,
    end=end_date).get('Close')

rsi = vbt.RSI.run(btc_price, window=14)

def custom_indicator(close, ma_window1, ma_window2, mstd_window,mean_window):

    ma1 = vbt.MA.run(close, ma_window1).ma.to_numpy()
    ma2 = vbt.MA.run(close, ma_window2).ma.to_numpy()
    ma1diff = pd.DataFrame(ma1).diff().values
    ma2diff = pd.DataFrame(ma2).diff().values

    mstd = vbt.MSTD.run(ma1diff, mstd_window).mstd.to_numpy()
    mean = vbt.MA.run(ma1diff, mean_window).ma.to_numpy()

    trend = np.where(close <= mean + 0.5 * mstd, -1, 0)
    trend = np.where(close > mean + 0.2*mstd, 1, trend)

    return trend


indic = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["ma1_window","ma2_window",'mstd_window','mean_window'],
    output_names=["value"]
).from_apply_func(custom_indicator, ma1_window=21, ma2_window=50, mstd_window=12,mean_window=12)

res = indic.run(btc_price,
                ma1_window = [30],
                ma2_window = [100],
                mstd_window = [10],
                mean_window = [10],
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
