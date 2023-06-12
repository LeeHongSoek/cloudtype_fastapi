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

    days = -20

    try:
        # 종목 정보 저장
        cursor.execute("INSERT INTO sp500_stocks (symbol, company_name) VALUES (%s, %s) "
                        "ON DUPLICATE KEY UPDATE company_name = VALUES(company_name)",
                        (symbol, company_name))

        # 최신 종가와 시가 가져오기
        data = yf.download(symbol, period='max')
        prices = data.iloc[days:]  # 최근부터 -20일까지의 데이터 선택

        for i in range(len(prices)):
            close, open, date = prices['Close'].iloc[i], prices['Open'].iloc[i], prices.index[i].strftime('%Y-%m-%d')
            change_rate = (close - open) / open * 100

            # 5일 평균 계산
            avg_5 = prices['Close'].iloc[i-4:i+1].mean()

            # 20일 평균 계산
            avg_20 = prices['Close'].iloc[i-19:i+1].mean()

            # 일자별 데이터 저장
            cursor.execute("INSERT INTO stock_prices (symbol, date, open, close, change_rate, avg_5, avg_20) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s) "
               "ON DUPLICATE KEY UPDATE open = VALUES(open), close = VALUES(close), "
               "change_rate = VALUES(change_rate), avg_5 = VALUES(avg_5), avg_20 = VALUES(avg_20)",
               (symbol, date, open, close, change_rate if not pd.isna(change_rate) else None,
                avg_5 if not pd.isna(avg_5) else None, avg_20 if not pd.isna(avg_20) else None))

            # 데이터 출력
            print("Symbol:", symbol, "| Date:", date, "| Open:", open, "| Close:", close,
                  "| Change Rate:", change_rate, "| 5-day Avg:", avg_5, "| 20-day Avg:", avg_20)

        conn.commit()
        print(f"Data saved for Symbol: {symbol} | Company: {company_name}")
    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))

cursor.close()
conn.close()
