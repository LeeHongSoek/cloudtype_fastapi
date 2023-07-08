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
    delayTime = 1  # 딜레이(초)

    def __init__(self, db_filename): # 생성자

        self.db_fullfilename = f'{self.sqlmap_dir}/'+db_filename

        self.sqlmap = ET.parse(f'{self.db_fullfilename}.xml').getroot() # sqlmap XML 파일 읽기

        zip_file_name = f'{self.db_fullfilename}.zip'
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

           pass
        # [db_filename == 'ActCrlKobis':]

        if db_filename == 'ActCrlLotte':

            self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'SELECT_sqlite_master_table_lotte_movie'}']").text.strip())
            if not self.sql_cursor.fetchone():
                self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'CREATE_TABLE_lotte_movie'}']").text.strip())
            
            self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'SELECT_sqlite_master_table_lotte_cinema'}']").text.strip())
            if not self.sql_cursor.fetchone():
                self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'CREATE_TABLE_lotte_cinema'}']").text.strip())
            
            self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'SELECT_sqlite_master_table_lotte_playdate'}']").text.strip())
            if not self.sql_cursor.fetchone():
                self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'CREATE_TABLE_lotte_playdate'}']").text.strip())

            self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'SELECT_sqlite_master_table_lotte_screen'}']").text.strip())
            if not self.sql_cursor.fetchone():
                self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'CREATE_TABLE_lotte_screen'}']").text.strip())
 
            self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'SELECT_sqlite_master_table_lotte_ticketing'}']").text.strip())
            if not self.sql_cursor.fetchone():
                self.sql_cursor.execute(self.sqlmap.find(f"query[@id='{'CREATE_TABLE_lotte_ticketing'}']").text.strip())

            self.sql_conn.commit()
        # [if db_filename == 'ActCrlLotte':]

        if db_filename == 'ActCrlMega':
            pass
        # [if db_filename == 'ActCrlMega':]    
    # [def __init__(self, db_filename): # 생성자]    
            
    def __del__(self, db_filename): # 소멸자

        self.logger.info(f' 파일 {self.db_fullfilename} 을 압축 ')
        zip_file(f'{self.db_fullfilename}.db', f'{self.db_fullfilename}.zip')
    # [def __del__(self, db_filename): # 소멸자]    


    @abstractmethod
    def crawling(self):
        pass

    @abstractmethod
    def uploading(self):
        pass
# [class ActCrlSupper(metaclass=ABCMeta):]