import yfinance as yf # pip install yfinance


# S&P 500 종목 가져오기
sp500 = yf.Tickers('^GSPC')  # ^GSPC는 S&P 500 지수를 나타냅니다

# 각 종목의 시가와 종가 가져오기
for ticker in sp500.tickers:
    symbol = ticker.ticker

    # 최신 종가와 시가 가져오기
    data = ticker.history(period='1d')
    latest_close = data['Close'].iloc[-1]
    latest_open = data['Open'].iloc[-1]

    print("Symbol:", symbol)
    print("Date:", latest_close.name.strftime("%Y-%m-%d"))
    print("Latest Close:", latest_close)
    print("Latest Open:", latest_open)
    print()
