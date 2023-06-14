import pandas as pd
import requests
import io
import yfinance as yf
import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('lhs_stock.db')

# Create tables
cursor = conn.cursor()


def create_sp500_stocks_table():
    # Check if sp500_stocks table exists
    query = '''
        SELECT name FROM sqlite_master WHERE type='table' AND name='sp500_stocks'
    '''
    cursor.execute(query)
    table_exists = cursor.fetchone()

    # Create sp500_stocks table if it does not exist
    if not table_exists:
        # Create sp500_stocks table
        query = '''
            CREATE TABLE IF NOT EXISTS sp500_stocks (
                symbol TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                date_update DATETIME NOT NULL,
                date_create DATETIME NOT NULL,
                able TEXT NOT NULL DEFAULT 'Y',
                favorite TEXT DEFAULT 'n'
            )
        '''
        cursor.execute(query)

def create_stock_prices_table():
    # Check if stock_prices table exists
    query = '''
        SELECT name FROM sqlite_master WHERE type='table' AND name='stock_prices'
    '''
    cursor.execute(query)
    table_exists = cursor.fetchone()

    # Create stock_prices table if it does not exist
    if not table_exists:
        # Create stock_prices table
        query = '''
            CREATE TABLE IF NOT EXISTS stock_prices (
                symbol TEXT NOT NULL,
                tr_date DATE NOT NULL,
                open DECIMAL(10, 2) DEFAULT NULL,
                close DECIMAL(10, 2) DEFAULT NULL,
                change_rate DECIMAL(5, 2) DEFAULT NULL,
                volume INTEGER DEFAULT NULL,
                avg_5 DECIMAL(10, 2) DEFAULT NULL,
                avg_20 DECIMAL(10, 2) DEFAULT NULL,
                date_update DATETIME DEFAULT NULL,
                PRIMARY KEY (symbol, tr_date)
            )
        '''
        cursor.execute(query)


# Function to fetch and store stock prices
def fetch_store_stock_prices(symbol, company_name):
    days = -1

    try:
        # Fetch stock prices using yfinance
        data = yf.download(symbol, period='max')
        prices = data.iloc[days:]

        for i in range(len(prices)):
            close_, open_, volume_, date = (
                prices['Close'].iloc[i],
                prices['Open'].iloc[i],
                prices['Volume'].iloc[i],
                prices.index[i].strftime('%Y-%m-%d')
            )
            change_rate = (close_ - open_) / open_ * 100

            # Insert or update daily stock prices
            query = '''
                INSERT OR IGNORE INTO stock_prices
                    (symbol, tr_date, open, close, change_rate, volume, date_update)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            '''
            parameters = (symbol, date, open_, close_, change_rate, int(volume_))
            cursor.execute(query, parameters)

            # Fetch symbols from sp500_stocks table
            query = '''
                SELECT COUNT(*) + 1 
                FROM stock_prices
                WHERE symbol = ?
                AND tr_date < ?
                ORDER BY tr_date DESC
                LIMIT 4
            '''
            parameters = (symbol, date)
            cursor.execute(query, parameters)

            results1 = cursor.fetchall()
            for row1 in results1:
                if row1[0] < 5:
                    avg_5 = None
                else:
                    query = '''
                        SELECT IFNULL(SUM(`close`), 0)
                        FROM (
                            SELECT close
                            FROM stock_prices
                            WHERE symbol = ?
                            AND tr_date < ?
                            ORDER BY tr_date DESC
                            LIMIT 4
                        ) a
                    '''
                    parameters = (symbol, date)
                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        avg_5 = (row2[0] + close_) / 5

            query = '''
                SELECT COUNT(*) + 1 
                FROM stock_prices
                WHERE symbol = ?
                AND tr_date < ?
                ORDER BY tr_date DESC
                LIMIT 19
            '''
            parameters = (symbol, date)
            cursor.execute(query, parameters)

            results1 = cursor.fetchall()
            for row1 in results1:
                if row1[0] < 20:
                    avg_20 = None
                else:
                    query = '''
                        SELECT IFNULL(SUM(`close`), 0)
                        FROM (
                            SELECT close
                            FROM stock_prices
                            WHERE symbol = ?
                            AND tr_date < ?
                            ORDER BY tr_date DESC
                            LIMIT 19
                        ) a
                    '''
                    parameters = (symbol, date)
                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        avg_20 = (row2[0] + close_) / 5

            query = '''
                UPDATE stock_prices
                SET avg_5 = ?,
                    avg_20 = ?
                WHERE symbol = ?
                AND tr_date = ?
            '''
            parameters = (avg_5, avg_20, symbol, date)
            cursor.execute(query, parameters)

            # 데이터 출력
            print("티커:", symbol, "| 일자:", date, "| 시가:", open_, "| 종가:", close_, "| 변동률:", change_rate, "| 거래량:", volume_)

        # Commit the changes for each symbol
        conn.commit()
        print(f"Data저장 - 티커: {symbol} | 종목명: {company_name}")
    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))



def insert_update_sp500_stocks(symbol, company_name):
    try:
        query = '''
            INSERT OR IGNORE INTO sp500_stocks
                (symbol, company_name, date_update, date_create)
                VALUES (?, ?, datetime('now'), datetime('now'))
        '''
        parameters = (symbol, company_name)
        cursor.execute(query, parameters)

        # 데이터 출력
        print("티커:", symbol, "| 종목명:", company_name)
    except Exception as e:
        print("Error message:", str(e))




# Create sp500_stocks table if it does not exist
# Create stock_prices table if it does not exist
create_sp500_stocks_table()
create_stock_prices_table()

# S&P 500 종목 가져오기
url = "https://datahub.io/core/s-and-p-500-companies/r/constituents.csv"
data = requests.get(url).content
sp500 = pd.read_csv(io.StringIO(data.decode('utf-8')))

# Insert or update each symbol in sp500_stocks table
for index, row in sp500.iterrows():
    symbol = row['Symbol']
    company_name = row['Name']

    # Insert or update the symbol in sp500_stocks table
    insert_update_sp500_stocks(symbol, company_name)

    # Fetch and store stock prices for each symbol
    fetch_store_stock_prices(symbol, company_name)

# Close the cursor and the connection
cursor.close()
conn.close()
