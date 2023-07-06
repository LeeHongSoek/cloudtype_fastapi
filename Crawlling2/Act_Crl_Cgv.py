from Crawlling2.Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import sqlite3

class ActCrlCgv(ActCrlSupper):

    # __init__, __del__ =================================================================
    def __init__(self, date_range): # 생성자

        self.logger = get_logger('lotte')   # 파이션 로그
        self.date_range = date_range        # 크롤링 할 날 수

        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('lotte')  # 한달전 로그파일을 삭제한다.
        super().__del__(type(self).__name__)
    # [def __del__(self): # 소멸자]

    # -----------------------------------------------------------------------------------

    # def crawling(self): ===============================================================
    def crawling(self):
        pass
    # [def crawling(self):] -------------------------------------------------------------

    # def uploading(self): ==============================================================
    def uploading(self):
        print("Uploading Lotte data...")
    # [def uploading(self):] ------------------------------------------------------------

if __name__ == '__main__':

    actCrlLotte = ActCrlCgv(date_range=12)  # Lotte
    actCrlLotte.crawling()
    actCrlLotte.uploading()
    
# [if __name__ == '__main__':]    
