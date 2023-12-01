# -*- coding: utf-8 -*-

# Installations


import math

"""## Def fonction_niveaux"""


def fonction_niveaux2(df):

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
    bandehaute=[]
    bandebasse=[]
    n1 = 2
    n2 = 2

    for row in range(n1, len(dfpl) - n2):

        if support4row(dfpl, row):

            if df.close[row] > df.open[row]:  # bullish
                if [row, dfpl.open[row]] not in srs:
                    srs.append([row, df.open[row]])

            else:  # bearish
                if [row, dfpl.close[row]] not in srs:
                    srs.append([row, df.close[row]])

        if resistance4row(dfpl, row):

            if df.close[row] > df.open[row]:  # bullish
                if [row, df.close[row]] not in srr:
                    srr.append([row, dfpl.close[row]])

            else:
                if [row, df.open[row]] not in srr:
                    srr.append([row, dfpl.open[row]])

        if resistancestand(dfpl, row, n1, n2):

            if df.close[row] > df.open[row]:  # bullish
                if [row, df.close[row]] not in srr:
                    srr.append([row, dfpl.close[row]])

            else:  # bearish
                if [row, df.open[row]] not in srr:
                    srr.append([row, dfpl.open[row]])

        if supportstand(dfpl, row, n1, n2):
            if df.close[row] > df.open[row]:  # bullish
                if [row, dfpl.open[row]] not in srs:
                    srs.append([row, df.open[row]])

            else:
                if [row, dfpl.close[row]] not in srs:
                    srs.append([row, df.close[row]])

        for i in srs :
            if i[1]> ohlc(dfpl,23) :
                srs.remove(i)
                srr.append(i)
        for i in srr :
            if i[1] < ohlc(dfpl,23) :
                srr.remove(i)
                srs.append(i)

    for row in range(24):

        bandehaute.append(dfpl.HIGH_BOL_BAND[row])
        bandebasse.append(dfpl.LOW_BOL_BAND[row])

    return srs, srr, bandehaute, bandebasse
