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

directory = '/sqlite'
filename = 'lhs_stock.db'

# Connect to SQLite database
conn = sqlite3.connect(filename)

# Create tables
cursor = conn.cursor()

subinit.createtable_sp500_stocks(cursor) # Create sp500_stocks table if it does not exist
subinit.createtable_stock_prices(cursor) # Create stock_prices table if it does not exist

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# Insert or update each symbol in sp500_stocks table
for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    # Insert or update the symbol in sp500_stocks table
    subfunc.insert_update_sp500_stocks(cursor, symbol, company_name)

conn.commit() # Commit the changes

# Fetch symbols, company_name from sp500_stocks table
results = subfunc.select_sp500_stocks(cursor)

# Fetch stock prices and store them in the database
for row in results:
    symbol, company_name = row
    
    # Fetch and store stock prices for each symbol
    subfunc.fetch_store_stock_prices(conn, cursor, symbol, company_name, -61)

query = ''' DELETE FROM stock_prices
                  WHERE avg_5 IS NULL OR avg_20 IS NULL   '''
cursor.execute(query)
conn.commit() # Commit the changes for each symbol


# Close the cursor and the connection
cursor.close()
conn.close()
