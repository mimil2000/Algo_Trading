dt['resultat'] = dt['valo'].diff()
    dt['resultat%'] = dt['valo'].pct_change() * 100
    dt.loc[dt['position'] == 'Buy', 'resultat'] = None
    dt.loc[dt['position'] == 'Buy', 'resultat%'] = None

    dt['tradeIs'] = ''
    dt.loc[dt['resultat'] > 0, 'tradeIs'] = 'Good'
    dt.loc[dt['resultat'] <= 0, 'tradeIs'] = 'Bad'

    iniClose = data[0][1][3]
    lastClose = data[-1][1][3]
    holdPorcentage = ((lastClose - iniClose) / iniClose) * 100
    algoPorcentage = ((wallet.valo - wallet.initalWallet) / wallet.initalWallet) * 100
    vsHoldPorcentage = ((algoPorcentage - holdPorcentage))

if open_long_position(position) and wallet.usdt > 0:

    orderpossible = False

    wallet.coin = wallet.usdt / position['close']
    wallet.frais = wallet.fee * wallet.coin * position['close']
    wallet.usdt = 0
    wallet.valo = wallet.coin * position['close'] - wallet.frais
    wallet.buyPrice = position['close']

    if wallet.valo > wallet.last_ath:
        wallet.last_ath = wallet.valo

    myrow = {'date': position['date'], 'position': "Buy",
             'price': position['close'], 'frais': wallet.frais,
             'usdt': wallet.usdt, 'coins': wallet.coin, 'valo': wallet.valo,
             'drawBack': (wallet.valo - wallet.last_ath) / wallet.last_ath}
    dt = dt.append(myrow, ignore_index=True)

if close_long_position(position) and wallet.coin > 0:
    orderpossible = True

    wallet.usdt = wallet.coin * position['close']
    wallet.frais = wallet.fee * wallet.coin * position['close']
    wallet.usdt = wallet.usdt - wallet.frais
    wallet.coin = 0
    wallet.valo = wallet.usdt

    if wallet.valo > wallet.last_ath:
        wallet.last_ath = wallet.valo

    myrow = {'date': position['date'], 'position': "Sell",
             'price': position['close'], 'frais': wallet.frais, 'usdt': wallet.usdt, 'coins': wallet.coin,
             'valo': wallet.valo, 'drawBack': (wallet.valo - wallet.last_ath) / wallet.last_ath}
    dt = dt.append(myrow, ignore_index=True)