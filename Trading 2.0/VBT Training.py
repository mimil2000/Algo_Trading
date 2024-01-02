import vectorbt as vbt
import datetime

end_date=datetime.datetime.now()
start_date=end_date-datetime.timedelta(days=3)

btc_price = vbt.YFData.download(
    'BTC-USD',
    interval ='1m',
    start=start_date,
    end=end_date,
    missing_index = 'drop').get('Close')

print(btc_price)