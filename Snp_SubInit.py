import sqlite3

def create_sp500_stocks_table(cursor):
    # Check if sp500_stocks table exists
    query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='sp500_stocks' '''
    cursor.execute(query)
    table_exists = cursor.fetchone()

    # Create sp500_stocks table if it does not exist
    if not table_exists:
        # Create sp500_stocks table
        query = ''' CREATE TABLE IF NOT EXISTS sp500_stocks (
                        symbol        TEXT PRIMARY KEY,
                        company_name  TEXT NOT NULL,
                        date_update   DATETIME NOT NULL,
                        date_create   DATETIME NOT NULL,
                        able          TEXT NOT NULL DEFAULT 'Y',
                        favorite      TEXT DEFAULT 'n'
                    )
        '''
        cursor.execute(query)

def create_stock_prices_table(cursor):
    # Check if stock_prices table exists
    query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='stock_prices' '''
    cursor.execute(query)
    table_exists = cursor.fetchone()

    # Create stock_prices table if it does not exist
    if not table_exists:
        # Create stock_prices table
        query = ''' CREATE TABLE IF NOT EXISTS stock_prices (
                        symbol      TEXT NOT NULL,
                        tr_date     DATE NOT NULL,
                        open        DECIMAL(10, 2) DEFAULT NULL,
                        close       DECIMAL(10, 2) DEFAULT NULL,
                        change_rate DECIMAL(5, 2) DEFAULT NULL,
                        volume      INTEGER DEFAULT NULL,
                        avg_5       DECIMAL(10, 2) DEFAULT NULL,
                        avg_20      DECIMAL(10, 2) DEFAULT NULL,
                        crossing 	TEXT DEFAULT NULL,
                        date_update DATETIME DEFAULT NULL,

                        PRIMARY KEY (symbol, tr_date)
                    )
        '''
        cursor.execute(query)
