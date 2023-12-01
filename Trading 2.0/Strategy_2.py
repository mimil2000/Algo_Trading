"Description de la stratgégie :"

import ta
import pandas as pd
from binance.client import Client
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
import mplfinance as mpf

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

def compute_derivative(data,name_column):

    if name_column not in data.columns:
        raise ValueError(f"Column '{name_column}' not found in the DataFrame.")

        # Calculer la dérivée en utilisant la méthode diff() de pandas
    derivative_column = f"{name_column}_derivative"
    data[derivative_column] = data[name_column].diff()

    return data


def smooth(data,name_column):

    if name_column not in data.columns:
        raise ValueError(f"Column '{name_column}' not found in the DataFrame.")

        # Calculer la dérivée en utilisant la méthode diff() de pandas
    smooth_column = f"{name_column}_smoothed"
    alpha = 0.15
    data[smooth_column] = data[name_column].ewm(alpha=alpha, adjust=False).mean()

    return data

def open_long_position(position):
    return position['ema30_derivative'] > (mean + std) and position['open'] > position['ema100'] and position['ema30'] - position['ema100']  > 0.2 * avg_dist

def open_short_position(position):
    return position['ema30_derivative'] <= (mean + std) #and position['open'] < position['ema15']

def close_long_position(position):
    return position['ema30_derivative'] <= 0 or position['low'] <= position['ema30']

def close_short_position(position):
    return position['ema30'] > position['ema100'] #position['close'] > position['ema30']


def show_graph(data):
    plt.figure(figsize=(12, 6))

    # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    #
    # # Tracer le graphique principal sur le premier sous-graphique
    # ax1.plot(data.index, data['close'], label='Prix de clôture', linewidth=1)
    # ax1.plot(data.index, data['ema30'], label='ema30', linewidth=1)
    # ax1.plot(data.index, data['ema100'], label='EMA100', linewidth=1)
    # ax1.set_title('Courbe de prix avec entrée/sortie de position')
    # ax1.set_ylabel('Prix de clôture')
    # ax1.legend()

    alpha = 0.15  # Vous pouvez ajuster ce paramètre en fonction de la souplesse souhaitée
    data['ema30_derivative_smoothed'] = data['ema30_derivative'].ewm(alpha=alpha, adjust=False).mean()

    # Tracer la dérivée sur le deuxième sous-graphique
    plt.plot(data.index, data['ema30_derivative'], label='Dérivée ema30', linewidth=1, color='orange')
    plt.plot(data.index, data['ema100_derivative'], label='Dérivée ema100', linewidth=1, color='blue')

    plt.plot(data.index, data['ema30_derivative_smoothed'], label='Dérivée smooth ema30', linewidth=1, color='green')


    plt.xlabel('Date')  # Corrected line
    plt.ylabel('Dérivée ema30', color='red')  # Corrected line
    plt.tick_params(axis='y', labelcolor='red')

    # Ajuster l'espacement entre les deux sous-graphiques
    plt.subplots_adjust(hspace=0.3)

    mean = data['ema30_derivative'].mean()
    std = data['ema30_derivative'].std()


    # Ajouter les constantes sur le graphique de la dérivée
    plt.axhline(0, color='green', linestyle='dashed', linewidth=1, label='Moyenne')
    plt.axhline(mean + std, color='orange', linestyle='dashed', linewidth=1, label='Moyenne + Écart-type')
    plt.axhline(mean - std, color='orange', linestyle='dashed', linewidth=1, label='Moyenne - Écart-type')

    plt.xlabel('Date')  # Corrected line
    plt.ylabel('Dérivée ema30')  # Corrected line
    plt.tick_params(axis='y', labelcolor='red')
    # plt.legend()
    plt.xlabel('Date')  # Corrected line

    # Afficher les graphiques
    return plt.show()



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


    start = datetime(2023, 11, 1)  # Définir la date de début
    end = datetime(2023, 11, 28)  # Définir la date de fin

    current_date = start

    dataframe = pd.DataFrame()



    while current_date <= end - timedelta(days=1):

        end_of_day = current_date + timedelta(days=4)


        data = get_data_from_binance(str(current_date), str(end_of_day), Client.KLINE_INTERVAL_5MINUTE, "BTCUSDT")
        data = add_ema_to_df(data, 30)
        data = add_ema_to_df(data, 100)
        data = compute_derivative(data,'ema30')
        data=smooth(data,'ema30_derivative')
        data = compute_derivative(data, 'ema100')
        data=data[100:]

        mean = data['ema30_derivative_smoothed'].mean()
        std = data['ema30_derivative_smoothed'].std()

        avg_dist= (abs(data['ema30']-data['ema100'])).mean()


        wallet = Wallet(1000)
        orderpossible = True
        dt = pd.DataFrame(columns=['date', 'position', 'price', 'usdt', 'coins', 'valo', 'drawBack'])
        entry_times = []
        exit_times = []
        entry_prices = []
        exit_prices = []

        for time in data.iterrows():

            position = {'date': time[0], 'open': time[1][0], 'high': time[1][1], 'low': time[1][2], 'close': time[1][3],
                        'ema30': time[1][11], 'ema100': time[1][12], 'ema30_derivative':time[1][13], 'ema30_derivative_smoothed':time[1][14], 'ema100_derivative':time[1][15]}

            if orderpossible:

                if open_long_position(position) and wallet.usdt > 0:

                    orderpossible = False

                    wallet.coin = wallet.usdt / position['close']
                    wallet.usdt = 0
                    wallet.sellPrice = position['close']

                    entry_times.append(position['date'])
                    entry_prices.append(position['close'])

                    if wallet.valo > wallet.last_ath:
                        wallet.last_ath = wallet.valo

                    myrow = {'date': position['date'], 'position': "Buy Long",
                             'price': position['close'],
                             'usdt': wallet.usdt, 'coins': wallet.coin, 'valo': wallet.valo,
                             'drawBack': (wallet.valo - wallet.last_ath) / wallet.last_ath}
                    df_row = pd.DataFrame([myrow])
                    dt = pd.concat([dt, df_row], ignore_index=True)

            else:

                if close_long_position(position) and wallet.coin > 0:

                    orderpossible = True

                    wallet.usdt = wallet.coin * position['close']
                    wallet.coin = 0
                    wallet.valo = wallet.usdt

                    exit_times.append(position['date'])
                    exit_prices.append(position['close'])

                    if wallet.valo > wallet.last_ath:
                        wallet.last_ath = wallet.valo

                    myrow = {'date': position['date'], 'position': "Sell Long",
                             'price': position['close'], 'usdt': wallet.usdt, 'coins': wallet.coin,
                             'valo': wallet.valo, 'drawBack': (wallet.valo - wallet.last_ath) / wallet.last_ath}
                    df_row = pd.DataFrame([myrow])
                    dt = pd.concat([dt, df_row], ignore_index=True)

        ### Résultats ###

        dt['resultat'] = dt['valo'] - dt['valo'].shift(1)

        dt['resultat%'] = ((dt['valo'] - dt['valo'].shift(1)) / dt['valo'].shift(1)) * 100

        dt.loc[dt['position'] == 'Buy Short', 'resultat'] = None
        dt.loc[dt['position'] == 'Buy Long', 'resultat%'] = None

        dt['tradeIs'] = None

        dt.loc[dt['resultat'] > 0, 'tradeIs'] = 'Good'
        dt.loc[dt['resultat'] < 0, 'tradeIs'] = 'Bad'

        iniClose = data.iloc[0]['close']
        lastClose = data.iloc[len(data) - 1]['close']
        holdPorcentage = ((lastClose - iniClose) / iniClose) * 100
        algoPorcentage = ((wallet.valo - wallet.initalWallet) / wallet.initalWallet) * 100
        vsHoldPorcentage = ((algoPorcentage - holdPorcentage))


        print("Starting balance : 1000 $")
        print("Final balance :", round(wallet.valo, 2), "$")
        print("Algo Performance:", round(algoPorcentage, 2), "%")
        print("Buy and Hold Performance :", round(holdPorcentage, 2), "%")
        print("Algo vs Buy and Hold :", round(vsHoldPorcentage, 2), "%")
        x = len([x for x in dt["tradeIs"] if x == "Good"])
        y = len([x for x in dt["tradeIs"] if x == "Bad"])
        print("Number positive trades:", x)
        print("Number negative trades:", y)

        dt['resultat%'] = pd.to_numeric(dt['resultat%'], errors='coerce')


        if x != 0:
            print("Average Positive Trades : ", round(
                dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].sum() / dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].count(), 2),
                  "%")
            idbest = dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].idxmax()
            print("Best trade +" + str(round(dt.loc[dt['tradeIs'] == 'Good', 'resultat%'].max(), 2)), "%, the ",
                  dt['date'][idbest])
        else:
            print("Average Positive Trades : ", 0)
        if y != 0:
            print("Average Negative Trades : ",
                  round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].sum() / dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].count(),
                        2), "%")
            idworst = dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].idxmin()
            print("Worst trade", round(dt.loc[dt['tradeIs'] == 'Bad', 'resultat%'].min(), 2), "%, the ", dt['date'][idworst])
        else:
            print("Average Negative Trades : ", 0)
        print("Worst drawBack", str(100 * round(dt['drawBack'].min(), 2)), "%")

        data['date'] = pd.to_datetime(data.index)
        data['date'] = data['date'].apply(mdates.date2num)

        # Create subplots with shared x-axis
        fig, ax1 = plt.subplots()

        # Plot candlestick chart
        ax1.xaxis_date()
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax1.plot(data['date'], data['open'], label='Open', linewidth=1, color='black', linestyle='dashed')
        ax1.plot(data['date'], data['high'], label='High', linewidth=1, color='green')
        ax1.plot(data['date'], data['low'], label='Low', linewidth=1, color='red')
        ax1.plot(data['date'], data['close'], label='Close', linewidth=1, color='black')

        # Overlay moving averages on the same plot
        ax1.plot(data['date'], data['ema30'], label='ema30', linewidth=1, color='green')
        ax1.plot(data['date'], data['ema100'], label='EMA100', linewidth=1, color='orange')

        # Plot entry and exit points
        ax1.scatter(entry_times, entry_prices, marker='^', color='g', label='Entry Position', s=100)
        ax1.scatter(exit_times, exit_prices, marker='v', color='r', label='Exit Position', s=100)

        # Set labels and title
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.set_title('Candlestick Chart with Moving Averages')

        myrowfinal = {'Start':current_date,'S_balance': 1000, 'E_balance': round(wallet.valo, 2), 'Algo_perce': round(algoPorcentage, 2),
                 'Buy&Hold':  round(holdPorcentage, 2), 'vsHoldPorcentage': round(vsHoldPorcentage, 2), 'Nb_positive': x,
                 'Nb_negative': y}
        df_row_final = pd.DataFrame([myrowfinal])
        dataframe = pd.concat([dataframe, df_row_final], ignore_index=True)

        current_date += timedelta(days=1)
    print()
    print('cc')




















