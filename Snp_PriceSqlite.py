import pandas as pd
import requests
import io
import yfinance as yf
import sqlite3
from Snp_PriceSubfunc import create_sp500_stocks_table, create_stock_prices_table, fetch_store_stock_prices, insert_update_sp500_stocks


# Connect to SQLite database
conn = sqlite3.connect('lhs_stock.db')

# Create tables
cursor = conn.cursor()

create_sp500_stocks_table(cursor) # Create sp500_stocks table if it does not exist
create_stock_prices_table(cursor) # Create stock_prices table if it does not exist

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# Insert or update each symbol in sp500_stocks table
for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    # Insert or update the symbol in sp500_stocks table
    insert_update_sp500_stocks(cursor, symbol, company_name)

# Commit the changes
conn.commit()

# Fetch symbols from sp500_stocks table
query = '''
    SELECT symbol, company_name
      FROM sp500_stocks
     WHERE able = 'Y'
'''
cursor.execute(query)
results = cursor.fetchall()

# Fetch stock prices and store them in the database
for row in results:
    symbol, company_name = row
    
    # Fetch and store stock prices for each symbol
    fetch_store_stock_prices(conn, cursor, symbol, company_name, -1)

# Close the cursor and the connection
cursor.close()
conn.close()
