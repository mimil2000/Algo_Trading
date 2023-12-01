
######## Modules d'importations #################################################
#################################################################################


import pandas as pd
from fonction_niveaux2 import fonction_niveaux2
from ezxt import WrappedBinanceClient
import ta
from binance.client import Client
#import pandas_ta as pda
#import matplotlib.pyplot as plt
import numpy as np
#from termcolor import colored


######## Téléchargement des données##############################################
#################################################################################


client = Client()
#client = WrappedBinanceClient()
data = client.get_historical_klines("ETHUSDT", Client.KLINE_INTERVAL_1HOUR, "01 january 2022","30 january 2022" )
#nbpoints=25+60*24

#data = client.load_ohlcv("ETH/USDT", "1h", 161455680000, nbpoints, True, 100)


df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av',
                                     'trades','tb_base_av', 'tb_quote_av', 'ignore'])

paramretour=24
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

dt = None
dt = pd.DataFrame(columns = ['date','position', 'price', 'frais' ,'fiat', 'coins', 'wallet', 'drawBack'])



######## Conditions BUY and SELL ##############################################
###############################################################

def ohlc(row):
    return (row['high'] + row['open'] + row['close'] + row['low']) / 4

def achatCondition(row,rang):

    data2 = df.iloc[rang-24:rang]
    srs, srr, bandehaute, bandebasse = fonction_niveaux2(data2)

    if len(srr)!=0 and len(srs)!=0 : #range
        srsmax=max(srs)
        srrmin = min(srr)
        rangeniveaux = srrmin[1]-srsmax[1]
        rangebande=row['HIGH_BOL_BAND']-row['LOW_BOL_BAND']
        distanceniveaux=ohlc(row)-srsmax[1]
        distancelowband = ohlc(row) - row['LOW_BOL_BAND']
        possupport=(distanceniveaux/rangeniveaux)*100
        poslowband=(distancelowband/rangebande)*100

        #print(len(srr), len(srs))
        #print('test buy',poslowband, possupport)
        return -20<poslowband<20 and -10<possupport<10

def venteCondition(row,rang):
    data2 = df.iloc[rang - 24:rang]
    srs, srr, bandehaute, bandebasse = fonction_niveaux2(data2)
    #print(len(srr),len(srs))
    if len(srr) != 0 and len(srs) != 0:  # range
        srsmax = max(srs)
        srrmin = min(srr)
        rangeniveaux = srrmin[1] - srsmax[1]
        rangebande=row['HIGH_BOL_BAND']-row['LOW_BOL_BAND']
        distanceniveaux = srrmin[1]-ohlc(row)
        distancehighband = row['HIGH_BOL_BAND'] - ohlc(row)
        posresis = (distanceniveaux / rangeniveaux) * 100
        poshighband = (distancehighband / rangebande) * 100

        #print('test sell',poshighband,posresis)
        return -20<poshighband<20 and -10<posresis<10

def testSLandTP(SL,TP,row,rang):
    data2 = df.iloc[rang - 24:rang]
    srs, srr, bandehaute, bandebasse = fonction_niveaux2(data2)

    if row['close']<SL:
        return 0
    elif row['high']>TP :
        return 1

    elif len(srr) != 0 and len(srs) != 0:  # range
        srsmax = max(srs)
        srrmin = min(srr)
        rangeniveaux = srrmin[1] - srsmax[1]
        distanceniveaux = srrmin[1] - ohlc(row)
        posresis = (distanceniveaux / rangeniveaux) * 100
        if -10 < posresis < 10:
            return 3
    else :
        return 2



######## Boucle de Backtest ##############################################
##########################################################################


usdt = 1000
initalWallet = usdt
coin = 0
wallet = 1000
fee = 0.0007
makerFee = 0.0002
lastAth = 0
stopLoss = 0
takeProfit = 0
orderpossible = True
type=0



for i in range(len(df)) :

    if i+paramretour<len(df):
        ##### -- Buy market order --

        if achatCondition(df.iloc[i + paramretour], i + paramretour) and usdt > 0 and orderpossible == True :
            coin = usdt / df.iloc[i + paramretour]['close']
            frais = fee * coin
            coin = coin - frais
            usdt = 0
            wallet = coin * df.iloc[i + paramretour]['close']
            buyPrice = df.iloc[i + paramretour]['close']
            orderpossible=False
            type='buy'
            stopLoss = buyPrice - 0.02 * buyPrice
            takeProfit = buyPrice + 0.04 * buyPrice

            if wallet > lastAth:
                lastAth = wallet

            myrow = {'date': df.index[i + paramretour], 'position': "Buy", 'price': df.iloc[i + paramretour]['close'], 'frais': frais * df.iloc[i + paramretour]['close'], 'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
            dt = dt.append(myrow,ignore_index=True)
            print('Achat',df.index[i + paramretour],df.iloc[i + paramretour]['close'])


        elif testSLandTP(stopLoss,takeProfit,df.iloc[i + paramretour],i + paramretour)==0 and coin > 0 and orderpossible == False:
            usdt = coin * df.iloc[i + paramretour]['close']
            frais = fee * usdt
            usdt = usdt - frais
            coin = 0
            wallet = usdt
            orderpossible=True

            if wallet > lastAth:
                lastAth = wallet

            myrow = {'date': df.index[i + paramretour], 'position': "Sell", 'price': df.iloc[i + paramretour]['close'], 'frais': frais, 'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
            dt = dt.append(myrow, ignore_index=True)
            print('Cloture par SL',df.index[i + paramretour],df.iloc[i + paramretour]['close'])

        elif testSLandTP(stopLoss,takeProfit,df.iloc[i + paramretour],i + paramretour) == 1 and coin > 0 and orderpossible == False:
            usdt = coin * df.iloc[i + paramretour]['close']
            frais = fee * usdt
            usdt = usdt - frais
            coin = 0
            wallet = usdt
            orderpossible = True

            if wallet > lastAth:
                lastAth = wallet

            myrow = {'date': df.index[i + paramretour], 'position': "Sell", 'price': df.iloc[i + paramretour]['close'],
                     'frais': frais, 'fiat': usdt, 'coins': coin, 'wallet': wallet,
                     'drawBack': (wallet - lastAth) / lastAth}
            dt = dt.append(myrow, ignore_index=True)
            print('Cloture par TP', df.index[i + paramretour],df.iloc[i + paramretour]['close'])

        elif testSLandTP(stopLoss,takeProfit,df.iloc[i + paramretour],i + paramretour) == 3 and coin > 0 and orderpossible == False:
            usdt = coin * df.iloc[i + paramretour]['close']
            frais = fee * usdt
            usdt = usdt - frais
            coin = 0
            wallet = usdt
            orderpossible = True

            if wallet > lastAth:
                lastAth = wallet

            myrow = {'date': df.index[i + paramretour], 'position': "Sell", 'price': df.iloc[i + paramretour]['close'],
                     'frais': frais, 'fiat': usdt, 'coins': coin, 'wallet': wallet,
                     'drawBack': (wallet - lastAth) / lastAth}
            dt = dt.append(myrow, ignore_index=True)
            print('Cloture par resistance', df.index[i + paramretour],df.iloc[i + paramretour]['close'])


        '''''#Stoplosss
        if type=='buy':
            if df.iloc[i + paramretour]['low'] < stopLoss and coin > 0:
                sellPrice = stopLoss
                usdt = coin * sellPrice
                frais = fee * usdt
                usdt = usdt - frais
                coin = 0
                wallet = usdt
                orderpossible = True

                # -- Check if your wallet hit a new ATH to know the drawBack --
                if wallet > lastAth:
                    lastAth = wallet
                print("Cloture BUY Stop loss",sellPrice,'$ the', df.index[i + paramretour])
                myrow = {'date': df.index[i + paramretour], 'position': "Buy", 'price': df.iloc[i + paramretour]['close'], 'frais': frais * df.iloc[i + paramretour]['close'], 'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                dt = dt.append(myrow, ignore_index=True)
        else :
            if df.iloc[i + paramretour]['high'] > stopLoss and coin > 0:
                sellPrice = stopLoss
                usdt = coin * sellPrice
                frais = fee * usdt
                usdt = usdt - frais
                coin = 0
                wallet = usdt
                orderpossible = True

                # -- Check if your wallet hit a new ATH to know the drawBack --
                if wallet > lastAth:
                    lastAth = wallet
                print("Cloture SELL Stop loss",sellPrice,'$ the', df.index[i + paramretour])
                myrow = {'date': df.index[i + paramretour], 'position': "Sell",
                         'price': df.iloc[i + paramretour]['close'], 'frais': frais * df.iloc[i + paramretour]['close'],
                         'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                dt = dt.append(myrow, ignore_index=True)


        #Takeprofit
        if type=='buy':
            if df.iloc[i + paramretour]['high'] > takeProfit and coin > 0:
                sellPrice = stopLoss
                usdt = coin * sellPrice
                frais = makerFee * usdt
                usdt = usdt - frais
                coin = 0
                wallet = usdt
                orderpossible = True

                # -- Check if your wallet hit a new ATH to know the drawBack --
                if wallet > lastAth:
                    lastAth = wallet
                print("Cloture Achat TAKE PROFIT ",sellPrice,'$ the', df.index[i + paramretour])
                myrow = {'date': df.index[i + paramretour], 'position': "Buy", 'price': df.iloc[i + paramretour]['close'], 'frais': frais * df.iloc[i + paramretour]['close'], 'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                dt = dt.append(myrow, ignore_index=True)
        else :
            if df.iloc[i + paramretour]['low'] > takeProfit and coin > 0:
                sellPrice = stopLoss
                usdt = coin * sellPrice
                frais = makerFee * usdt
                usdt = usdt - frais
                coin = 0
                wallet = usdt
                orderpossible = True

                # -- Check if your wallet hit a new ATH to know the drawBack --
                if wallet > lastAth:
                    lastAth = wallet
                print("Cloture Sell TAKE PROFIT",sellPrice,'$ the', df.index[i + paramretour])
                myrow = {'date': df.index[i + paramretour], 'position': "Sell",
                         'price': df.iloc[i + paramretour]['close'], 'frais': frais * df.iloc[i + paramretour]['close'],
                         'fiat': usdt, 'coins': coin, 'wallet': wallet, 'drawBack': (wallet - lastAth) / lastAth}
                dt = dt.append(myrow, ignore_index=True)'''



######## Résultats ###########################################################
#############################################################################



print("Period : [" + str(df.index[0]) + "] -> [" +str(df.index[len(df)-1]) + "]")
dt = dt.set_index(dt['date'])
dt.index = pd.to_datetime(dt.index)
dt['resultat'] = dt['wallet'].diff()
dt['resultat%'] = dt['wallet'].pct_change()*100
dt.loc[dt['position']=='Buy','resultat'] = None
dt.loc[dt['position']=='Buy','resultat%'] = None

dt['tradeIs'] = ''
dt.loc[dt['resultat']>0,'tradeIs'] = 'Good'
dt.loc[dt['resultat']<=0,'tradeIs'] = 'Bad'

iniClose = df.iloc[0]['close']
lastClose = df.iloc[len(df)-1]['close']
holdPorcentage = ((lastClose - iniClose)/iniClose) * 100
algoPorcentage = ((wallet - initalWallet)/initalWallet) * 100
vsHoldPorcentage = ((algoPorcentage - holdPorcentage))


print("Starting balance : 1000 $")
print("Final balance :",round(wallet,2),"$")
print("Algo Performance:",round(algoPorcentage,2),"%")
print("Buy and Hold Performance :",round(holdPorcentage,2),"%")
print("Algo vs Buy and Hold :",round(vsHoldPorcentage,2),"%")
#print("Number of negative trades : ",dt.groupby('tradeIs')['date'].nunique()['Bad'])
#print("Number of positive trades : ",dt.groupby('tradeIs')['date'].nunique()['Good'])
x=len([x for x in dt["tradeIs"] if x == "Good"])
y=len([x for x in dt["tradeIs"] if x == "Bad"])
print("Number positive trades:" , x )
print("Number negative trades:" , y )

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
print("Total fee : ",round(dt['frais'].sum(),2),"$")











