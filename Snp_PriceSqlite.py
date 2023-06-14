import pandas as pd
import requests
import io
import sqlite3
import Snp_PriceSubfunc as sub
import ftpCliant as fc

directory = '/sqlite'
filename = 'lhs_stock.db'

fc.file_download(directory, filename)

# Connect to SQLite database
conn = sqlite3.connect('lhs_stock.db')

# Create tables
cursor = conn.cursor()

sub.create_sp500_stocks_table(cursor) # Create sp500_stocks table if it does not exist
sub.create_stock_prices_table(cursor) # Create stock_prices table if it does not exist

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# Insert or update each symbol in sp500_stocks table
for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    # Insert or update the symbol in sp500_stocks table
    sub.insert_update_sp500_stocks(cursor, symbol, company_name)

conn.commit() # Commit the changes

# Fetch symbols, company_name from sp500_stocks table
results = sub.select_sp500_stocks(cursor)

# Fetch stock prices and store them in the database
for row in results:
    symbol, company_name = row
    
    # Fetch and store stock prices for each symbol
    sub.fetch_store_stock_prices(conn, cursor, symbol, company_name, -1)

# Close the cursor and the connection
cursor.close()
conn.close()

fc.file_download(directory, filename)