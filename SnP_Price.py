from mysql.connector import connect
import pandas as pd
import requests
import io
import yfinance as yf

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
        data = yf.download(symbol, period='1d')
        latest_close = data['Close'].iloc[-1]
        latest_open = data['Open'].iloc[-1]
        latest_date = data.index[-1].strftime('%Y-%m-%d')

        # 종목 정보 저장
        cursor.execute("INSERT INTO sp500_stocks (symbol, company_name) VALUES (%s, %s) "
                       "ON DUPLICATE KEY UPDATE company_name = VALUES(company_name)",
                       (symbol, company_name))

        # 등락율 계산
        change_rate = (latest_close - latest_open) / latest_open * 100

        # 종목 가격 정보 저장
        cursor.execute("INSERT INTO stock_prices (symbol, date, open, close, change_rate) "
                       "VALUES (%s, %s, %s, %s, %s) "
                       "ON DUPLICATE KEY UPDATE open = VALUES(open), close = VALUES(close), "
                       "change_rate = VALUES(change_rate)",
                       (symbol, latest_date, latest_open, latest_close, change_rate))

        conn.commit()
        print(f"Data saved for Symbol: {symbol} | Company: {company_name}")
    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))

cursor.close()
conn.close()
