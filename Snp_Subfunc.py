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
                                    VALUES              (?,      ?,       ?,    ?,     ?,           ?,      datetime('now'))   '''
            parameters = (symbol, date, open_, close_, change_rate, int(volume_))
            cursor.execute(query, parameters)

            # 이전에 수집된 가격자료 갯수
            query = '''   SELECT COUNT(*)
                            FROM stock_prices
                           WHERE symbol = ?
                             AND tr_date < ?   '''
            parameters = (symbol, date)
            cursor.execute(query, parameters)
            results1 = cursor.fetchall()

            # 5일 평균 구하기            
            for row1 in results1:
                if row1[0] < 4: # 4개 이하면 평균을 못 구한다.
                    avg_5 = None
                else:
                    # 4개의 종가 합계를 구한다.
                    query = ''' SELECT IFNULL(SUM(`close`), 0)
                                 FROM (
                                        SELECT tr_date, close
                                        FROM (
                                                SELECT tr_date, close
                                                  FROM stock_prices
                                                 WHERE symbol  = ?
                                                   AND tr_date < ?
                                              ORDER BY tr_date DESC    
                                            ) a                                
                                        LIMIT 4
                                      ) b                                 '''
                    parameters = (symbol, date)
                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        avg_5 = (row2[0] + close_) / 5

                if row1[0] < 19: # 19개 이하면 평균을 못 구한다.
                    avg_20 = None
                else:
                    # 19개의 종가 합계를 구한다.
                    query = ''' SELECT IFNULL(SUM(`close`), 0)
                                 FROM (
                                        SELECT tr_date, close
                                        FROM (
                                                SELECT tr_date, close
                                                  FROM stock_prices
                                                 WHERE symbol  = ?
                                                   AND tr_date < ?
                                               ORDER BY tr_date DESC    
                                            ) a                                
                                        LIMIT 19
                                      ) b                               '''
                    parameters = (symbol, date)
                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        avg_20 = (row2[0] + close_) / 20

            # 5일 평균과 20일 평균이 있는 건의 갯수를 구하야
            query = ''' SELECT COUNT(*) 
                          FROM stock_prices
                         WHERE symbol = ?
                           AND tr_date < ?
                           AND avg_5  IS NOT NULL
                           AND avg_20 IS NOT NULL    '''
            parameters = (symbol, date)              

            # 쿼리 확인
            formatted_query = query.replace('?', "'{}'").format(*parameters)
            #print("대입된 쿼리:", formatted_query)

            cursor.execute(query, parameters)

            results1 = cursor.fetchall()
            for row1 in results1:
                if row1[0] == 0:
                    crossing_ = '' # 5일 평균과 20일 평균이 있어야 교차를 확인할 수 있다.
                else:
                    # 바로전날(날짜 역순)으로 종가 5일 평균과 20일 평균을 구한다.
                    query = '''   SELECT IFNULL(avg_5, 0)  avg_5
                                       , IFNULL(avg_20, 0) avg_20
                                       , crossing
                                    FROM (   
                                            SELECT *    
                                              FROM stock_prices
                                             WHERE symbol = ?
                                               AND tr_date < ?
                                               AND avg_5  IS NOT NULL
                                               AND avg_20 IS NOT NULL
                                          ORDER BY tr_date DESC
                                         )
                                   LIMIT 1                             '''
                    parameters = (symbol, date)

                    formatted_query = query.replace('?', "'{}'").format(*parameters)
                    #print("대입된 쿼리:", formatted_query)

                    cursor.execute(query, parameters)

                    results2 = cursor.fetchall()
                    for row2 in results2:
                        crossing_ = row2[2]

                        # 바로 전날의 마킹값을 일단 따라 간다.. [연속성]
                        if crossing_ == '[U]p':
                            crossing_ = 'Up'
                        if crossing_ == '[D]own':
                            crossing_ = 'Down'
                        
                        # 바로전날 종가 5일 평균과 20일 평균과 당일  종가 5일 평균과 20일 비교하여 교차를 확인하고 마킹한다.
                        if ((row2[0] < row2[1]) & (avg_5 > avg_20)):
                            crossing_ = '[U]p'
                        if ((row2[0] > row2[1]) & (avg_5 < avg_20)):
                            crossing_ = '[D]own'


            # 당일 종가 5일 평균과 20일 평균을 저장
            query = ''' UPDATE stock_prices
                           SET avg_5    = ?
                             , avg_20   = ?
                             , crossing = ?
                         WHERE symbol  = ?
                           AND tr_date = ?   '''
            parameters = (avg_5, avg_20, crossing_, symbol, date)
            cursor.execute(query, parameters)

            # 크기 비교 확인을 위해
            compare = '_'
            if ((avg_5 != None) & (avg_20 != None)):
                if (avg_5 > avg_20):
                    compare = '>'
                if (avg_5 < avg_20):
                    compare = '<'

            # 데이터 출력
            if change_rate >= 0:
                sign = "+"
            else:
                sign = "-"


            print(f"{i+1:3d} | {date} |시: {open_:>4.5f} |종: {close_:>4.5f} |률: {sign}{abs(change_rate):>3.4f} |량: {volume_:8d} |5/20: {avg_5} {compare} {avg_20} | /{crossing_}/")


        query = ''' UPDATE sp500_stocks
                       SET date_update = datetime('now')
                     WHERE symbol = ?                       '''
        parameters = (symbol)
        cursor.execute(query, parameters)
        
        conn.commit() # Commit the changes for each symbol

    except Exception as e:
        print("Error occurred while fetching data for symbol:", symbol)
        print("Error message:", str(e))


def insert_update_sp500_stocks(cursor, symbol, company_name):
    try:
        query = ''' INSERT OR IGNORE 
                                INTO sp500_stocks (symbol, company_name, date_create)
                              VALUES              (?,      ?,            datetime('now'))   '''
        parameters = (symbol, company_name)
        cursor.execute(query, parameters)

        # 데이터 출력
        print("티커:", symbol, "| 종목명:", company_name)
    except Exception as e:
        print("Error message:", str(e))
