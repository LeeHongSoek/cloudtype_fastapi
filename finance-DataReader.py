import FinanceDataReader as fdr
from datetime import datetime, timedelta
import pandas_market_calendars as mcal
import pandas as pd
import json
import numpy as np

# S&P 500의 종목 리스트 가져오기
sp500_list = fdr.StockListing('S&P500')

# 미국 거래소 달력 가져오기
nyse = mcal.get_calendar('NYSE')

# 어제의 날짜 구하기
yesterday = datetime.now() - timedelta(days=1)

# 거래일 필터링
schedule = nyse.schedule(start_date=yesterday - timedelta(days=45), end_date=yesterday)
trading_days = schedule.index


# 종목별 데이터 저장을 위한 리스트
stock_data_list = []

# 각 종목의 데이터 가져오기
for index, row in sp500_list.iterrows():
    ticker = row['Symbol']
    name = row['Name']

    # 개별 종목의 데이터 가져오기
    try:
        stock_data = fdr.DataReader(ticker, trading_days[0].date(), trading_days[-1].date())

        # 충분한 데이터가 있는 경우에만 이동평균 계산
        if len(stock_data) >= 20:
            stock_data['5-day Close Avg'] = stock_data['Close'].rolling(window=5).mean().fillna(-1)
            stock_data['20-day Close Avg'] = stock_data['Close'].rolling(window=20).mean().fillna(-1)
            stock_data['5-day Volume Avg'] = stock_data['Volume'].rolling(window=5).mean().fillna(-1)
            stock_data['20-day Volume Avg'] = stock_data['Volume'].rolling(window=20).mean().fillna(-1)
        else:
            stock_data['5-day Close Avg'] = -1
            stock_data['20-day Close Avg'] = -1
            stock_data['5-day Volume Avg'] = -1
            stock_data['20-day Volume Avg'] = -1

        stock_data['Date'] = stock_data.index.strftime('%Y-%m-%d')
        stock_data['Ticker'] = ticker
        stock_data['Name'] = name
        stock_data = stock_data[['Date', 'Ticker', 'Name', 'Open', 'Close', '5-day Close Avg', '20-day Close Avg', 'Volume', '5-day Volume Avg', '20-day Volume Avg']]
        stock_data.columns = ['날짜', '티커', '종목명', '시가', '종가', '5일평균 종가', '20일평균 종가', '거래량', '5일평균 거래량', '20일평균 거래량']

        stock_data.replace(np.nan, -1, inplace=True)  # NaN 값을 -1로 대체

        stock_data_list.append(stock_data)
    except Exception as e:
        print(f"Error occurred while fetching data for {name}: {str(e)}")

# 종목별 데이터를 JSON 형식으로 변환
json_data = []
for stock_data in stock_data_list:
    json_data += stock_data.to_dict('records')

# JSON 출력
json_output = json.dumps(json_data, indent=4, ensure_ascii=False, default=str)
print(json_output)
