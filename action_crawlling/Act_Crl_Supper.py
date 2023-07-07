"""

"""
from abc import *
import zipfile
import sqlite3
import xml.etree.ElementTree as ET
import os


def zip_file(file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))

def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_path)


class ActCrlSupper(metaclass=ABCMeta):
    
    sqlmap_dir = 'action_sqlmap'

    # __init__, __del__ =======================================================================================================================================

    def __init__(self, db_filename): # 생성자

        db_fullfilename = f'{self.sqlmap_dir}/'+db_filename

        # XML 파일 읽기
        tree = ET.parse(f'{db_fullfilename}.xml')
        root = tree.getroot()

        zip_file_name = f'{db_fullfilename}.zip'
        zip_path = os.path.join(os.getcwd(), zip_file_name)
        extract_path = os.getcwd()

        if os.path.exists(zip_path):
            self.logger.info(f' 파일 {zip_file_name} 을 압축해제! ')
            unzip_file(zip_path, extract_path)
        else:
            self.logger.info(f"파일 '{zip_file_name}' 가 존재하지 않습니다. ")

        self.sql_conn = sqlite3.connect(db_filename + '.db') # Connect to SQLite database
        self.sql_cursor = self.sql_conn.cursor()

        if db_filename == 'ActCrlCgv':
            pass
        # [if db_filename == 'ActCrlCgv':]
        
        if db_filename == 'ActCrlKobis':

            # ??  ------------------------------------------
            """
            
            Boxoffice
            curDate + ';' + str(no)] = [rank, movieCd, movieNm

            query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='??' '''
            self.sql_cursor.execute(query)
            table_exists = self.sql_cursor.fetchone()

            if not table_exists:
                query = ''' CREATE TABLE IF NOT EXISTS ?? ( moviecode        TEXT PRIMARY KEY
                                                                   , moviename        TEXT NOT NULL  /* 영화명 */
                                                                   , moviegenrename   TEXT NULL      /* ex) 공포, 다큐, 드라마 */
                                                               
                                                                   
                                                                   , viewgradenameus  TEXT NULL      /* ..관람가 */
                                                                   , orgcode          TEXT NULL      /* 영화명이 같고 코드가 다를때 기준영화의 코드 */
                                                                   )                                           '''
                self.sql_cursor.execute(query)
"""
        # [db_filename == 'ActCrlKobis':]

        if db_filename == 'ActCrlLotte':

            # lotte_movie  ------------------------------------------
            self.sql_cursor.execute(root.find(f"query[@id='{'SELECT_sqlite_master_table_lotte_movie'}']").text.strip())
            table_exists = self.sql_cursor.fetchone()

            if not table_exists:
                self.sql_cursor.execute(root.find(f"query[@id='{'CREATE_TABLE_IF_NOT_EXISTS_lotte_movie'}']").text.strip())

            
            # lotte_cinema  ------------------------------------------
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

            
            # lotte_playdate  ------------------------------------------
            query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_playdate' '''
            self.sql_cursor.execute(query)
            table_exists = self.sql_cursor.fetchone()

            if not table_exists:
                query = ''' CREATE TABLE IF NOT EXISTS lotte_playdate ( cinemacode  TEXT
                                                                    , playdate    TEXT
                                                                    , PRIMARY KEY (cinemacode, playdate)
                                                                    )                                          '''
                self.sql_cursor.execute(query)

            
            # lotte_screen  ------------------------------------------
            query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_screen' '''
            self.sql_cursor.execute(query)
            table_exists = self.sql_cursor.fetchone()

            if not table_exists:
                query = ''' CREATE TABLE IF NOT EXISTS lotte_screen ( screencode     TEXT PRIMARY KEY
                                                                    , cinemacode     TEXT NOT NULL
                                                                    , screenname     TEXT NOT NULL
                                                                    , screendivname  TEXT NOT NULL
                                                                    , totalseatcount INT NOT NULL
                                                                    )                                          '''
                self.sql_cursor.execute(query)
                
                query = ''' CREATE INDEX IF NOT EXISTS idx_cinemacode_screenname ON lotte_screen (cinemacode, screenname) '''
                self.sql_cursor.execute(query)

            
            # lotte_ticketing  ------------------------------------------
            query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_ticketing' '''
            self.sql_cursor.execute(query)
            table_exists = self.sql_cursor.fetchone()

            if not table_exists:
                query = ''' CREATE TABLE IF NOT EXISTS lotte_ticketing ( cinemacode        TEXT
                                                                       , playdt            TEXT
                                                                       , screencode        TEXT    
                                                                       , degreeno          INT
                                                                       , moviecode         TEXT NOT NULL
                                                                       , starttime         TEXT NOT NULL
                                                                       , endtime           TEXT NOT NULL
                                                                       , bookingseatcount  INT NOT NULL
                                                                       , PRIMARY KEY (cinemacode, playdt, screencode, degreeno)
                                                                       )                                                       '''
                self.sql_cursor.execute(query)


            """
           SELECT LT.cinemacode
                , LC.cinemaname
                , LT.playdt
                , LT.screencode
                , LS.screenname
                , LS.screendivname
                , LT.degreeno
                , LT.moviecode     
                , LM.moviename
                , LT.starttime
                , LT.endtime
                , LT.bookingseatcount
                , LS.totalseatcount                
            FROM lotte_ticketing LT         
       left join lotte_cinema LC
              on LC.cinemacode = LT.cinemacode              
       left join lotte_screen LS
              on LS.cinemacode = LT.cinemacode
             AND LS.screencode = LT.screencode
       left join lotte_movie LM
              on LM.moviecode = LT.moviecode
            """
            self.sql_conn.commit()
        # [if db_filename == 'ActCrlLotte':]

        if db_filename == 'ActCrlMega':
            pass
        # [if db_filename == 'ActCrlMega':]    
    # [def __init__(self, db_filename): # 생성자]    
            
    def __del__(self, db_filename): # 소멸자

        db_fullfilename = f'{self.sqlmap_dir}/'+db_filename

        self.logger.info(f' 파일 {db_fullfilename} 을 압축 ')
        zip_file(f'{db_fullfilename}.db', f'{db_fullfilename}.zip')
    # [def __del__(self, db_filename): # 소멸자]    


    # def crawling(self):, def uploading(self): ===============================================================================================================

    delayTime = 1  # 딜레이(초)

    @abstractmethod
    def crawling(self):
        pass

    @abstractmethod
    def uploading(self):
        pass
# [class ActCrlSupper(metaclass=ABCMeta):]