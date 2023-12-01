import matplotlib.pyplot as plt

from fonction_niveaux2 import fonction_niveaux2
from ezxt import WrappedBinanceClient
import plotly.graph_objects as go
import pandas as pd
import ta.volatility
import numpy as np
from binance.client import Client


## Initialisation ------------------------------------------------------------------------------------------------

"""client = WrappedBinanceClient()

nbpoints=25+10*24

data = client.load_ohlcv("ETH/USDT", "1h", 1659343415000, nbpoints, True, 100)"""

client = Client()

data = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1HOUR, "01 january 2022","30 january 2022" )

df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                     'trades','tb_base_av', 'tb_quote_av', 'ignore'])

df['close'] = pd.to_numeric(df['close'])
df['high'] = pd.to_numeric(df['high'])
df['low'] = pd.to_numeric(df['low'])
df['open'] = pd.to_numeric(df['open'])
df['volume'] = pd.to_numeric(df['volume'])
df['Log returns'] = np.log(df['close'] / df['close'].shift())
df['HIGH_BOL_BAND'] = ta.volatility.bollinger_hband(df['close'], 20, 2)
df['LOW_BOL_BAND'] = ta.volatility.bollinger_lband(df['close'], 20, 2)

df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index, unit='ms')
del df['timestamp']


## Affichage test figure -------------------------------------------------------------------------------------------

for i in range(round(len(df)/24)-1):

    data2=df.iloc[0+(i+1)*24:24+(i+1)*24]

    xaxe = []
    for i in range(24):
        xaxe.append(data2.index[i])

    srs, srr, bandehaute, bandebasse= fonction_niveaux2(data2)

    fig = go.Figure(data=[go.Candlestick(x=data2.index,
                                         open=data2['open'],
                                         high=data2['high'],
                                         low=data2['low'],
                                         close=data2['close'])])

    for j in srr:

        fig.add_shape(type="line",
                      x0=data2.index[0], y0=j[1], x1=data2.index[23], y1=j[1],
                      line=dict(color="rosybrown", width=3))

    for k in srs:

        fig.add_shape(type="line",
                      x0=data2.index[0], y0=k[1], x1=data2.index[23], y1=k[1],
                      line=dict(color="green", width=3))


    fig.add_trace(go.Scatter(x=xaxe, y=bandehaute, line=dict(color="blue", width=3, dash='dashdot')))

    fig.add_trace(go.Scatter(x=xaxe, y=bandebasse, line=dict(color="blue", width=3, dash='dashdot')))

    fig.update_xaxes(range=[data2.index[0], data2.index[len(data2) - 1]])

    fig.show()

## Programme trading-----------------------------------------------------







