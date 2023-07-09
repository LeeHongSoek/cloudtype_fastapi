from Act__Supper import ActCrlSupper
from Act__Logger import get_logger, clear_logger

import requests
import sys
import traceback
import sqlite3
import time
import html
import datetime

from bs4 import BeautifulSoup  # pip install beautifulsoup4
from json.decoder import JSONDecodeError


class ActCrlKobis(ActCrlSupper):

    def __init__(self, date_range): # 생성자

        self.logger = get_logger('Kobis')   # 파이션 로그
        self.date_range = date_range        # 크롤링 할 날 수


        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('Kobis')  # 한달전 로그파일을 삭제한다.
        super().__del__()
    # [def __del__(self): # 소멸자]


    def crawling(self):

        # =====================================================================================================================================================
        # 1. 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) 에서 박스오피스정보를 가지고 온다.
        #
        def _1_crawlKobis_Boxoffice():
            
            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 1. ### 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __1_crawl_ranking(tag, curDate):

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
                                for tag7 in tag_tds.select("span > a"):  #
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
                    # [for tag_tds in tag_trs.select("td"):]

                    self.logger.info(f'{curDate}, {rank}, {movieCd}, {movieNm}, {openDt}, {salesAmk}, {share}, {salesAmkGap}, {salesAmkAgo}, {salesAmkAcc}, {score}, {scoreGap}, {scoreAgo}, {scoreAcc}, {screen}, {playing}')

                    #self.dicBoxoffice[curDate + ';' + str(no)] = [rank, movieCd, movieNm]
                    query = self.sqlxmp.find(f"query[@id='{'INSERT_kobis_boxoffice'}']").text.strip()
                    parameters = (curDate, rank, movieCd, movieNm, openDt, salesAmk, share, salesAmkGap, salesAmkAgo, salesAmkAcc, score, scoreGap, scoreAgo, scoreAcc, screen, playing )
                    self.sql_cursor.execute(query, parameters)
                # [for tag5 in tag.select("table > tbody > tr"):  # 랭킹 한 줄]    
            # [def __1_crawl_ranking(tag, curDate):]

            strDateSt = (datetime.date.today() - datetime.timedelta(days=6)).strftime('%Y-%m-%d')  # -6 일
            strDateEd = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')  # -1 일

            url = 'http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do'
            url += '?loadEnd=0'
            url += '&searchType=search'
            url += '&sSearchFrom=' + strDateSt
            url += '&sSearchTo=' + strDateEd
            url += '&sMultiMovieYn='
            url += '&sRepNationCd='
            url += '&sWideAreaCd='   # print(url)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            r = requests.post(url, headers=headers)
            time.sleep(self.delayTime)

            soup = BeautifulSoup(r.text, 'html.parser')
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

                        no += 1
                        __1_crawl_ranking(tag2, curDate)
                    elif tag2['style'] == 'display: none;':

                        for tag3 in tag2.findChildren("div", recursive=False):

                            if not tag3.has_attr('style'):  # 랭킹 날짜..

                                curDate = tag3.text.strip()
                                curDate = curDate[0:4] + curDate[6:8] + curDate[10:12]

                                no = 10
                            else:

                                if tag3['style'] == 'overflow-x:auto ;overflow-y:hidden;':  # 날짜별 랭킹테이블 11위 ~~~

                                    no += 1
                                    __1_crawl_ranking(tag3, curDate)
                        # [for tag3 in tag2.findChildren("div", recursive=False):]            
                    #                 
                # [for tag5 in tag.select("table > tbody > tr"):  # 랭킹 한 줄]  

                self.sql_conn.commit()
        # [def _1_crawlKobis_Boxoffice():]

        # =====================================================================================================================================================
        # 2. 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) 에서 영화상영관정보를 가지고 온다. (dicTheaters)
        #
        def _2_crawlKobis_JobA():
            
            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 2. ### 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            url = 'https://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do'                      
            fields = { "pageIndex": "1"
                     , "sPermYn": "Y"
                     , "sJoinYn": "Y"
                     , "sSaleStat": "018201"
                     , "theaCd": ""
                     , "sTheaNm": ""
                     , "sTheaCd": ""
                     , "sWideareaCd": ""
                     , "sBasareaCd": ""
                     , "sSenderCd": ""
                    }
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            r = requests.post(url, headers=headers, data=fields)
            time.sleep(self.delayTime)

            soup = BeautifulSoup(r.text, 'html.parser')

            totalRecode = int((soup.find('em', class_='fwb')).text.replace("총 ", "").replace("건", ""))
            totalPage, remainder = divmod(totalRecode, 10)  # 숫자를 10으로 나눈 몫과 나머지를 계산합니다.

            if remainder > 0:
                totalPage += 1  # 나머지가 0보다 크면 몫에 1을 더합니다.

            for page in range(1, totalPage+1):  # 페이지별로 순환

                #if page not in range(1, 2):  # 디버깅용 1개 페이지에 해당하는 극장만...
                #    continue

                url = 'https://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do'                      
                fields = { "pageIndex": page
                         , "sPermYn": "Y"
                         , "sJoinYn": "Y"
                         , "sSaleStat": "018201"
                         , "theaCd": ""
                         , "sTheaNm": ""
                         , "sTheaCd": ""
                         , "sWideareaCd": ""
                         , "sBasareaCd": ""
                         , "sSenderCd": ""
                         }
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                r = requests.post(url, headers=headers, data=fields)
                time.sleep(self.delayTime)

                soup = BeautifulSoup(r.text, 'html.parser')

                if len(soup.select("table.tbl_comm > tbody > tr")) == 0:  # 없으면 마지막이므로 탈출!!
                    continue

                for tag1 in soup.select("table.tbl_comm > tbody > tr"):  # 극장리스트테이블에서 극장정보를 가지고 온다.

                    i = 0
                    locName1 = locName2 = theaterCd = theaterNm = scrreenNum = seetNum = permanentYn = joinYn = businessOper = openDt = SalleingYn = ''

                    for tag1td in tag1.findChildren("td", recursive=False): #  print(tag1td)
                        tmpVal = tag1td.text

                        if i == 0:
                            locName1 = tmpVal  # 광역단체
                        if i == 1:
                            locName2 = tmpVal  # 기초단체
                        if i == 2:
                            theaterCd = tmpVal  # 상영관 코드
                        if i == 3:
                            theaterNm = tmpVal  # 상영관 이름
                        if i == 4:
                            scrreenNum = tmpVal  # 스크린수
                        if i == 5:
                            seetNum = tmpVal  # 좌석수
                        if i == 6:
                            permanentYn = tmpVal  # 상설여부
                        if i == 7:
                            joinYn = tmpVal  # 가입여부
                        if i == 8:
                            businessOper = tmpVal  # 전송사업자명
                        if i == 9:
                            openDt = tmpVal  # 개관일
                        if i == 10:
                            SalleingYn = tmpVal  # 영업상태

                        i += 1
                    #

                    #if theaterCd != '001205' and theaterCd != '001284' and theaterCd != '001123':  # 건만.. 디버깅용
                    #    continue

                    self.logger.info(f'page:{page}, {theaterCd}, {theaterNm}, {locName1} {locName2}, {scrreenNum}, {seetNum}, {permanentYn}, {joinYn}, {businessOper}, {openDt}, {SalleingYn}')

                    query = self.sqlxmp.find(f"query[@id='{'INSERT_kobis_theater'}']").text.strip()
                    parameters = (theaterCd, theaterNm, locName1, locName2, scrreenNum, seetNum, permanentYn, joinYn, businessOper, openDt, SalleingYn )
                    self.sql_cursor.execute(query, parameters)

                    # 극장코드 정보 저장 (, 상영스케쥴 Dic(B), 스크린정보 Dic(C), 상영관 Dic(E), 상영정보 Dic(E) ... )                    
                    # self.dicTheather[theaterCd] = [theaterNm, {}, {}, {}, {}, scrreenNum]
                # [for tag1 in soup.select("table.tbl_comm > tbody > tr"):  # 극장리스트테이블에서 극장정보를 가지고 온다.]

                # break  ######################################################################################################## 디버그 용

                # if page == 1:  # 디버깅용
                #    break
            # [for page in range(1, totalPage+1):  # 페이지별로 순환]
            self.sql_conn.commit()
        # [def _2_crawlKobis_JobA():]

        # =====================================================================================================================================================
        # 3. 영화정보/영화상영관/상영스케줄  (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) 에서 상영스케줄을 가지고 온다.
        #
        def _3_crawlKobis_JobB():
            
            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 3. ### 영화정보/영화상영관/상영스케줄 (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __3_get_date_range(date_range):
                days = []

                date1 = datetime.date.today()  # 오늘자 날짜객체
                days.append(f'{date1.year:04d}{date1.month:02d}{date1.day:02d}')  # 오늘의 날짜

                for i in range(1, date_range + 1):
                    date = date1 + datetime.timedelta(days=i)  # 오늘 + i 일
                    days.append(f'{date.year:04d}{date.month:02d}{date.day:02d}')

                return days

            def __3_crawlKobis_JobB(theatherCd, theatherNm, itday):

                url = 'https://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do'
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                fields = {"showDt": itday, "theaCd": theatherCd}
                r = requests.post(url, headers=headers, data=fields)
                time.sleep(self.delayTime)

                arrSchedule = []
                schedule_list = r.json()["schedule"]
                if len(schedule_list) > 0:  # 해당날에 해당극장에 상영하는 영화

                    self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                    self.logger.info(f'일자 : /{itday[-2:]} 극장 : ({theatherCd}) {theatherNm}    ')
                    self.logger.info('일자, 상영관코드, 관, 상영시작시간, (영화코드)영화명  ')
                    self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                    for val in schedule_list:

                        movieCd = val['movieCd']
                        movieNm = html.unescape(val['movieNm']).replace('-', '-').replace('–', '-')  # 특수문자 때문
                        scrnNm = val['scrnNm']
                        showTms = val['showTm']

                        lstTms = showTms.split(',')
                        for showTm in lstTms:

                            self.logger.info(f'{itday}, {scrnNm}, {showTm[:2]}:{showTm[-2:]}, ({movieCd}){movieNm}')
                            
                            arrSchedule.append([itday, scrnNm, showTm, movieCd]) # movieNm 제거
                        # [for showTm in lstTms:]

                        #(self.dicTheather[theatherCd])[1] = dicSchedule
                    # [for val in schedule_list:]
                # [if len(schedule_list) > 0:  # 해당날에 해당극장에 상영하는 영화]

                return arrSchedule
            # [def __3_crawlKobis_JobB(self, dicSchedule, theatherCd, today):]

            loopCnt = 0
            dicLoop = {}

            self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'SELECT_kobis_theater'}']").text.strip())
            self.sql_cursor.row_factory = sqlite3.Row
            for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환

                theatherCd = row['theaterCd']
                theatherNm = row['theaterNm']

                # 1 ~ 7 일간 자료 가져오기
                for itday in __3_get_date_range(dateRange):

                    dicLoop[loopCnt] = [theatherCd, theatherNm, itday,  False]
                    loopCnt += 1
                    #self.crawl_kobis_theaters_JobB_sub(dicSchedule, schNo, theatherCd, today)
                # [for itday in __3_get_date_range(dateRange):]
            # [for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환]

            isDone = False  # 종료여부를 확인!
            while not isDone:

                cntTry = 0

                _theatherCd_Old = ""
                for i in range(0, loopCnt):

                    _theatherCd = dicLoop[i][0]
                    _theatherNm = dicLoop[i][1]
                    _itday = dicLoop[i][2]
                    _isDone = dicLoop[i][3]

                    if _theatherCd_Old != _theatherCd:
                        arrSchedule = []  # 해당극장의 일자별 스케쥴

                    if not _isDone:
                        cntTry = cntTry + 1                       

                        try:

                            for schedule in __3_crawlKobis_JobB( _theatherCd, _theatherNm, _itday):
                                query = self.sqlxmp.find(f"query[@id='{'INSERT_kobis_schedule'}']").text.strip()
                                parameters = (_theatherCd, schedule[0], schedule[1], schedule[2], schedule[3]) # arrSchedule.append([itday, scrnNm, showTm, movieCd]) 
                                self.sql_cursor.execute(query, parameters)


                            dicLoop[i][3] = True  # 성공!!!
                        except JSONDecodeError as e:  #  json decode 오류발생시

                            dicLoop[i][3] = False  # 실패!!

                            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                            self.logger.error(f'{_itday}:상영관({_theatherNm})크롤링에 예외가 발생되어 실패')
                            self.logger.error(f'오류 내용! {e}')
                            self.logger.error(f'{traceback.print_exc()}')
                            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                    # [if not _isDone:]        

                    _theatherCd_Old = _theatherCd
                # [for i in range(0, loopCnt):]

                if cntTry == 0:  # 단 한번도 시도되지 않았다면 완전 수행됨으로 빠져나간다.
                    isDone = True
            # [while not isDone:] 

            self.sql_conn.commit()       
        # [def _3_crawlKobis_JobB():]

        # =====================================================================================================================================================
        # 4. 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) 에서 개별상영관정보를 가지고 온다.
        #
        def _4_crawlKobis_JobC():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 4. ### 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'SELECT_kobis_theater'}']").text.strip())
            self.sql_cursor.row_factory = sqlite3.Row
            for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환

                dicScreen = {}  # 해당극장의 상영관

                theatherCd = row['theaterCd'] # theatherNm = row['theaterNm']

                url = 'http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=' + theatherCd
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                r = requests.post(url, headers=headers)
                time.sleep(self.delayTime)

                soup = BeautifulSoup(r.text, 'html.parser')

                for tag in soup.select("div.title_pop02 > strong.tit"):  # print(tag1.text.strip())
                    theaterNm = tag.text.strip()

                for tagTR in soup.select("div#pop_content02 > table.tbl_99 > tbody > tr"):  #

                    for tagTD in tagTR.children:

                        if tagTD != '\n':

                            tagNm = tagTD.name  # th 아니면 td   # print(tag2.name)

                            for tag3 in tagTD:
                                tagVal = tag3.strip() # print(tag3.strip())

                            if tagNm == 'th':
                                itemNm = tagVal  # 항목명이 저장
                            if tagNm == 'td':
                                itemVal = tagVal  # 그 항목의 값이 저장
                                # print(itemVal)

                                if itemNm == '영화상영관코드':
                                    theaterCd = itemVal
                                if itemNm == '전송사업자':
                                    businessOper = itemVal
                                if itemNm == '대표전화번호':
                                    telNo = itemVal
                                if itemNm == '개관일':
                                    openDt = itemVal
                                if itemNm == '홈페이지':
                                    homePage = itemVal
                                if itemNm == '주소':
                                    address = itemVal
                #

                self.logger.info(f'({theaterCd}){theaterNm}[{businessOper}], {telNo}, {openDt}, {homePage}, {address}')

                lstScreenCd = []
                lstScreenNm = []
                lstSeatNum = []

                for tagTR in soup.select("div#pop_content02 > table.tbl3 > thead > tr"): #

                    for tagTD in tagTR.select("th.tac"):  # print(tag2)

                        lstScreenCd.append(tagTD.text.strip())  # 상영관 코드
                #

                for tagTR in soup.select("div#pop_content02 > table.tbl3 > tbody > tr"):  #

                    for tagTD in tagTR.select("th.tac"):    # print(tag2)
                        lstScreenNm.append(tagTD.text.strip())  # 스크린명
                  
                    for tagTD in tagTR.select("td.tac"): # print(tag2)
                        lstSeatNum.append(tagTD.text.strip())  # 좌석수
                #
                
                self.logger.info(lstScreenCd)
                self.logger.info(lstScreenNm)
                self.logger.info(lstSeatNum)

                i = 0
                for screenCd in lstScreenCd:

                    dicScreen[screenCd] = (lstScreenNm[i], lstSeatNum[i])
                    i += 1
                # [for screenCd in lstScreenCd:]

                #(self.dicTheather[theatherCd])[2] = dicScreen

                for screenCd, screen in dicScreen.items():
                    query = self.sqlxmp.find(f"query[@id='{'INSERT_kobis_screen'}']").text.strip()
                    parameters = (theatherCd, screenCd, screen[0], screen[1])
                    self.sql_cursor.execute(query, parameters)
                # [for screen in dicScreen.items():]
            # [for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환]

            self.sql_conn.commit() 
        # [def _4_crawlKobis_JobC():]

        # =====================================================================================================================================================
        # 5. 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) 에서 상영내역을 가지고 온다.
        #
        def _5_crawlKobis_JobE():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 5. ### 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            strDateSt = (datetime.date.today() - datetime.timedelta(days=self.date_range)).strftime('%Y-%m-%d')
            strDateEd = datetime.date.today().strftime('%Y-%m-%d')

            self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'SELECT_kobis_theater'}']").text.strip())
            self.sql_cursor.row_factory = sqlite3.Row
            for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환

                dicShowRoom = {}  # 해당극장의 상영관

                theatherCd = row['theaterCd']
                theatherNm = row['theaterNm']

                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                self.logger.info(f'({theatherCd}) {theatherNm}                 ')
                self.logger.info('일자, 상영관, 회차, 시작시간, 금액, 영화명   ')
                

                #f theatherCd != "015070":  # 디버깅용 (CGV 인천가정)
                #   continue

                url = 'https://www.kobis.or.kr/kobis/business/mast/thea/findShowHistorySc.do'
                fields = { "theaCd": ""
                         , "theaArea": "Y"
                         , "showStartDt": strDateSt
                         , "showEndDt": strDateEd
                         , "sWideareaCd": ""
                         , "sBasareaCd": ""
                         , "sTheaCd": theatherCd
                         , "choice": "1"
                         , "sTheaNm": ""
                         }
                r = requests.post(url, data=fields)
                time.sleep(self.delayTime)

                soup = BeautifulSoup(r.text, 'html.parser')

                # 영화상영관 정보
                lstShowroom = []
                lstSeatnum = []

                for tagTR in soup.select("table.tbl3.info2 > thead > tr"):  # 상영관
                    tagsTH = tagTR.select("th")  #
                    for tagTD in tagsTH:
                        # print(tag2.text.strip())
                        tmpStr = tagTD.text.strip()
                        if not (tmpStr.find('상영관') == 0 or (tmpStr.find('총') == 0 and tmpStr.find('관') > 0)): # print(tmpStr)
                            lstShowroom.append(tmpStr)

                for tagTR in soup.select("table.tbl3.info2 > tbody > tr"):  # 좌석수
                    for tagTD in tagTR.findChildren(recursive=False):
                        # print(tag2)
                        tmpStr = tagTD.text.strip()
                        if not (tmpStr.find('좌석수') == 0 or (tmpStr.find('총') == 0 and tmpStr.find('개') > 0)):
                            # print(tmpStr)
                            lstSeatnum.append(tmpStr)

                    self.logger.info('{0}, {1}'.format('상영관', lstShowroom))
                    self.logger.info('{0}, {1}'.format('좌석수', lstSeatnum))
                    self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                dicPlayDt = {}
                dicShowroom = {}
                i = 0
                for showroom in lstShowroom:

                    dicShowRoom[showroom] = lstSeatnum[i]
                    i += 1
                # [for showroom in lstShowroom:]

                # 상영내역
                lstInningNm = []
                for tagTR in soup.select("table.tbl3.info3 > thead > tr"):  # 상영일자, 상영관, 1회,  2회, 3회, ......

                    for tagTD in tagTR.select("th"):  # print(tag2.text.strip())

                        tmpStr = tagTD.text.strip()
                        if not (tmpStr.find('상영관') == 0 or tmpStr.find('상영일자') == 0): # print(tmpStr.replace("회", ""))
                            lstInningNm.append(tmpStr.replace("회", ""))

                j = 0
                rowspan = 1
                dicInning = {}  # 회차 정보
                
                for tagTR in soup.select("table.tbl3.info3 > tbody > tr"):  # 상영내역 일자별 상영관별

                    playTm = ''
                    movieNm = ''
                    unitprice = ''

                    i = 0
                    minusVal = 1  # 2 번째부터 0

                    tagsTD = tagTR.select("td")  #
                    if (len(lstInningNm) + 1 == len(tagsTD)) or (len(tagsTD) == len(lstInningNm) + 2):  # 현대예술관시네마

                        for tagTD in tagsTD:

                            # if i == 0 and len(tags2) == len(lstInningNm)+2:  # 첫컬럼이 '상영일자' 가 있는 태그
                            if i == 0 and tagTD.has_attr("rowspan"):  # 첫컬럼이 rowspan의 속성을 가지고 있는 태그
                                minusVal = 2  # 3 번째부터 0
                                rowspan = int(tagTD.get('rowspan'))
                                playDt = tagTD.text.strip()  # 상영일자
                                playDt = playDt[0:4] + playDt[5:7] + playDt[8:10]

                                i += 1
                                continue

                            if i == (minusVal-1):  # '상영관'
                                showroom = tagTD.text.strip() # print(tag2.text.strip())
                            else:
                                listDate = list(tagTD.stripped_strings)  # 내용이 붉은 색이여도 바로 잡아준다!!
                                if len(listDate) == 2:  # <br>로 분리되어 있는 경우
                                    tmpStr = listDate[0].strip()
                                    tmpStr = tmpStr.replace('(', '').replace('원)', '').replace(',', '')
                                    tmpLst = tmpStr.split()
                                    if len(tmpLst) == 2:
                                        playTm = tmpLst[0].strip().replace(":", "")[:4]
                                        unitprice = tmpLst[1]
                                    else:
                                        playTm = listDate[0].strip().replace(":", "")[:4]
                                        unitprice = '0'
                                    movieNm = (html.unescape(listDate[1].strip())).replace('-', '-').replace('–', '-').replace('\xa0', ' ').replace('\xA0', ' ')  # 특수문자 때문

                                    dicInning[lstInningNm[i - minusVal]] = [playTm, unitprice, movieNm]
                            i += 1

                        dicShowroom[showroom] = dicInning
                        dicInning = {}

                        j += 1
                        if rowspan == j:   # rowspan의 끝
                            dicPlayDt[playDt] = dicShowroom
                            dicShowroom = {}
                            j = 0
                    # [if (len(lstInningNm) + 1 == len(tagsTD)) or (len(tagsTD) == len(lstInningNm) + 2):]        
                # [for tagTR in soup.select("table.tbl3.info3 > tbody > tr"):  # 상영내역 일자별 상영관별]

                for keyDt, playDt in dicPlayDt.items():
                    for keyRm, showroom in playDt.items():
                        for keyInn, inning in showroom.items():

                            self.logger.info(f'{keyDt}, {keyRm}, {keyInn}, {inning[0]}, {inning[1]}, {inning[2]}')

                            query = self.sqlxmp.find(f"query[@id='{'INSERT_kobis_history'}']").text.strip()
                            parameters = (theatherCd, keyDt, keyRm, keyInn, inning[0], inning[1], inning[2])
                            self.sql_cursor.execute(query, parameters)
                # [for keyDt, playDt in dicPlayDt.items():]
            # [for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환]

            self.sql_conn.commit()
        # [def _5_crawlKobis_JobE():]


        try:

            _1_crawlKobis_Boxoffice()  # 1. 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) 에서 박스오피스정보를 가지고 온다.
            _2_crawlKobis_JobA()       # 2. 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) 에서 영화상영관정보를 가지고 온다.
            _3_crawlKobis_JobB()       # 3. 영화정보/영화상영관/상영스케줄  (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) 에서 상영스케줄을 가지고 온다.
            _4_crawlKobis_JobC()       # 4. 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) 에서 개별상영관정보를 가지고 온다.
            _5_crawlKobis_JobE()       # 5. 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) 에서 상영내역을 가지고 온다.
        except Exception as e:

            self.logger.error('Kobis 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):]

    def uploading(self):
        
        print("Uploading Kobis data...")
    # [def uploading(self):]
# [class ActCrlKobis(ActCrlSupper):]

if __name__ == '__main__':

    maxDateRage = 12  # 최대 일수

    if len(sys.argv) == 2:
        try:
            dateRange = min(max(int(sys.argv[1]), 0), maxDateRage)
        except ValueError:
            dateRange = maxDateRage
    else:
        dateRange = maxDateRage

    actCrlKobis = ActCrlKobis(date_range = dateRange)  # Kobis
    actCrlKobis.crawling()
    actCrlKobis.uploading()
    
# [if __name__ == '__main__':]    
