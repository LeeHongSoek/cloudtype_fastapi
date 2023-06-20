import pandas as pd
import requests
import io
import sqlite3
import Snp_Subfunc as subfunc
import Snp_SubInit as subinit
import os

# 현재 실행 중인 스크립트 파일의 경로
# 디렉토리 경로 추출
script_path = os.path.realpath(__file__)
current_directory = os.path.dirname(script_path)

filename = 'lhs_stock.db'

zip_file_name = filename + ".zip"
zip_path = os.path.join(os.getcwd(), zip_file_name)
extract_path = os.getcwd()

if os.path.exists(zip_path):
    subfunc.unzip_file(zip_path, extract_path)
else:
    print(f"The '{zip_file_name}' file does not exist. Skipping the extraction step.")

# Connect to SQLite database
conn = sqlite3.connect(filename)

cursor = conn.cursor()

subinit.createtables(cursor) # Create sp500_stocks, stock_prices table if it does not exist
conn.commit() # Commit the changes for each symbol

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    # S&P 500 종목 전체 저장
    subfunc.insert_update_sp500_stocks(cursor, symbol, company_name)

conn.commit() # Commit the changes

# S&P 500 종목 읽어오기
results = subfunc.select_sp500_stocks(cursor)
for row in results:
    symbol, company_name = row
    
    # S&P 500 종목 일자별 가격저장
    subfunc.fetch_store_stock_prices(cursor, symbol, company_name, -3650)
    #break
conn.commit() # Commit the changes for each symbol    

# 이동평균값이 없으면 삭제
query = ''' DELETE FROM stock_prices
                  WHERE avg_short IS NULL OR avg_long IS NULL   '''
cursor.execute(query)
conn.commit() # Commit the changes for each symbol

# Close the cursor and the connection
cursor.close()
conn.close()

# 파일 압축
subfunc.zip_file(filename, filename+".zip")