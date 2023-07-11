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
    
    sqlmap_dir = 'crawl_sqlmap'
    delayTime = 0.5  # 딜레이(초)

    def __init__(self, db_filename): # 생성자

        self.db_fullfilename = f'{self.sqlmap_dir}/{db_filename}'

        # zip_file_name = f'{self.db_fullfilename}.zip' # 압축파일
        # zip_path = os.path.join(os.getcwd(), zip_file_name)
        # extract_path = os.getcwd()

        # if os.path.exists(zip_path): # 압축파일이 있다면 먼저 푼다.. (쌓이는 구조가 아니라 패스~!!)
        #     self.logger.info(f' 파일 {zip_file_name} 을 압축해제! ')
        #     unzip_file(zip_path, extract_path)

        self.sql_conn = sqlite3.connect(f'{self.db_fullfilename}.db') # Connect to SQLite database
        self.sql_cursor = self.sql_conn.cursor()
            
        self.sqlxmp = ET.parse(f'{self.db_fullfilename}.xml').getroot() # sqlmap XML 파일 읽기
        for table_name in self.sqlxmp.find("tables").text.strip().split(';'):  # 만들어지고 관리되어질 테이블 목록

            self.sql_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name.strip()}'") # 테이블 존재검사
            if self.sql_cursor.fetchone():

                self.sql_cursor.execute(f"TRUNCATE TABLE {table_name.strip()}") # 있으면 싹비우고
            else:

                query = self.sqlxmp.find(f"query[@id='CREATE_TABLE_{table_name}']").text.strip() # 없으면 생성!!
                for qry in query.split(";"):
                    self.sql_cursor.execute(qry.strip()) if qry.strip() else None
        # [for table_name in table_names:]

        self.sql_conn.commit()
    # [def __init__(self, db_filename): # 생성자]    
            
    def __del__(self): # 소멸자
        pass
    # [def __del__(self, db_filename): # 소멸자]    


    @abstractmethod
    def crawling(self):
        pass

    @abstractmethod
    def uploading(self):

        self.logger.info('===============================================================================================================================')
        self.logger.info(f' ♨. 파일 {self.db_fullfilename} 을 압축                                                                                      ')
        self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

        zip_file(f'{self.db_fullfilename}.db', f'{self.db_fullfilename}.zip') # 전송효휼을 위해~!!
# [class ActCrlSupper(metaclass=ABCMeta):]