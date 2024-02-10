import vectorbt as vbt
import datetime
import numpy as np
import pandas as pd

# regarder pour bloquer à un trade maximum par croisement d'EMA

vbt.settings['plotting']['layout']['width']=1200
vbt.settings['plotting']['layout']['height']=500

now=datetime.datetime.now()
# now = pd.Timestamp(year=2024, month=1, day=10)
end_date = now - datetime.timedelta(days=0)
start_date = end_date - datetime.timedelta(days=10)

# end_date = pd.Timestamp(year=2024, month=1, day=4)
# start_date = pd.Timestamp(year=2024, month=1, day=1)


btc_price = vbt.BinanceData.download(
    'BTCUSDT',
    missing_index='drop',
    interval='30m',
    start=start_date,
    end=end_date).get('Close')

def custom_long_indicator(close, ma_window1, ma_window2, mstd_window, mean_window, min_entry_delay=12):

    ma1 = vbt.MA.run(close, ma_window1).ma.to_numpy()
    ma2 = vbt.MA.run(close, ma_window2).ma.to_numpy()

    ma1diff = pd.DataFrame(ma1).diff().values
    ma2diff = pd.DataFrame(ma2).diff().values

    mstd = vbt.MSTD.run(ma1diff, mstd_window).mstd.to_numpy()
    mean = vbt.MA.run(ma1diff, mean_window).ma.to_numpy()

    trend = np.zeros_like(close)

    entry_delay_counter = 0

    for i in range(1, len(close)):
        if entry_delay_counter == 0:
            if (ma1diff[i] > mean[i] + 1.0 * mstd[i]) \
                and ma2diff[i] > mean[i] + 1.0 * mstd[i] \
                    and (ma1[i] > ma2[i]) \
                    and (ma1diff[i] > ma2diff[i]) \
                    and (ma2diff[i] > mean[i]) \
                    and (ma1diff[i] > 0) \
                    and (ma2diff[i] > 0):
                trend[i] = -1
                entry_delay_counter = min_entry_delay
        else:
            entry_delay_counter -= 1

        if (ma1diff[i] <= mean[i] - 1.0 * mstd[i]) \
                or (ma1[i] <= ma2[i]):
            trend[i] = 1
            if entry_delay_counter >=1 :
                entry_delay_counter -= 1



    df = pd.DataFrame({
        'Close': close.tolist(),
        'MA1': ma1.tolist(),
        'MA2': ma2.tolist(),
        'MA1_diff': ma1diff.tolist(),
        'MA2_diff': ma2diff.tolist(),
        'MSTD': mstd.tolist(),
        'Mean': mean.tolist(),
        'Trend': trend.tolist()
    })

    df['index']=df.index
    df.index = btc_price.index
    return trend


def custom_short_indicator(close, ma_window1, ma_window2, mstd_window, mean_window):

    ma1 = vbt.MA.run(close, ma_window1).ma.to_numpy()
    ma2 = vbt.MA.run(close, ma_window2).ma.to_numpy()

    ma1diff = pd.DataFrame(ma1).diff().values
    ma2diff = pd.DataFrame(ma2).diff().values

    mstd = vbt.MSTD.run(ma1diff, mstd_window).mstd.to_numpy()
    mean = vbt.MA.run(ma1diff, mean_window).ma.to_numpy()

    trend = np.where((ma1diff < mean - 0.5 * mstd)
                     & (ma1 < ma2)
                     & (ma1diff < 0)
                     & (ma2diff < 0), -1, 0)

    trend = np.where((ma1diff >= mean + 0.5 * mstd)
                     | (ma1 >= ma2), 1, trend)

    df = pd.DataFrame(data={
        'Close': close.tolist(),
        'MA1': ma1.tolist(),
        'MA2': ma2.tolist(),
        'MA1_diff': ma1diff.tolist(),
        'MA2_diff': ma2diff.tolist(),
        'MSTD': mstd.tolist(),
        'Mean': mean.tolist(),
        'Trend': trend.tolist()
    })

    df=df.apply(pd.Series.explode)

    df['check'] = np.where(
        (df['MA1_diff'] < df['Mean'] - 0.5 * df['MSTD']) &
        (df['MA1'] < df['MA2']) &
        (df['MA1_diff'] < 0) &
        (df['MA2_diff'] < 0),
        -1, 0
    )

    df['check'] = np.where(
        (df['MA1_diff'] < df['Mean'] - 0.5 * df['MSTD']) &
        (df['MA1'] < df['MA2']),
        1, 0
    )



    # Assuming close has an index, set the index of the DataFrame
    df.index = btc_price.index

    return trend

ma1_window = 30
ma2_window = 100
mstd_window = 10
mean_window = 30

indic_long = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["ma1_window", "ma2_window", 'mstd_window', 'mean_window'],
    output_names=["value"]
).from_apply_func(custom_long_indicator, ma1_window=ma1_window, ma2_window=ma2_window, mstd_window=mstd_window, mean_window=mean_window)

res_long = indic_long.run(btc_price,
                ma1_window=ma1_window,
                ma2_window=ma2_window,
                mstd_window=mstd_window,
                mean_window=mean_window,
                param_product=True)

indic_short = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["ma1_window", "ma2_window", 'mstd_window', 'mean_window'],
    output_names=["value"]
).from_apply_func(custom_short_indicator, ma1_window=ma1_window, ma2_window=ma2_window, mstd_window=mstd_window, mean_window=mean_window)

res_short = indic_short.run(btc_price,
                ma1_window=ma1_window,
                ma2_window=ma2_window,
                mstd_window=mstd_window,
                mean_window=mean_window,
                param_product=True)

entries_long = res_long.value == -1.0
exits_long = res_long.value == 1.0
entries_short = res_short.value == -1.0
exits_short = res_short.value == 1.0

pf = vbt.Portfolio.from_signals(btc_price,
                                entries=entries_long,
                                exits=exits_long,
                                # short_entries=entries_short,
                                # short_exits=exits_short,
                                )


ma1 = vbt.MA.run(btc_price, ma1_window)
ma2 = vbt.MA.run(btc_price, ma2_window)
ma1diff = pd.DataFrame(ma1.ma.to_numpy(), index=btc_price.index).diff()
ma2diff = pd.DataFrame(ma2.ma.to_numpy(), index=btc_price.index).diff()
mstd = vbt.MSTD.run(ma1diff, mstd_window).mstd
mean = vbt.MA.run(ma1diff, mean_window).ma
meanSTD = mean[mean_window]+1.0*mstd[mstd_window]
meanstd = mean[mean_window]-1.0*mstd[mstd_window]

fig = pf.plot(subplots=['trades',('price', dict(title='Metrics', yaxis_kwargs=dict(title='Price'))), 'trade_pnl','cum_returns','drawdowns'])

scatter = vbt.plotting.Scatter(
    data = btc_price,
    x_labels = btc_price.index,
    trace_names=["Metrics"],
    add_trace_kwargs=dict(row=1,col=1),
    fig=fig,
    trace_kwargs=dict(line=dict(color='gray'))
)

scatter = vbt.plotting.Scatter(
    data = ma1.ma,
    x_labels = ma1.ma.index,
    trace_names=[f"M{ma1_window}"],
    add_trace_kwargs=dict(row=1,col=1),
    fig=fig,
    trace_kwargs=dict(line=dict(color='orange'))
)

scatter = vbt.plotting.Scatter(
    data = ma2.ma,
    x_labels = ma2.ma.index,
    trace_names=[f"M{ma2_window}"],
    add_trace_kwargs=dict(row=1,col=1),
    fig=fig,
    trace_kwargs=dict(line=dict(color='green'))
)

scatter = vbt.plotting.Scatter(
    data = ma1diff,
    x_labels = ma1diff.index,
    trace_names=[f"M{ma1_window}diff"],
    add_trace_kwargs=dict(row=2,col=1),
    fig=fig,
    trace_kwargs = dict(line=dict(color='orange'))
)

scatter = vbt.plotting.Scatter(
    data = ma2diff,
    x_labels = ma2diff.index,
    trace_names=[f"M{ma2_window}diff"],
    add_trace_kwargs=dict(row=2,col=1),
    fig=fig,
    trace_kwargs=dict(line=dict(color='green'))
)

# scatter = vbt.plotting.Scatter(
#     data = mstd,
#     x_labels = mstd.index,
#     trace_names=[f"Std{mstd_window}"],
#     add_trace_kwargs=dict(row=2,col=1),
#     trace_kwargs=dict(
#             line=dict(color='brown', dash='dash')),
#     fig=fig
# )

scatter = vbt.plotting.Scatter(
    data = mean,
    x_labels = mean.index,
    trace_names=[f"Mean{mean_window}"],
    add_trace_kwargs=dict(row=2,col=1),
    fig=fig
)


scatter = vbt.plotting.Scatter(
    data = meanSTD,
    x_labels = meanSTD.index,
    add_trace_kwargs=dict(row=2,col=1),
    trace_kwargs=dict(
            line=dict(color='black')),
    fig=fig
)

scatter = vbt.plotting.Scatter(
    data = meanstd,
    x_labels = meanstd.index,
    add_trace_kwargs=dict(row=2,col=1),
    trace_kwargs=dict(
        line=dict(color='black')),
    fig=fig
)


fig = fig.add_hline(y=0,line_color="black",row = 2,col = 1,line_width = 3)

fig.show()


print()
