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
    delayTime = 0.5  # 딜레이(초)

    def __init__(self, db_filename): # 생성자

        self.db_fullfilename = f'{self.sqlmap_dir}/'+db_filename

        zip_file_name = f'{self.db_fullfilename}.zip'
        zip_path = os.path.join(os.getcwd(), zip_file_name)
        extract_path = os.getcwd()

        if os.path.exists(zip_path):
            self.logger.info(f' 파일 {zip_file_name} 을 압축해제! ')
            unzip_file(zip_path, extract_path)
        else:
            self.logger.info(f"파일 '{zip_file_name}' 가 존재하지 않습니다. ")

        self.sql_conn = sqlite3.connect(self.db_fullfilename + '.db') # Connect to SQLite database
        self.sql_cursor = self.sql_conn.cursor()
            
        self.sqlxmp = ET.parse(f'{self.db_fullfilename}.xml').getroot() # sqlmap XML 파일 읽기

        # id가 "SELECT_sqlite_master_"로 시작하는 모든 태그를 수집합니다.
        selected_tags = self.sqlxmp.findall(".//query")
        matching_tags = [tag for tag in selected_tags if tag.attrib['id'].startswith('SELECT_sqlite_master_')]

        for tag in matching_tags:

            tableNm = tag.attrib['id'][len('SELECT_sqlite_master_'):]

            self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{tag.attrib['id']}']").text.strip()) # table 존재유무 검사
            if not self.sql_cursor.fetchone():
                query = self.sqlxmp.find(f"query[@id='{f'CREATE_TABLE_{tableNm}'}']").text.strip() # table 생성
                queries = query.split(";")  # 세미콜론으로 쿼리들을 분리
                for q in queries:
                    if q.strip():  # 빈 쿼리는 실행하지 않음
                        self.sql_cursor.execute(q.strip())
        # [for tag in selected_tags:]

        self.sql_conn.commit()
    # [def __init__(self, db_filename): # 생성자]    
            
    def __del__(self): # 소멸자

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