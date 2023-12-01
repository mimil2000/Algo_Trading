"Description de la stratgégie :
"timeframe 3 min / croisement des EMA15 et EMA 100"
"Dur de filtrer les mouvements de range qui viennent poluer  "

import ta
import pandas as pd
from binance.client import Client
import matplotlib.pyplot as plt

def get_data_from_binance(start_date, end_date, step, devise):
    client = Client()
    price_curve = client.get_historical_klines(devise, step, start_date, end_date)
    df = pd.DataFrame(price_curve, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                     'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['open'] = pd.to_numeric(df['open'])
    df['volume'] = pd.to_numeric(df['volume'])
    df.index = pd.to_datetime(df['timestamp'], unit='ms')
    del df['timestamp']
    return df

def add_ema_to_df(df, period):
    df[f'ema{period}'] = ta.trend._ema(df['close'], period)
    return df

def add_sma_to_df(df, period):
    df[f'sma{period}'] = ta.trend._sma(df['close'], period)
    return df

def open_long_position(position):
    return position['ema100'] < position['ema15'] and position['ema100'] < position['ema30']  and position['ema15'] > position['ema30']  #and position['open'] > position['ema15']

def open_short_position(position):
    return position['ema100'] > position['ema15'] and position['ema100'] > position['ema30']  and  position['ema15'] < position['ema30'] #and position['open'] < position['ema15']

def close_long_position(position):
    return position['ema30'] < position['ema100'] #position['close'] < position['ema30']

def close_short_position(position):
    return position['ema30'] > position['ema100'] #position['close'] > position['ema30']

class Wallet:
    def __init__(self, initial_usdt):
        self.usdt = initial_usdt
        self.initalWallet = self.usdt
        self.coin = 0
        self.valo = initial_usdt
        self.fee = 0.0007
        self.maker_fee = 0.0002
        self.last_ath = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.buy_price = None


if '__main__':
    start = '2023-11-01'
    end = '2023-11-03'
    data = get_data_from_binance(start, end, Client.KLINE_INTERVAL_3MINUTE, "BTCUSDT")
    data = add_ema_to_df(data, 200)
    data = add_ema_to_df(data, 50)
    data=data[-4800:]

##### Boucle de Backtest ######

    wallet=Wallet(1000)
    orderpossible = True
    dt = pd.DataFrame(columns=['date','position', 'price', 'usdt', 'coins', 'valo', 'drawBack'])
    entry_times = []
    exit_times = []
    entry_prices = []
    exit_prices = []


    for time in data.iterrows():

        position={'date': time[0],'open' : time[1][0], 'high' : time[1][1], 'low' : time[1][2], 'close' : time[1][3], 'ema30' : time[1][11],  'ema15' : time[1][12], 'ema100' : time[1][13]}

        if orderpossible :

            if open_short_position(position) and wallet.usdt > 0:

                orderpossible = False

                wallet.coin = - wallet.usdt / position['close']
                # wallet.frais = - wallet.fee * wallet.coin * position['close']
                wallet.usdt = wallet.usdt - wallet.coin * position['close']
                # wallet.valo = wallet.usdt-wallet.frais
                wallet.sellPrice = position['close']

                entry_times.append(position['date'])
                entry_prices.append(position['close'])


                if wallet.valo > wallet.last_ath:
                    wallet.last_ath = wallet.valo

                myrow = {'date': position['date'], 'position': "Buy Short",
                         'price': position['close'],
                         'usdt': wallet.usdt, 'coins': wallet.coin, 'valo': wallet.valo,
                         'drawBack': (wallet.valo - wallet.last_ath) / wallet.last_ath}
                dt = dt.append(myrow, ignore_index=True)

        else:

            if close_short_position(position) and wallet.coin < 0 :

                orderpossible = True

                wallet.usdt = wallet.usdt + wallet.coin * position['close']
                # wallet.frais = - wallet.fee * wallet.coin * position['close']
                # wallet.usdt = wallet.usdt - wallet.frais
                wallet.coin = 0
                wallet.valo = wallet.usdt

                exit_times.append(position['date'])
                exit_prices.append(position['close'])

                if wallet.valo > wallet.last_ath:
                    wallet.last_ath = wallet.valo

                myrow = {'date': position['date'],'position': "Sell Short",
                         'price': position['close'], 'usdt': wallet.usdt, 'coins': wallet.coin,
                         'valo': wallet.valo, 'drawBack': (wallet.valo - wallet.last_ath) / wallet.last_ath}
                dt = dt.append(myrow, ignore_index=True)



### Résultats ###

    dt['resultat'] = dt['valo'] - dt['valo'].shift(2)

    dt['resultat%'] = ((dt['valo'] - dt['valo'].shift(2)) / dt['valo'].shift(2)) * 100


    dt.loc[dt['position'] == 'Buy Short', 'resultat'] = None
    dt.loc[dt['position'] == 'Buy Long', 'resultat%'] = None

    dt['tradeIs'] = None

    dt.loc[dt['resultat'] > 0, 'tradeIs'] = 'Good'
    dt.loc[dt['resultat'] <= 0, 'tradeIs'] = 'Bad'

    iniClose = data.iloc[0]['close']
    lastClose = data.iloc[len(data)-1]['close']
    holdPorcentage = ((lastClose - iniClose) / iniClose) * 100
    algoPorcentage = ((wallet.valo - wallet.initalWallet) / wallet.initalWallet) * 100
    vsHoldPorcentage = ((algoPorcentage - holdPorcentage))


print("Starting balance : 1000 $")
print("Final balance :",round(wallet.valo,2),"$")
print("Algo Performance:",round(algoPorcentage,2),"%")
print("Buy and Hold Performance :",round(holdPorcentage,2),"%")
print("Algo vs Buy and Hold :",round(vsHoldPorcentage,2),"%")
x=len([x for x in dt["tradeIs"] if x == "Good"])
y=len([x for x in dt["tradeIs"] if x == "Bad"])
print("Number positive trades:" , x )
print("Number negative trades:" , y )

dt['resultat%'] = pd.to_numeric(dt['resultat%'], errors='coerce')

if x!=0 :
    print("Average Positive Trades : ",round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].sum() / dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].count(),2), "%")
    idbest = dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].idxmax()
    print("Best trade +" + str(round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].max(), 2)), "%, the ",
          dt['date'][idbest])
else :
    print("Average Positive Trades : ", 0)
if y!=0:
    print("Average Negative Trades : ",round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].sum() / dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].count(),2), "%")
    idworst = dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].idxmin()
    print("Worst trade", round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].min(), 2), "%, the ", dt['date'][idworst])
else :
    print("Average Negative Trades : ", 0)
print("Worst drawBack", str(100*round(dt['drawBack'].min(),2)),"%")
# print("Total fee : ",round(dt['frais'].sum(),2),"$")


plt.figure(figsize=(12, 6))
plt.plot(data.index, data['close'], label='Prix de clôture', linewidth=1)
plt.plot(data.index, data['ema30'], label='EMA30', linewidth=1)
plt.plot(data.index, data['ema15'], label='EMA15', linewidth=1)
plt.plot(data.index, data['ema100'], label='EMA100', linewidth=1)
plt.scatter(entry_times, entry_prices, marker='^', color='g', label='Entrée de position', s=100)
plt.scatter(exit_times, exit_prices, marker='v', color='r', label='Sortie de position', s=100)
plt.title('Courbe de prix avec entrée/sortie de position')
plt.xlabel('Date')
plt.ylabel('Prix de clôture')
plt.legend()

# Affichez le graphique
plt.show()

breakpoint()



