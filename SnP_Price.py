from mysql.connector import connect
import pandas as pd
import requests
import io
import yfinance as yf
import numpy as np

# MySQL 서버에 연결
conn = connect(
    host="svc.gksl2.cloudtype.app",  # MySQL 서버 호스트
    user="root",  # MySQL 사용자 이름
    password="leehs1181!",  # MySQL 사용자 비밀번호
    database="classicmodels",  # 사용할 데이터베이스 이름
    port=32617  # MySQL 접속 포트
)

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# 각 종목의 시가와 종가 가져와서 MySQL에 저장
cursor = conn.cursor()
for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    try:
        # 최신 종가와 시가 가져오기
        data = yf.download(symbol, period='20d')
        prices = data.tail(20)  # 최근 20일의 데이터 선택
        latest_close = prices['Close'].iloc[-1]
        latest_open = prices['Open'].iloc[-1]
        latest_date = prices.index[-1].strftime('%Y-%m-%d')

        # 이전 4일의 종가의 평균 계산
        prev_closes = prices['Close'].iloc[:-1]
        avg_5 = np.mean(prev_closes)

        # 이전 19일의 종가의 평균 계산
        prev_closes_20 = prices['Close'].iloc[:-1]
        avg_20 = np.mean(prev_closes_20)

        # 종목 정보 저장
        cursor.execute("INSERT INTO sp500_stocks (symbol, company_name) VALUES (%s, %s) "
                       "ON DUPLICATE KEY UPDATE company_name = VALUES(company_name)",
                       (symbol, company_name))

        # 최근일자 데이터 저장
        cursor.execute("INSERT INTO stock_prices (symbol, date, open, close, change_rate, avg_5, avg_20) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                       "ON DUPLICATE KEY UPDATE open = VALUES(open), close = VALUES(close), "
                       "change_rate = VALUES(change_rate), avg_5 = VALUES(avg_5), avg_20 = VALUES(avg_20)",
                       (symbol, latest_date, latest_open, latest_close, change_rate, avg_5 if not np.isnan(avg_5) else None, avg_20 if not np.isnan(avg_20) else None))

        conn.commit()
        print(f"Data saved for Symbol: {symbol} | Company: {company_name}")
    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))

cursor.close()
conn.close()
