"""
    KOBIS

http://www.kobis.or.kr/

"""
from Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import traceback
import sqlite3

import html
import datetime
import urllib3  # pip install urllib3
from bs4 import BeautifulSoup  # pip install beautifulsoup4


class ActCrlKobis(ActCrlSupper):

    # __init__, __del__ =================================================================
    def __init__(self, date_range): # 생성자

        self.logger = get_logger('Kobis')   # 파이션 로그
        self.date_range = date_range        # 크롤링 할 날 수

        self.http = urllib3.PoolManager()

        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('Kobis')  # 한달전 로그파일을 삭제한다.
        super().__del__(type(self).__name__)
    # [def __del__(self): # 소멸자]

    # -----------------------------------------------------------------------------------

    # def crawling(self): ===============================================================
    def crawling(self):

        # -----------------------------------------------------------------------------------
        # 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) 에서 박스오피스정보를 가지고 온다.
        #
        def _1_crawlKobis_Boxoffice():
            
            self.logger.info('')
            self.logger.info('### 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) ###  [__crawl_kobis_theaters_Boxoffice(self)]')

            today = datetime.date.today()  # 오늘자 날짜객체
            dateSt = today + datetime.timedelta(days=-6)  # -6 일
            dateEd = today + datetime.timedelta(days=-1)  # -1 일

            strDeteSt = format('{:04d}-{:02d}-{:02d}'.format(dateSt.year, dateSt.month, dateSt.day))
            strDateEd = format('{:04d}-{:02d}-{:02d}'.format(dateEd.year, dateEd.month, dateEd.day))

            url = 'http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do'
            url += '?loadEnd=0'
            url += '&searchType=search'
            url += '&sSearchFrom=' + strDeteSt
            url += '&sSearchTo=' + strDateEd
            url += '&sMultiMovieYn='
            url += '&sRepNationCd='
            url += '&sWideAreaCd='   # print(url)

            data = self.http.request('GET', url).data.decode('utf-8') # print(data)

            soup = BeautifulSoup(data, 'html.parser')

            def __1_crawl_ranking(tag, curDate, no):

                for tag_trs in tag.select("table > tbody > tr"):  # 랭킹 한 줄

                    rank = movieCd = movieNm = openDt = salesAmk = share = salesAmkGap = salesAmkAgo = salesAmkAcc = score = scoreGap = scoreAgo = scoreAcc = screen = playing = ''

                    i = 0

                    for tag_tds in tag_trs.select("td"):

                        listDate = list(tag_tds.stripped_strings)

                        if len(listDate) == 2:  # <br>로 분리되어 있는 경우

                            if i == 1:  # 영화명
                                movieCd = tag_tds.select_one('span > a').get('onclick').split('\'')[3]
                                movieNm = (html.unescape(listDate[0].strip())).replace('-', '-').replace('–', '-')  # 특수문자 때문
                            if i == 5:  # 매출액증감 (전일대비)
                                salesAmkGap = listDate[0].strip()
                                salesAmkAgo = listDate[1].strip()
                            if i == 8:  # 관객수증감 (전일대비)
                                scoreGap = listDate[0].strip()
                                scoreAgo = listDate[1].strip()
                        else:

                            if i == 0:  # 랭킹
                                rank = tag_tds.text.strip()
                            if i == 1:  # 영화명
                                tags7 = tag_tds.select("span > a")  #
                                for tag7 in tags7:
                                    movieCd = tag_tds.select_one('span > a').get('onclick').split('\'')[3]
                                    movieNm = (html.unescape(tag7.text.strip())).replace('-', '-').replace('–', '-')  # 특수문자 때문
                            if i == 2:  # 개봉일
                                openDt = tag_tds.text.strip()
                            if i == 3:  # 매출액
                                salesAmk = tag_tds.text.strip()
                            if i == 4:  # 점유율
                                share = tag_tds.text.strip()
                            if i == 6:  # 누적매출액
                                salesAmkAcc = tag_tds.text.strip()
                            if i == 7:  # 관객수
                                score = tag_tds.text.strip()
                            if i == 9:  # 누적관객수
                                scoreAcc = tag_tds.text.strip()
                            if i == 10:  # 스크린수
                                screen = tag_tds.text.strip()
                            if i == 11:  # 상영쵯수
                                playing = scoreAcc = tag_tds.text.strip()
                        i += 1

                    # 처리 결과를 반환
                    self.logger.info(f'{curDate}, {rank}, {movieCd}, {movieNm}, {openDt}, {salesAmk}, {share}, {salesAmkGap}, {salesAmkAgo}, {salesAmkAcc}, {score}, {scoreGap}, {scoreAgo}, {scoreAcc}, {screen}, {playing}')

                    #self.dicBoxoffice[curDate + ';' + str(no)] = [rank, movieCd, movieNm]

                    no += 1
                # [for tag5 in tag.select("table > tbody > tr"):  # 랭킹 한 줄]    
            # [def process_rankingtag(tag, curDate, no):]


            for tag2 in soup.select_one("div.rst_sch").findChildren("div", recursive=False):

                if tag2.has_attr('class'):

                    if tag2['class'][0] == 'board_tit':  # 랭킹 날짜..
                        curDate = tag2.text.strip()
                        curDate = curDate[0:4] + curDate[6:8] + curDate[10:12]

                    no = 0
                else:

                    if not tag2.has_attr('style'):
                        continue

                    if tag2['style'] == 'overflow-x:auto ;overflow-y:hidden;':  # 날짜별 랭킹테이블 1위에서 10위까지

                        __1_crawl_ranking(tag2, curDate, no)
                        no += 1
                    elif tag2['style'] == 'display: none;':

                        for tag3 in tag2.findChildren("div", recursive=False):

                            if not tag3.has_attr('style'):  # 랭킹 날짜..
                                curDate = tag3.text.strip()
                                curDate = curDate[0:4] + curDate[6:8] + curDate[10:12]

                                no = 10
                            else:
                                if tag3['style'] == 'overflow-x:auto ;overflow-y:hidden;':  # 날짜별 랭킹테이블 11위 ~~~
                                    __1_crawl_ranking(tag3, curDate, no)
                                    no += 1
                    #                 
                # [for tag5 in tag.select("table > tbody > tr"):  # 랭킹 한 줄]                    
        # [def _1_crawlKobis_Boxoffice():]

        # -----------------------------------------------------------------------------------
        # 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) 에서 영화상영관정보를 가지고 온다. (dicTheaters)
        #
        def _2_crawlKobis_JobA():
            pass
        # [def _2_crawlKobis_JobA():]

        # -----------------------------------------------------------------------------------
        # 영화정보/영화상영관/상영스케줄  (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) 에서 상영스케줄을 가지고 온다.
        #
        def _3_crawlKobis_JobB():
            pass
        # [def _3_crawlKobis_JobB():]

        # -----------------------------------------------------------------------------------
        # 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) 에서 개별상영관정보를 가지고 온다.
        #
        def _4_crawlKobis_JobC():
            pass
        # [def _4_crawlKobis_JobC():]

        # -----------------------------------------------------------------------------------
        # 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) 에서 상영내역을 가지고 온다.
        #
        def _5_crawlKobis_JobE():
            pass
        # [def _5_crawlKobis_JobE():]


        try:
            _1_crawlKobis_Boxoffice()  # 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) 에서 박스오피스정보를 가지고 온다.
            _2_crawlKobis_JobA()       # 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) 에서 영화상영관정보를 가지고 온다. (dicTheaters)
            _3_crawlKobis_JobB()       # 영화정보/영화상영관/상영스케줄  (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) 에서 상영스케줄을 가지고 온다.
            _4_crawlKobis_JobC()       # 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) 에서 개별상영관정보를 가지고 온다.
            _5_crawlKobis_JobE()       # 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) 에서 상영내역을 가지고 온다.
        except Exception as e:
            self.logger.error('KOBIS 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):] -------------------------------------------------------------

    # def uploading(self): ==============================================================
    def uploading(self):
        print("Uploading Kobis data...")
    # [def uploading(self):] ------------------------------------------------------------

if __name__ == '__main__':

    actCrlKobis = ActCrlKobis(date_range=12)  # Kobis
    actCrlKobis.crawling()
    actCrlKobis.uploading()
    
# [if __name__ == '__main__':]    
