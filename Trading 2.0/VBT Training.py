import vectorbt as vbt
import datetime
import numpy as np
import pandas as pd

# comprendre que la sortie d'une position longue != bonne condition d'entrée pour un short.

vbt.settings['plotting']['layout']['width']=1200
vbt.settings['plotting']['layout']['height']=500

now=datetime.datetime.now()
end_date = now - datetime.timedelta(days=1)
start_date = end_date - datetime.timedelta(days=50)

btc_price = vbt.YFData.download(
    'BTC-USD',
    missing_index='drop',
    interval='30m',
    start=start_date,
    end=end_date).get('Close')

def custom_indicator(close, ma_window1, ma_window2, mstd_window, mean_window):

    ma1 = vbt.MA.run(close, ma_window1).ma.to_numpy()
    ma2 = vbt.MA.run(close, ma_window2).ma.to_numpy()

    ma1diff = pd.DataFrame(ma1).diff().values
    ma2diff = pd.DataFrame(ma2).diff().values

    mstd = vbt.MSTD.run(ma1diff, mstd_window).mstd.to_numpy()
    mean = vbt.MA.run(ma1diff, mean_window).ma.to_numpy()

    trend = np.where((ma1diff > mean + 0.5 * mstd)
                     & (ma1 > ma2)
                     & (ma1diff > 0)
                     & (ma2diff > 0)
                     & (ma2diff > mean), -1, 0)

    trend = np.where((ma1diff <= mean - 0.5 * mstd)
                     | (ma1 <= ma2), 1, trend)

    # Create a DataFrame with trend and other indicators
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

    return trend

ma1_window = 30
ma2_window = 100
mstd_window = 10
mean_window = 30

indic = vbt.IndicatorFactory(
    class_name="Combination",
    short_name="comb",
    input_names=["close"],
    param_names=["ma1_window", "ma2_window", 'mstd_window', 'mean_window'],
    output_names=["value"]
).from_apply_func(custom_indicator, ma1_window=ma1_window, ma2_window=ma2_window, mstd_window=mstd_window, mean_window=mean_window)

res = indic.run(btc_price,
                ma1_window=ma1_window,
                ma2_window=ma2_window,
                mstd_window=mstd_window,
                mean_window=mean_window,
                param_product=True)


entries = res.value == -1.0
exits = res.value == 1.0


pf = vbt.Portfolio.from_signals(btc_price,
                                # entries=entries,
                                # exits=exits,
                                short_entries=exits,
                                short_exits=entries,
                                )

ma1 = vbt.MA.run(btc_price, ma1_window)
ma2 = vbt.MA.run(btc_price, ma2_window)
ma1diff = pd.DataFrame(ma1.ma.to_numpy(), index=btc_price.index).diff()
ma2diff = pd.DataFrame(ma2.ma.to_numpy(), index=btc_price.index).diff()
mstd = vbt.MSTD.run(ma1diff, mstd_window).mstd
mean = vbt.MA.run(ma1diff, mean_window).ma
meanSTD = mean[mean_window]+0.5*mstd[mstd_window]
meanstd = mean[mean_window]-0.5*mstd[mstd_window]

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

scatter = vbt.plotting.Scatter(
    data = mstd,
    x_labels = mstd.index,
    trace_names=[f"Std{mstd_window}"],
    add_trace_kwargs=dict(row=2,col=1),
    trace_kwargs=dict(
            line=dict(color='brown', dash='dash')),
    fig=fig
)

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
            line=dict(color='black', dash='dot')),
    fig=fig
)

scatter = vbt.plotting.Scatter(
    data = meanstd,
    x_labels = meanstd.index,
    add_trace_kwargs=dict(row=2,col=1),
    trace_kwargs=dict(
        line=dict(color='black', dash='dot')),
    fig=fig
)


fig = fig.add_hline(y=0,line_color="black",row = 2,col = 1,line_width = 3)

fig.show()


print()
