from mysql.connector import connect
import pandas as pd
import requests
import io
import yfinance as yf # pip install yfinance

# MySQL 서버에 연결
conn = connect(
    host="svc.gksl2.cloudtype.app",  # MySQL 서버 호스트
    user="root",  # MySQL 사용자 이름
    password="leehs1181!",  # MySQL 사용자 비밀번호
    database="lhs_stock",  # 사용할 데이터베이스 이름
    port=32617  # MySQL 접속 포트
)

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# 각 종목 MySQL에 저장
cursor = conn.cursor()

for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    try:
        # 종목 정보 저장
        cursor.execute("INSERT INTO sp500_stocks (symbol, company_name, date_update, date_create) VALUES (%s, %s, NOW(), NOW()) "
                        "ON DUPLICATE KEY UPDATE company_name = VALUES(company_name), date_update = NOW()",
                        (symbol, company_name))
    except Exception as e:
        print("Error message:", str(e))
    # break

# 각 종목의 시가, 종가, 거래량 가져와서 MySQL에 저장

# SELECT 문 실행
cursor.execute("SELECT symbol, company_name FROM sp500_stocks")

# 결과 가져오기
results = cursor.fetchall()

# 결과 출력
for row in results:
    symbol, company_name = row
    days = -1
    
    try:
        # 최신 종가, 시가, 거래량 가져오기
        data = yf.download(symbol, period='max')
        prices = data.iloc[days:]  # 최근부터 days 일까지의 데이터 선택

        for i in range(len(prices)):
            close, open, volume, date = (
                prices['Close'].iloc[i],
                prices['Open'].iloc[i],
                prices['Volume'].iloc[i],
                prices.index[i].strftime('%Y-%m-%d')
            )
            change_rate = (close - open) / open * 100

            # 일자별 데이터 저장
            cursor.execute("INSERT INTO stock_prices (symbol, tr_date, open, close, change_rate, volume, date_update) "
               "VALUES (%s, %s, %s, %s, %s, %s, NOW()) "
               "ON DUPLICATE KEY UPDATE open = VALUES(open), close = VALUES(close), "
               "change_rate = VALUES(change_rate), avg_5 = VALUES(avg_5), avg_20 = VALUES(avg_20), "
               "volume = VALUES(volume), date_update = NOW()",
               (symbol, date, open, close, change_rate if not pd.isna(change_rate) else None, int(volume)))

            # 데이터 출력
            print(
                "Symbol:", symbol,
                "| Date:", date,
                "| Open:", open,
                "| Close:", close,
                "| Change Rate:", change_rate,
                "| Volume:", volume
            )

        conn.commit()
        print(f"Data saved for Symbol: {symbol} | Company: {company_name}")
    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))


cursor.close()
conn.close()

 