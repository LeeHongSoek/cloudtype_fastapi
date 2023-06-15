import yfinance as yf
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


# Fetch symbols, company_name from sp500_stocks table
def select_sp500_stocks(cursor):    
    query = ''' SELECT symbol, company_name FROM sp500_stocks WHERE able = 'Y' '''
    cursor.execute(query)

    return cursor.fetchall()


# Function to fetch and store stock prices
def fetch_store_stock_prices(conn, cursor, symbol, company_name, days):

    try:
        print("")
        print(f"Data저장 - 티커: {symbol} | 종목명: {company_name} ({days*(-1)}일치)")

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

            # 가격정보저장
            query = ''' INSERT OR REPLACE 
                                      INTO stock_prices (symbol, tr_date, open, close, change_rate, volume, date_update)
                                    VALUES              (?, ?, ?, ?, ?, ?, datetime('now'))
            '''
            parameters = (symbol, date, open_, close_, change_rate, int(volume_))
            cursor.execute(query, parameters)

            # 5일 평균 구하기
            query = '''   SELECT COUNT(*) + 1 
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
                    query = ''' SELECT IFNULL(SUM(`close`), 0)
                                  FROM (
                                        SELECT close
                                          FROM stock_prices
                                         WHERE symbol  = ?
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

            # 20일 평균구하기
            query = '''  SELECT COUNT(*) + 1 
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
                    query = ''' SELECT IFNULL(SUM(`close`), 0)
                                  FROM (
                                          SELECT close
                                            FROM stock_prices
                                           WHERE symbol  = ?
                                             AND tr_date < ?
                                        ORDER BY tr_date DESC
                                           LIMIT 19
                                       ) a
                    '''
                    parameters = (symbol, date)
                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        avg_20 = (row2[0] + close_) / 20

            query = '''  SELECT COUNT(*) 
                           FROM stock_prices
                          WHERE symbol = ?
                            AND tr_date < ?
                            AND avg_5  IS NOT NULL
                            AND avg_20 IS NOT NULL
                       ORDER BY tr_date DESC
                          LIMIT 1
            '''
            parameters = (symbol, date)
            cursor.execute(query, parameters)

            results2 = cursor.fetchall()
            for row2 in results2:
                if row2[0] < 1:
                    crossing = ''
                else:
                    query = '''   SELECT IFNULL(SUM(`avg_5`), 0) avg_5
                                       , IFNULL(SUM(`avg_20`), 0) avg_20
                                    FROM stock_prices
                                   WHERE symbol = ?
                                     AND tr_date < ?
                                     AND avg_5  IS NOT NULL
                                     AND avg_20 IS NOT NULL
                                ORDER BY tr_date DESC
                                   LIMIT 1
                    '''
                    parameters = (symbol, date)
                    cursor.execute(query, parameters)

                    results3 = cursor.fetchall()
                    for row3 in results3:
                        crossing = ''
                        if ((row3[0] < avg_5) & (row3[1] > avg_20)):
                            crossing = '[G]olden'
                        if ((row3[0] > avg_5) & (row3[1] < avg_20)):
                            crossing = '[D]eath'



            # 5일 평균과 20일 평균을 저장
            query = '''  UPDATE stock_prices
                           SET avg_5    = ?
                             , avg_20   = ?
                             , crossing = ?
                         WHERE symbol  = ?
                           AND tr_date = ?
            '''
            parameters = (avg_5, avg_20, crossing, symbol, date)
            cursor.execute(query, parameters)

            # 데이터 출력
            print(f"{i+1} |일자: {date} |교차: {crossing} |시가: {open_} |종가: {close_} |변동률:  {change_rate} |5평균:  {avg_5} |20평균:  {avg_20} |거래량: {volume_}")

        query = ''' UPDATE sp500_stocks
                       SET date_update = datetime('now')
                     WHERE symbol       = ?
                       AND company_name = ?
        '''
        parameters = (symbol, company_name)
        cursor.execute(query, parameters)
        
        conn.commit() # Commit the changes for each symbol

    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))


def insert_update_sp500_stocks(cursor, symbol, company_name):
    try:
        query = ''' INSERT OR IGNORE 
                                INTO sp500_stocks (symbol, company_name, date_update, date_create)
                              VALUES              (?, ?, datetime('now'), datetime('now'))
        '''
        parameters = (symbol, company_name)
        cursor.execute(query, parameters)

        # 데이터 출력
        print("티커:", symbol, "| 종목명:", company_name)
    except Exception as e:
        print("Error message:", str(e))
