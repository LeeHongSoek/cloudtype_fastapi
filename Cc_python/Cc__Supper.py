"""

"""
from Cc__Config import ConfigFile

from abc import *
import zipfile
import sqlite3
import xml.etree.ElementTree as ET
import os
import requests  # pip install requests
import gzip
import shutil
import os

def parse_strings(str, delimiter=';'):
    parsed_str = [s.strip() for s in str.split(delimiter)]
    return parsed_str


def compress_file(input_file, output_file):
    with open(input_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

def zip_file(file_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(file_path, os.path.basename(file_path))

def unzip_file(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_path)


class CcSupper(metaclass=ABCMeta):
    
    'crawl_sqlmap'
    delayTime = 0.5  # 딜레이(초)

    def __init__(self, db_filename): # 생성자

        config_file = ConfigFile('Cc__Config.properties')

        self.sqlmap_fullfilename = f'{config_file.sqlmap_dir}{db_filename}'
        self.db_fullfilename = f'{config_file.db_dir}{db_filename}'

        # zip_file_name = f'{self.db_fullfilename}.zip' # 압축파일
        # zip_path = os.path.join(os.getcwd(), zip_file_name)
        # extract_path = os.getcwd()

        # if os.path.exists(zip_path): # 압축파일이 있다면 먼저 푼다.. (쌓이는 구조가 아니라 패스~!!)
        #     self.logger.info(f' 파일 {zip_file_name} 을 압축해제! ')
        #     unzip_file(zip_path, extract_path)

        self.sql_conn = sqlite3.connect(f'{self.db_fullfilename}.db') # Connect to SQLite database
        self.sql_cursor = self.sql_conn.cursor()
            
        self.sqlxmp = ET.parse(f'{self.sqlmap_fullfilename}.xml').getroot() # sqlmap XML 파일 읽기        
        for table_name in parse_strings(self.sqlxmp.find("tables").text,';'):  # 만들어지고 관리되어질 테이블 목록

            table_name2 = parse_strings(table_name,':')
            self.sql_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name2[0]}'") # 테이블 존재검사
            if self.sql_cursor.fetchone():
                if len(table_name2) > 1 and table_name2[1] == 'Clear':
                    self.sql_cursor.execute(f"DELETE FROM {table_name2[0]}") # 있으면 싹비우고
            else:

                query = self.sqlxmp.find(f"query[@id='CREATE_TABLE_{table_name2[0]}']").text.strip() # 없으면 생성!!
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

        
        self.logger.info('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
        self.logger.info(f' ♨. 파일 {self.db_fullfilename} 을 압축                                                                                      ')
        self.logger.info('────────────────────────────────────────────────────────────────')

        zip_file(f'{self.db_fullfilename}.db', f'{self.db_fullfilename}.zip') # 의미 없음.. zip를 업로드해도 압축풀기를 못함.
        compress_file(f'{self.db_fullfilename}.db', f'{self.db_fullfilename}.db.gz') # 반드기 gz파일로 압축해야 리눅스에서 압축을 풀수 있음..

        baseUrl = "http://www.mtns7.co.kr/totalscore/upload_gz_file.php"
        r = requests.post(baseUrl, files={'upload': open(f'{self.db_fullfilename}.db.gz', "rb")})
        self.logger.info(r.text) 

"""
        
"""
    # [def uploading(self):]

# [class ActCrlSupper(metaclass=ABCMeta):]