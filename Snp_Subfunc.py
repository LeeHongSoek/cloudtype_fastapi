import yfinance as yf
import sqlite3


# Fetch symbols, company_name from sp500_stocks table
def select_sp500_stocks(cursor):    
    query = ''' SELECT symbol, company_name FROM sp500_stocks WHERE able = 'Y' '''
    cursor.execute(query)

    return cursor.fetchall()


# Function to fetch and store stock prices
def fetch_store_stock_prices(conn, cursor, symbol, company_name, days):

    try:
        # Fetch stock prices using yfinance
        data = yf.download(symbol, period='max')
        prices = data.iloc[days:]

        print("")
        print(f"Data저장 - 티커: {symbol} | 종목명: {company_name} ({days*(-1)}일치)")

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

            query = ''' SELECT COUNT(*) 
                          FROM (
                                 SELECT *
                                   FROM stock_prices
                                  WHERE symbol = ?
                                    AND tr_date < ?
                                    AND avg_5  IS NOT NULL
                                    AND avg_20 IS NOT NULL
                               ORDER BY tr_date DESC
                                  LIMIT 1
                               )
            '''
            parameters = (symbol, date)
              

            # 쿼리 확인
            formatted_query = query.replace('?', "'{}'").format(*parameters)
            #print("대입된 쿼리:", formatted_query)

            cursor.execute(query, parameters)

            results1 = cursor.fetchall()
            for row1 in results1:
                if row1[0] < 1:
                    crossing_ = ''
                else:
                    query = '''   SELECT IFNULL(avg_5, 0) avg_5
                                       , IFNULL(avg_20, 0) avg_20
                                       , crossing
                                    FROM stock_prices
                                   WHERE symbol = ?
                                     AND tr_date < ?
                                     AND avg_5  IS NOT NULL
                                     AND avg_20 IS NOT NULL
                                ORDER BY tr_date DESC
                                   LIMIT 1
                    '''
                    parameters = (symbol, date)

                    formatted_query = query.replace('?', "'{}'").format(*parameters)
                    #print("대입된 쿼리:", formatted_query)

                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        crossing_ = row2[2]
                        
                        if ((row2[0] < row2[1]) & (avg_5 > avg_20)):
                            crossing_ = '[U]p'
                        if ((row2[0] > row2[1]) & (avg_5 < avg_20)):
                            crossing_ = '[D]own'


            # 5일 평균과 20일 평균을 저장
            query = ''' UPDATE stock_prices
                           SET avg_5    = ?
                             , avg_20   = ?
                             , crossing = ?
                         WHERE symbol  = ?
                           AND tr_date = ?
            '''
            parameters = (avg_5, avg_20, crossing_, symbol, date)
            cursor.execute(query, parameters)

            sign = '_'
            if ((avg_5 != None) & (avg_20 != None)):
                if (avg_5 > avg_20):
                    sign = '>'
                if (avg_5 < avg_20):
                    sign = '<'

            # 데이터 출력
            print(f"{i+1} |일자: {date} |시가: {open_} |종가: {close_} |변동률:  {change_rate} |거래량: {volume_} |5/20평균: {avg_5} {sign} {avg_20} |교차: {crossing_}")

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
