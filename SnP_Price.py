import pandas as pd
import requests
import io
import yfinance as yf

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# 각 종목의 시가와 종가 가져오기
for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']
    
    try:
        # 최신 종가와 시가 가져오기
        data = yf.download(symbol, period='1d')
        latest_close = data['Close'].iloc[-1]
        latest_open = data['Open'].iloc[-1]

        print(f"{index+1}. Symbol: {symbol} | Company: {company_name} | Date: {data.index[-1].strftime('%Y-%m-%d')} | Latest Close: {latest_close} | Latest Open: {latest_open}")
    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))
    print()
