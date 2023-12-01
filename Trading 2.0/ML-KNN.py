import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score


import pandas as pd
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


# Charger les données BTCUSDT (remplacez cela par votre propre chemin de fichier)


# Supposons que vous souhaitez prédire la direction du prix (1 pour une augmentation, 0 pour une diminution)
df['Target'] = (df['close'].shift(-1) > df['close']).astype(int)

# Supprimer la dernière ligne pour éviter les valeurs NaN après le décalage
df = df.dropna()

# Séparer les fonctionnalités et les étiquettes
X = df[['open', 'high', 'low', 'close']]
y = df['Target']

# Diviser les données en ensembles d'entraînement et de test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialiser le modèle k-NN
knn_model = KNeighborsClassifier(n_neighbors=3)

# Entraîner le modèle sur les données d'entraînement
knn_model.fit(X_train, y_train)

# Faire des prédictions sur les données de test
predictions = knn_model.predict(X_test)

# Calculer la précision du modèle
accuracy = accuracy_score(y_test, predictions)
print(f"Précision du modèle k-NN : {accuracy * 100:.2f}%")
