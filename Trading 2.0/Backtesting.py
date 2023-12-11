"Analyse du backtesing"

# -----------------Importation-------------------------------------------------------------------------------------------

import pandas as pd
from Strategy_2 import backtest_launch
from dateutil.relativedelta import relativedelta
import logging

# -----------------Variables-------------------------------------------------------------------------------------------

logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

underlying_list =[
    'BTCUSDT',  # Bitcoin/US Dollar Tether
    'ETHUSDT',  # Ethereum/US Dollar Tether
    'BNBUSDT',  # Binance Coin/US Dollar Tether
    'ADAUSDT',  # Cardano/US Dollar Tether
    'XRPUSDT',  # Ripple/US Dollar Tether
    'LTCUSDT',  # Litecoin/US Dollar Tether
    'DOTUSDT',  # Polkadot/US Dollar Tether
    'SOLUSDT',  # Solana/US Dollar Tether
    'UNIUSDT',  # Uniswap/US Dollar Tether
    'LINKUSDT'  # Chainlink/US Dollar Tether
]
underlying_list =['ETHUSDT']

timeframe_dict = {'15m': 0.25, '30m': 0.5, '1h': 1, '2h': 2, '4h': 4, '6h': 6, '12h': 12, '1d': 24}

# option_list = ['Long', 'Short', 'Short/Long']
option_list = ['Long']

start_date = pd.Timestamp(year=2022, month=1, day=1, hour=0, minute=0, second=0)
end_date = pd.Timestamp(year=2022, month=1, day=1, hour=0, minute=0, second=0)+relativedelta(months=12)

# -----------------Main Loop-------------------------------------------------------------------------------------------

if '__main__':

    df_analyse = pd.DataFrame(columns=['underlying','timeframe','option','profit factor', 'sortino'])
    logging.info('Programm Start')
    for underlying in underlying_list:
        for timeframe in timeframe_dict.keys():
            logging.info(underlying + " / " + timeframe + ': START backetsting')
            for option in option_list:
                dataframe,dt= backtest_launch(start_date, end_date, underlying, timeframe, option,
                                                 timeframe_dict[timeframe])

                nb_good_trade = dataframe['Nb_positive'].sum()
                nb_bad_trade = dataframe['Nb_negative'].sum()

                # Calculez le profit factor en considérant uniquement les gains
                total_gains =(dataframe[dataframe['E_balance'] > 1000]['E_balance']- 1000).sum()
                total_losses = abs((dataframe[dataframe['E_balance'] < 1000]['E_balance']- 1000)).sum()
                profit_factor = total_gains / total_losses if total_losses != 0 else float('inf')

                # Sortino ratio
                avg_returns = dataframe['Algo_perce'].mean()
                negative_returns = dataframe[dataframe['Algo_perce'] < 0]['Algo_perce']
                downside_deviation = negative_returns.std()
                sortino_ratio = avg_returns / downside_deviation if downside_deviation != 0 else float('inf')

                row={'underlying':underlying ,'timeframe':timeframe,'option':option,'profit factor':profit_factor, 'sortino':sortino_ratio, 'nb_good':nb_good_trade, 'nb_bad':nb_bad_trade}
                df_row = pd.DataFrame([row])
                df_analyse = pd.concat([df_analyse, df_row], ignore_index=True)
                print()
            logging.info(underlying + " / " + timeframe + ': END backetsting')


    df_analyse = df_analyse[df_analyse['profit factor'] > 1].dropna().sort_values('profit factor', ascending=False)
    df_analyse = df_analyse[df_analyse['sortino'] > 1].dropna().sort_values('profit factor', ascending=False)

    df_analyse = df_analyse.reset_index(drop=True)

    #On trace l'équité des combinaisons retenues

    df_triplets = df_analyse[['underlying', 'timeframe', 'option']]
    liste_triplets = df_triplets.values.tolist()

    for underlying, timeframe, option in liste_triplets:
        df,dt = backtest_launch(start_date, end_date, underlying, timeframe, option,
                                                 timeframe_dict[timeframe])
        print()






    print()
print()