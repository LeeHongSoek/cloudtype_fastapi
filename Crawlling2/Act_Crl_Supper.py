from abc import *
import zipfile
import sqlite3
import os



def zip_file(file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))

def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_path)


class ActCrlSupper(metaclass=ABCMeta):
    
    # __init__, __del__ =================================================================
    def __init__(self): # 생성자

        self.db_filename = 'action_crawl.db'

        zip_file_name = self.db_filename + ".zip"
        zip_path = os.path.join(os.getcwd(), zip_file_name)
        extract_path = os.getcwd()

        if os.path.exists(zip_path):
            unzip_file(zip_path, extract_path)
        else:
            print(f"파일 '{zip_file_name}' 가 존재하지 않습니다. ")

        self.sql_conn = sqlite3.connect(self.db_filename) # Connect to SQLite database
        self.sql_cursor = self.sql_conn.cursor()

        query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_movie' '''
        self.sql_cursor.execute(query)
        table_exists = self.sql_cursor.fetchone()

        if not table_exists:
            query = ''' CREATE TABLE IF NOT EXISTS lotte_movie ( moviecode        TEXT PRIMARY KEY
                                                               , movienamekr      TEXT NOT NULL  /* 영화명 */
                                                               , moviegenrename   TEXT NULL      /* ex) 공포, 다큐, 드라마 */
                                                               , filmnamekr       TEXT NULL      /* ex) 2D 4D */
                                                               , gubun            TEXT NULL      /* ex) 더빙 자막 */
                                                               , bookingyn        TEXT NULL      /* 예매여부 */
                                                               , releasedate      TEXT NULL      /* 개봉일 */
                                                               , viewgradenameus  TEXT NULL      /* ..관람가 */
                                                               , orgcode          TEXT NULL      /* 영화명이 같고 코드가 다를때 기준영화의 코드 */
                                                               )                                           '''
            self.sql_cursor.execute(query)

        query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_cinema' '''
        self.sql_cursor.execute(query)
        table_exists = self.sql_cursor.fetchone()

        if not table_exists:
            query = ''' CREATE TABLE IF NOT EXISTS lotte_cinema ( cinemacode  TEXT PRIMARY KEY
                                                                , spacialyn   TEXT NOT NULL /* 스페셜관여부 */
                                                                , cinemaname  TEXT NOT NULL /* 극장명 */
                                                                , link        TEXT NOT NULL /* url(임시) */
                                                                , succese     TEXT NOT NULL /* 크롤링성공여부(임시) */
                                                                )                                           '''
            self.sql_cursor.execute(query)

        query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_ticketing' '''
        self.sql_cursor.execute(query)
        table_exists = self.sql_cursor.fetchone()

        if not table_exists:
            query = ''' CREATE TABLE IF NOT EXISTS lotte_ticketing ( cinemacode        TEXT
                                                                   , playdt            TEXT
                                                                   , screenno          TEXT
                                                                   , degreeno          INT
                                                                   , screennamekr      TEXT NOT NULL
                                                                   , moviecode         TEXT NOT NULL
                                                                   , starttime         TEXT NOT NULL
                                                                   , endtime           TEXT NOT NULL
                                                                   , bookingseatcount  INT NOT NULL
                                                                   , totalseatcount    INT NOT NULL
                                                                   , PRIMARY KEY (cinemacode, playdt, screenno, degreeno)
                                                                   )                                          '''
            self.sql_cursor.execute(query)

        self.sql_conn.commit()
            
    def __del__(self): # 소멸자
        zip_file(self.db_filename, self.db_filename+".zip")
        
    # -----------------------------------------------------------------------------------

    delayTime = 2  # 딜레이(초)

    @abstractmethod
    def crawling(self):
        pass

    @abstractmethod
    def uploading(self):
        pass

#  end of [class ActCrlSupper(metaclass=ABCMeta):]