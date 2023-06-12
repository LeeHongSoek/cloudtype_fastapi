import pandas as pd
import requests

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(pd.compat.StringIO(data.decode('utf-8')))

# 각 종목의 시가와 종가 가져오기
for symbol in sp500['Symbol']:
    # 최신 종가와 시가 가져오기
    data = yf.download(symbol, period='1d')
    latest_close = data['Close'].iloc[-1]
    latest_open = data['Open'].iloc[-1]

    print("Symbol:", symbol)
    print("Date:", latest_close.name.strftime("%Y-%m-%d"))
    print("Latest Close:", latest_close)
    print("Latest Open:", latest_open)
    print()
