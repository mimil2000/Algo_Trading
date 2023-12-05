"Analyse du backtesing"

# -----------------Importation-------------------------------------------------------------------------------------------

import pandas as pd
from Strategy_2 import backtest_launch

# -----------------Variables-------------------------------------------------------------------------------------------

underlying_list = ['BTCUSDT', 'BTCUSD', 'ETHUSDT', 'SOLUSDT', 'ETHUSD', 'XRPUSDT', 'MATICUSDT', 'EGLUSDT', 'AVAXUSDT']

timeframe_dict = {'15m': 0.25, '30m': 0.5, '1h': 1, '2h': 2, '4h': 4, '6h': 6, '12h': 12, '1d': 24}

option_list = ['Long', 'Short', 'Short/Long']

start_date = pd.Timestamp(year=2022, month=1, day=1, hour=0, minute=0, second=0)
end_date = pd.Timestamp(year=2022, month=2, day=28, hour=0, minute=0, second=0)

# -----------------Main Loop-------------------------------------------------------------------------------------------

if '__main__':

    df_analyse = pd.DataFrame(columns=['underlying','timeframe','option','profit factor', 'sortino'])

    for underlying in underlying_list:
        for timeframe in timeframe_dict.keys():
            for option in option_list:
                dataframe= backtest_launch(start_date, end_date, underlying, timeframe, option,
                                                 timeframe_dict[timeframe])

                # Calculez le profit factor en considérant uniquement les gains
                total_gains =(dataframe[dataframe['E_balance'] > 1000]['E_balance']- 1000).sum()
                total_losses = abs((dataframe[dataframe['E_balance'] < 1000]['E_balance']- 1000)).sum()
                profit_factor = total_gains / total_losses if total_losses != 0 else float('inf')

                # Calculez le sortino ratio à partir des rendements négatifs
                negative_returns = dataframe[dataframe['Algo_perce'] < 0]['Algo_perce']
                downside_deviation = negative_returns.std()
                sortino_ratio = total_gains / downside_deviation if downside_deviation != 0 else float('inf')

                row={'underlying':underlying ,'timeframe':timeframe,'option':option,'profit factor':profit_factor, 'sortino':sortino_ratio}
                df_row = pd.DataFrame([row])
                df_analyse = pd.concat([df_analyse, df_row], ignore_index=True)
                print('cc')