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
                                                               , movienamekr      TEXT NOT NULL
                                                               , moviegenrename   TEXT NOT NULL
                                                               , bookingyn        TEXT NOT NULL
                                                               , releasedate      TEXT NOT NULL
                                                               , viewgradenameus  TEXT NOT NULL
                                                               )                                           '''
            self.sql_cursor.execute(query)

        query = ''' SELECT name FROM sqlite_master WHERE type='table' AND name='lotte_cinema' '''
        self.sql_cursor.execute(query)
        table_exists = self.sql_cursor.fetchone()

        if not table_exists:
            query = ''' CREATE TABLE IF NOT EXISTS lotte_cinema ( cinemacode  TEXT PRIMARY KEY
                                                                , spacialyn   TEXT NOT NULL
                                                                , cinemaname  TEXT NOT NULL
                                                                , link        TEXT NOT NULL
                                                                , succese     TEXT NOT NULL
                                                                )                                           '''
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