from fonction_niveaux1 import fonction_niveaux, Client
from ezxt import WrappedBinanceClient
import pandas as pd
import plotly.graph_objects as go
from binance.client import Client

## Initialisation ------------------------------------------------------------------------------------------------

#client = WrappedBinanceClient()

#data = client.load_ohlcv("ETH/USDT", "1h", 1659343415000, 25+30*24, True, 100)


client = Client()
data = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1HOUR, "01 september 2022","29 september 2022" )


## Boucle de backtest -------------------------------------------------------------------------------------------

for i in range(round(len(data)/24)):

    data2=data[0+i*24:24+i*24]

    srs, srr, bandehaute, bandebasse = fonction_niveaux(data2)




    """fig = go.Figure(data=[go.Candlestick(x=data2.index,
                                         open=data2['open'],
                                         high=data2['high'],
                                         low=data2['low'],
                                         close=data2['close'])])"""

    fig = go.Figure(data=[go.Candlestick(x=data2['Date'],
                                         open=data2['open'],
                                         high=data2['high'],
                                         low=data2['low'],
                                         close=data2['close'])])

    """fig.add_shape(type="line",
                  x0=data2.index[0], y0=avgl, x1=data2.index[24], y1=avgl,
                  line=dict(color="Blue", width=3, dash='dashdot'))

    fig.add_shape(type="line",
                  x0=data2.index[0], y0=avgh, x1=data2.index[24], y1=avgh,
                  line=dict(color="Blue", width=3, dash='dashdot'))"""

    """if srs2:

        if len(srs2) == 1:
            fig.add_shape(type='rect', x0=data2.index[0], y0=srs[0][1],
                          x1=data2.index[len(data2) - 1],
                          y1=srs[0][1] + amplitudebande / 10,
                          line=dict(color="green", width=3),
                          fillcolor="lightgreen", opacity=0.5)
        else:
            mins = srs2.index(min(srs2))
            maxs = srs2.index(max(srs2))
            rectsrs = [srs[mins], srs[maxs]]

            fig.add_shape(type='rect', x0=data2.index[0], y0=rectsrs[0][1],
                          x1=data2.index[len(data2) - 1],
                          y1=rectsrs[1][1], line=dict(color="green", width=3),
                          fillcolor="lightgreen", opacity=0.5)

    if srr2:

        if len(srr2) == 1:

            fig.add_shape(type='rect', x0=data2.index[0], y0=srr[0][1],
                          x1=data2.index[len(data2) - 1],
                          y1=srr[0][1] - amplitudebande / 10,
                          line=dict(color="red", width=3),
                          fillcolor="rosybrown", opacity=0.5)

        else:

            minr = srr2.index(min(srr2))
            maxr = srr2.index(max(srr2))
            rectsrr = [srr[minr], srr[maxr]]

            fig.add_shape(type='rect', x0=data2.index[0], y0=rectsrr[0][1],
                          x1=data2.index[len(data2) - 1],
                          y1=rectsrr[1][1], line=dict(color="red", width=3),
                          fillcolor="rosybrown", opacity=0.5)"""



    for i in srr:

        fig.add_shape(type="line",
                      x0=data2.index[0], y0=i[1], x1=data2.index[24], y1=i[1],
                      line=dict(color="rosybrown", width=3, dash='dashdot'))

    for i in srs:

        fig.add_shape(type="line",
                      x0=data2.index[0], y0=i[1], x1=data2.index[24], y1=i[1],
                      line=dict(color="green", width=3, dash='dashdot'))

    fig.update_xaxes(range=[data2.index[0], data2.index[len(data2) - 1]])

    fig.show()


