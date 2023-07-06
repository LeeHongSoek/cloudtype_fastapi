from Crawlling2.Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import sqlite3

class ActCrlMega(ActCrlSupper):

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
        try:
            self.__crawl_kobis_theaters_Boxoffice()  # 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) 에서 박스오피스정보를 가지고 온다.
            self.__crawl_kobis_theaters_JobA()  # 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) 에서 영화상영관정보를 가지고 온다. (dicTheaters)
            self.__crawl_kobis_theaters_JobB()  # 영화정보/영화상영관/상영스케줄  (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) 에서 상영스케줄을 가지고 온다.
            self.__crawl_kobis_theaters_JobC()  # 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) 에서 개별상영관정보를 가지고 온다.
            self.__crawl_kobis_theaters_JobE()  # 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) 에서 상영내역을 가지고 온다.
        except:
            self.logger.error('KOBIS 크롤링 중 오류발생!')
            raise
    # [def crawling(self):] -------------------------------------------------------------

    # def uploading(self): ==============================================================
    def uploading(self):
        print("Uploading Lotte data...")
    # [def uploading(self):] ------------------------------------------------------------

if __name__ == '__main__':

    actCrlLotte = ActCrlMega(date_range=12)  # Lotte
    actCrlLotte.crawling()
    actCrlLotte.uploading()
    
# [if __name__ == '__main__':]    
