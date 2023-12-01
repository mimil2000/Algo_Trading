# -*- coding: utf-8 -*-

#Installations


import ta.volatility
import numpy as np
import pandas as pd
from binance.client import Client
import math

"""## Def fonction_niveaux"""

def fonction_niveaux(data):


    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades',
                           'tb_base_av', 'tb_quote_av', 'ignore'])

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


    def average(lst):
        listc = []
        for int in range(len(lst)):
            if not math.isnan(lst[int]):
                listc.append(lst[int])
        return listc, (sum(listc) / len(listc))

    bollow = df['LOW_BOL_BAND'].values
    bollowc, avgl = average(bollow)
    bolhigh = df['HIGH_BOL_BAND'].values
    bolhighc, avgh = average(bolhigh)

    amplitudebande = avgh - avgl

    def ohlc(df, row):
        return (df.high[row] + df.close[row] + df.open[row] + df.low[row]) / 4

    def support4row(df1, l):  # n1 n2 before and after candle l
        compteur = 0
        for i in range(l - 4, l - 1):
            if ohlc(df1, l) < ohlc(df1, i):
                compteur = compteur + 1
        for i in range(l + 1, l + 4):
            if l + 4 < len(df1):
                if ohlc(df1, l) < ohlc(df1, i):
                    compteur = compteur + 1
            if compteur >= 6:
                return 1

    def resistance4row(df1, l):  # n1 n2 before and after candle l
        compteur = 0
        for i in range(l - 4, l - 1):
            if ohlc(df1, l) > ohlc(df1, i):
                compteur = compteur + 1
        for i in range(l + 1, l + 4):
            if l + 4 < len(df1):
                if ohlc(df1, l) > ohlc(df1, i):
                    compteur = compteur + 1
            if compteur >= 6:
                return 1

    def supportstand(df1, l, n1, n2):  # n1 n2 before and after candle l
        for i in range(l - n1 + 1, l + 1):
            if df1.low[i] > df1.low[i - 1]:
                return 0
        for i in range(l + 1, l + n2 + 1):
            if df1.low[i] < df1.low[i - 1]:
                return 0
        if abs(((df1.close[l] + df1.open[l]) / 2) - (
                (df1.close[l - 1] + df1.open[l - 1]) / 2)) > amplitudebande / 10 or abs(
            ((df1.close[l] + df1.open[l]) / 2) - ((df1.close[l + 1] + df1.open[l + 1]) / 2)) > amplitudebande / 10:
            return 1

    def resistancestand(df1, l, n1, n2):  # n1 n2 before and after candle l
        for i in range(l - n1 + 1, l + 1):
            if df1.high[i] < df1.high[i - 1]:
                return 0
        for i in range(l + 1, l + n2 + 1):
            if df1.high[i] > df1.high[i - 1]:
                return 0
        if abs(((df1.close[l] + df1.open[l]) / 2) - (
                (df1.close[l - 2] + df1.open[l - 2]) / 2)) > amplitudebande / 10 or abs(
            ((df1.close[l] + df1.open[l]) / 2) - ((df1.close[l + 2] + df1.open[l + 2]) / 2)) > amplitudebande / 10:
            return 1

    def suppgroup2(df1, l):
        if df1.close[l] > df1.open[l] and df1.close[l - 1] < df1.open[l - 1] and ohlc(df1, l - 2) > ohlc(df1,
                                                                                                         l) and ohlc(
                df1, l + 1) > ohlc(df1, l):
            return 1
        else:
            return 0

    def resgroup2(df1, l):
        if df1.close[l] < df1.open[l] and df1.close[l - 1] > df1.open[l - 1] and ohlc(df1, l - 2) < ohlc(df1,
                                                                                                         l) and ohlc(
                df1, l + 1) < ohlc(df1, l):
            return 1
        else:
            return 0

    dfpl = df

    srs = []
    srr = []
    n1 = 2
    n2 = 2

    for row in range(n1, len(dfpl) - n2):

        if support4row(dfpl, row):

            if df.close[row] > df.open[row]:  # bullish
                if [row, dfpl.open[row]] not in srs :
                    srs.append([row, df.open[row]])

            else:  # bearish
                if [row, dfpl.close[row]] not in srs :
                    srs.append([row, df.close[row]])


        if resistance4row(dfpl, row):

            if df.close[row] > df.open[row]:  # bullish
                if [row, df.close[row]] not in srr :
                    srr.append([row, dfpl.close[row]])

            else:
                if [row, df.open[row]] not in srr:
                    srr.append([row, dfpl.open[row]])


        if resistancestand(dfpl, row, n1, n2):

            if df.close[row] > df.open[row]:  # bullish
                if [row, df.close[row]] not in srr :
                    srr.append([row, dfpl.close[row]])

            else:  # bearish
                if [row, df.open[row]] not in srr :
                    srr.append([row, dfpl.open[row]])


        if supportstand(dfpl, row, n1, n2):
            if df.close[row] > df.open[row]:  # bullish
                if [row, dfpl.open[row]] not in srs:
                    srs.append([row, df.open[row]])

            else:
                if [row, dfpl.close[row]] not in srs:
                    srs.append([row, df.close[row]])


        """if suppgroup2(dfpl, row):
            print('supgroup2')
            if [row, dfpl.low[row]] or [row, df.close[row]] not in srs:
                if df.close[row] > df.open[row]:  # bullish
                    if [row, dfpl.open[row]] not in srs:
                        srs.append([row, df.open[row]])
                        srs3.append([row, df.open[row]])
                else:
                    if [row, dfpl.close[row]] not in srs:
                        srs.append([row, df.close[row]])
                        srs3.append([row, df.close[row]])
    
        if resgroup2(dfpl, row):
            print('resgroup2')
            if df.close[row] > df.open[row]:  # bullish
                if [row, df.close[row]] not in srr:
                    srr.append([row, dfpl.close[row]])
                    srr3.append([row, dfpl.close[row]])
            else:
                if [row, df.open[row]] not in srr:
                    srr.append([row, dfpl.open[row]])
                    srr3.append([row, dfpl.open[row]])"""

    srs3=[]
    srr3=[]
    srs2 = []
    srr2 = []

    for i in range(len(srs)):
        srs2.append(srs[i][1])
        srs3.append([srs[i][0],srs[i][1]])

    for i in range(len(srr)):
        srr2.append(srr[i][1])
        srr3.append([srr[i][0],srr[i][1]])

    print('srs1', srs)
    print('srr1', srr)


    if srr != [] and srs != []:

        for row in range(len(dfpl)):
            print('row',row)
            print('srs', srs)
            print('srr', srr)

            if len(srr) > 1:
                for elmtr in srr:
                    if dfpl.close[row] > dfpl.open[row]: #bullish
                        val = dfpl.open[row]
                    else:                               #bearish
                        val = dfpl.close[row]
                    if val > elmtr[1] and row > elmtr[0]:
                        print('oui1')
                        for v in range(len(srr)):
                            if srr[v - 1][1] == elmtr[1]:
                                srs.append(srr[v - 1])
                                srs2.append(elmtr[1])
                                srr.remove(srr[v - 1])
                                srr2.remove(elmtr[1])
                                break

            if len(srr) == 1:
                if dfpl.close[row] > dfpl.open[row]:
                    val = dfpl.open[row]
                else:
                    val = dfpl.close[row]
                if val > srr[0][1] and row > srr[0][0]:

                    srs.append([srr[0][0], srr[0][1]])
                    srs2.append(srr[0][1])
                    srr2.remove(srr[0][1])
                    srr.remove(srr[0])
                    break

            if len(srs) > 1:
                for elmts in srs:
                    if dfpl.close[row] > dfpl.open[row]:
                        val = dfpl.close[row]
                    else:
                        val = dfpl.open[row]
                    if val < elmts[1] and row > elmts[0]:
                        print('oui2')
                        for v in range(len(srs)):
                            if srs[v - 1][1] == elmts[1]:
                                srr.append(srs[v - 1])
                                srr2.append(elmts[1])
                                srs.remove(srs[v - 1])
                                srs2.remove(elmts[1])
                                break

            if len(srs) == 1:
                if dfpl.close[row] > dfpl.open[row]:
                    val = dfpl.close[row]
                else:
                    val = dfpl.open[row]
                if val < srs[0][1] and row > srs[0][0]:
                    srr.append([srs[0][0], srs[0][1]])
                    srr2.append(srs[0][1])
                    srs2.remove(srs[0][1])
                    srs.remove(srs[0])
                    break

    def proximity(v1, v2, distance):
        if type(v1) == list:
            return abs(v1[1] - v2[1]) < distance
        else:
            return abs(v1 - v2) < distance

    for i in range(len(srr) - 1):
        if len(srr) > 1:
            try:
                if proximity(srr[i], srr[i + 1], amplitudebande / 10):
                    if srr[i][1] > srr[i + 1][1]:
                        srr.pop(i + 1)
                    else:
                        srr.pop(i)
            except:
                pass

    for i in range(len(srr2) - 1):
        if len(srr2) > 1:
            try:
                if proximity(srr2[i], srr2[i + 1], amplitudebande / 10):
                    if srr2[i] > srr2[i + 1]:
                        srr2.pop(i + 1)
                    else:
                        srr2.pop(i)
            except:
                pass

    for i in range(len(srs) - 1):
        if len(srs) > 1:
            try:
                if proximity(srs[i], srs[i + 1], amplitudebande / 10):
                    if srs[i][1] < srs[i + 1][1]:
                        srs.pop(i + 1)
                    else:
                        srs.pop(i)
            except:
                pass

    for i in range(len(srs2) - 1):
        if len(srs2) > 1:
            try:
                if proximity(srs2[i], srs2[i + 1], amplitudebande / 10):
                    if srs2[i] < srs2[i + 1]:
                        srs2.pop(i + 1)
                    else:
                        srs2.pop(i)
            except:
                pass

    print('srs finaux', srs)
    print('srr finaux', srr)

    print('srs2 finaux', srs2)
    print('srr2 finaux', srr2)

    return srs, srr, srs2, srr2, avgl, avgh, amplitudebande, srr3, srs3
