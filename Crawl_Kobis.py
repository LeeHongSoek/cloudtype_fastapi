"""
    KOBIS

http://www.kobis.or.kr/

"""
import datetime
import html
import json
import sys

import urllib3  # pip install urllib3
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from Crawl_Supper import Crawl
from Crawling_Logger import get_logger, clean_logger
import zipfile
import os
import time
import requests  # pip install requests
from json.decoder import JSONDecodeError

# requests.get()에서 SSL 인증서 오류를 무시하도록 처리
# Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings InsecureRequestWarning)
urllib3.disable_warnings()

class CrawlKobis(Crawl):

    # -----------------------------------------------------------------------------------
    def __init__(self, isPrnConsole, logger, dateRage):

        self.dt = datetime.datetime.today()  # 오늘자 날짜객체

        self.startDt = '{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}'.format(self.dt.year, self.dt.month, self.dt.day, self.dt.hour, self.dt.minute, self.dt.second)
        self.dateRage = dateRage
        self.http = urllib3.PoolManager()
        self.logger = logger  # 파이션 로그
        self.isPrnConsole = isPrnConsole  # 출력여부

        self.dicBoxoffice = {}  # 박스오피스 정보
        self.dicTheather = {}  # 극장코드 정보
        self.dicMovies = {}  # 영화 코드 정보
    # -----------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # 박스오피스/일별 박스오피스(http://www.kobis.or.kr/kobis/business/stat/boxs/findDailyBoxOfficeList.do) 에서 박스오피스정보를 가지고 온다.
    #
    def __crawl_kobis_theaters_Boxoffice(self):

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
        url += '&sWideAreaCd='
        # print(url)

        r = self.http.request('GET', url)

        data = r.data.decode('utf-8')
        # print(data)

        soup = BeautifulSoup(data, 'html.parser')

        tags1 = soup.select("div.rst_sch")  #
        for tag1 in tags1:
            for tag2 in tag1.findChildren("div", recursive=False):
                if tag2.has_attr('class'):
                    if tag2['class'][0] == 'board_tit':  # 랭킹 날짜..
                        # print(tag2.text.strip())
                        curDate = tag2.text.strip()
                        curDate = curDate[0:4] + curDate[6:8] + curDate[10:12]

                    no = 0
                else:
                    if tag2.has_attr('style'):
                        # print(tag2['style'])
                        if tag2['style'] == 'overflow-x:auto ;overflow-y:hidden;':  # 날짜별 랭킹테이블 1위에서 10위까지
                            # print(tag2)

                            tags3 = tag2.select("table > tbody > tr")  # 랭킹 한 줄
                            for tag4 in tags3:
                                tags5 = tag4.select("td")  #

                                rank = ''
                                movieNm = ''
                                openDt = ''
                                salesAmk = ''
                                share = ''
                                salesAmkGap = ''
                                salesAmkAgo = ''
                                salesAmkAcc = ''
                                score = ''
                                scoreGap = ''
                                scoreAgo = ''
                                scoreAcc = ''
                                screen = ''
                                playing = ''
                                i = 0

                                for tag5 in tags5:
                                    listDate = list(tag5.stripped_strings)

                                    if len(listDate) == 2:  # <br>로 분리되어 있는 경우
                                        if i == 1:  # 영화명
                                            movieCd = tag5.select_one('span > a').get('onclick').split('\'')[3]
                                            movieNm = html.unescape(listDate[0].strip())  # 특수문자 때문
                                            movieNm = movieNm.replace('-', '-')  # 특수문자 때문
                                            movieNm = movieNm.replace('–', '-')  # 특수문자 때문
                                        if i == 5:  # 매출액증감 (전일대비)
                                            salesAmkGap = listDate[0].strip()
                                            salesAmkAgo = listDate[1].strip()
                                        if i == 8:  # 관객수증감 (전일대비)
                                            scoreGap = listDate[0].strip()
                                            scoreAgo = listDate[1].strip()
                                    else:
                                        if i == 0:  # 랭킹
                                            rank = tag5.text.strip()
                                        if i == 1:  # 영화명
                                            tags6 = tag5.select("span > a")  #
                                            for tag6 in tags6:
                                                movieCd = tag5.select_one('span > a').get('onclick').split('\'')[3]
                                                movieNm = html.unescape(tag6.text.strip())  # 특수문자 때문
                                                movieNm = movieNm.replace('-', '-')  # 특수문자 때문
                                                movieNm = movieNm.replace('–', '-')  # 특수문자 때문
                                        if i == 2:  # 개봉일
                                            openDt = tag5.text.strip()
                                        if i == 3:  # 매출액
                                            salesAmk = tag5.text.strip()
                                        if i == 4:  # 점유율
                                            share = tag5.text.strip()
                                        if i == 6:  # 누적매출액
                                            salesAmkAcc = tag5.text.strip()
                                        if i == 7:  # 관객수
                                            score = tag5.text.strip()
                                        if i == 9:  # 누적관객수
                                            scoreAcc = tag5.text.strip()
                                        if i == 10:  # 스크린수
                                            screen = tag5.text.strip()
                                        if i == 11:  # 상영쵯수
                                            playing = scoreAcc = tag5.text.strip()
                                    i += 1

                                if self.isPrnConsole:  # ################
                                    self.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}'.format(curDate, rank, movieCd, movieNm, openDt, salesAmk, share, salesAmkGap, salesAmkAgo, salesAmkAcc, score, scoreGap, scoreAgo, scoreAcc, screen, playing))

                                self.dicBoxoffice[curDate + ';' + str(no)] = [rank, movieCd, movieNm]

                                no += 1
                        else:
                            if tag2['style'] == 'display: none;':

                                for tag3 in tag2.findChildren("div", recursive=False):
                                    if not tag3.has_attr('style'):  # 랭킹 날짜..
                                        # print(tag3)
                                        curDate = tag3.text.strip()
                                        curDate = curDate[0:4] + curDate[6:8] + curDate[10:12]

                                        no = 10
                                    else:
                                        if tag3['style'] == 'overflow-x:auto ;overflow-y:hidden;':  # 날짜별 랭킹테이블 11위 ~~~
                                            tags4 = tag3.select("table > tbody > tr")  # 랭킹 한 줄
                                            for tag5 in tags4:
                                                tags6 = tag5.select("td")  #

                                                rank = ''
                                                movieNm = ''
                                                openDt = ''
                                                salesAmk = ''
                                                share = ''
                                                salesAmkGap = ''
                                                salesAmkAgo = ''
                                                salesAmkAcc = ''
                                                score = ''
                                                scoreGap = ''
                                                scoreAgo = ''
                                                scoreAcc = ''
                                                screen = ''
                                                playing = ''
                                                i = 0

                                                for tag6 in tags6:
                                                    listDate = list(tag6.stripped_strings)

                                                    if len(listDate) == 2:  # <br>로 분리되어 있는 경우
                                                        if i == 1:  # 영화명
                                                            movieCd = tag6.select_one('span > a').get('onclick').split('\'')[3]
                                                            movieNm = html.unescape(listDate[0].strip())  # 특수문자 때문
                                                            movieNm = movieNm.replace('-', '-')  # 특수문자 때문
                                                            movieNm = movieNm.replace('–', '-')  # 특수문자 때문
                                                        if i == 5:  # 매출액증감 (전일대비)
                                                            salesAmkGap = listDate[0].strip()
                                                            salesAmkAgo = listDate[1].strip()
                                                        if i == 8:  # 관객수증감 (전일대비)
                                                            scoreGap = listDate[0].strip()
                                                            scoreAgo = listDate[1].strip()
                                                    else:
                                                        if i == 0:  # 랭킹
                                                            rank = tag6.text.strip()
                                                        if i == 1:  # 영화명
                                                            tags7 = tag6.select("span > a")  #
                                                            for tag7 in tags7:
                                                                movieCd = tag6.select_one('span > a').get('onclick').split('\'')[3]
                                                                movieNm = html.unescape(tag7.text.strip())  # 특수문자 때문
                                                                movieNm = movieNm.replace('-', '-')  # 특수문자 때문
                                                                movieNm = movieNm.replace('–', '-')  # 특수문자 때문
                                                        if i == 2:  # 개봉일
                                                            openDt = tag6.text.strip()
                                                        if i == 3:  # 매출액
                                                            salesAmk = tag6.text.strip()
                                                        if i == 4:  # 점유율
                                                            share = tag6.text.strip()
                                                        if i == 6:  # 누적매출액
                                                            salesAmkAcc = tag6.text.strip()
                                                        if i == 7:  # 관객수
                                                            score = tag6.text.strip()
                                                        if i == 9:  # 누적관객수
                                                            scoreAcc = tag6.text.strip()
                                                        if i == 10:  # 스크린수
                                                            screen = tag6.text.strip()
                                                        if i == 11:  # 상영쵯수
                                                            playing = scoreAcc = tag6.text.strip()
                                                    i += 1

                                                if self.isPrnConsole:  # ################
                                                    self.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}'.format(curDate, rank, movieCd, movieNm, openDt, salesAmk, share, salesAmkGap, salesAmkAgo, salesAmkAcc, score, scoreGap, scoreAgo, scoreAcc, screen, playing))

                                                self.dicBoxoffice[curDate + ';' + str(no)] = [rank, movieCd, movieNm]

                                                no += 1
        # print(self.dicBoxoffice)
    #
    #
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) 에서 영화상영관정보를 가지고 온다. (dicTheaters)
    #
    def __crawl_kobis_theaters_JobA(self):

        self.logger.info('')
        self.logger.info('### 영화정보검색/영화상영관정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do) ###  [__crawl_kobis_theaters_JobA(self)]')

        mov_count = 0

        url = 'http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterInfoList.do'

        fields = {"pageIndex": "1",
                  "sPermYn": "Y",
                  "sJoinYn": "Y",
                  "sSaleStat": "018201",
                  "theaCd": "",
                  "sTheaNm": "",
                  "sTheaCd": "",
                  "sWideareaCd": "",
                  "sBasareaCd": "",
                  "sSenderCd": ""
                  }
        r = self.http.request('POST', url, fields)
        # time.sleep(self.delayTime)

        data = r.data.decode('utf-8')

        soup = BeautifulSoup(data, 'html.parser')
        tag = soup.find('em', class_='fwb')
        # print(tag.text)

        totalRecode = int(tag.text.replace("총 ", "").replace("건", ""))
        totalPage, remainder = divmod(totalRecode, 10)  # 숫자를 10으로 나눈 몫과 나머지를 계산합니다.

        if remainder > 0:
            totalPage += 1  # 나머지가 0보다 크면 몫에 1을 더합니다.

        no = 0
        for page in range(1, totalPage+1):  # 페이지별로 순환

            # if page == range(1, 2):  # 디버깅용 2개 페이지에 해당하는 극장만...
            #    continue

            fields = {"pageIndex": page,
                      "sPermYn": "Y",
                      "sJoinYn": "Y",
                      "sSaleStat": "018201",
                      "theaCd": "",
                      "sTheaNm": "",
                      "sTheaCd": "",
                      "sWideareaCd": "",
                      "sBasareaCd": "",
                      "sSenderCd": ""
                     }
            r = self.http.request('POST', url, fields)
            #time.sleep(self.delayTime)

            data = r.data.decode('utf-8')
            # print(data)
            # self.logger.info(data)

            soup = BeautifulSoup(data, 'html.parser')

            tags1 = soup.select("table.tbl_comm > tbody > tr")  # 극장리스트테이블에서 극장정보를 가지고 온다.
            if len(tags1) == 0:  # 없으면 마지막이므로 탈출!!
                continue

            for tag1 in tags1:

                no += 1  # 일련번호
                i = 0
                locName1 = ""
                locName2 = ""
                theaterCd = ""
                theaterNm = ""
                scrreenNum = ""
                seetNum = ""
                permanentYn = ""
                joinYn = ""
                businessOper = ""
                openDt = ""
                SalleingYn = ""

                for tag1td in tag1.findChildren("td", recursive=False):
                    #  print(tag1td)
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

                if self.isPrnConsole:  # ################
                    self.logger.info('page:{0}, no:{1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}'.format(page, no, theaterCd, theaterNm, locName1+' '+locName2, scrreenNum, seetNum, permanentYn, joinYn, businessOper, openDt, SalleingYn))
                #

                # 극장코드 정보 저장 (, 상영스케쥴 Dic(B), 스크린정보 Dic(C), 상영관 Dic(E), 상영정보 Dic(E) ... )
                #  self.dicTheather[theaterCd] = [theaterNm, {}, {}, {}, {}, locName1 + ' ' + locName2, scrreenNum, seetNum, permanentYn, joinYn, businessOper, openDt, SalleingYn]
                self.dicTheather[theaterCd] = [theaterNm, {}, {}, {}, {}, scrreenNum]
            #
            # break  ######################################################################################################## 디버그 용

            # if page == 1:  # 디버깅용
            #    break
        #
    #
    #
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # 영화정보/영화상영관/상영스케줄  (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) 에서 상영스케줄을 가지고 온다.
    #
    def __crawl_kobis_theaters_JobB(self):

        self.logger.info('')
        self.logger.info('### 영화정보/영화상영관/상영스케줄 (http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do) ###  [__crawl_kobis_theaters_JobB(self)]')

        loopCnt = 0
        dicLoop = {}

        for key in self.dicTheather.keys():  # 극장리스트 만큼 순환

            theatherCd = key
            theatherNm = (self.dicTheather[key])[0]

            days = []

            date1 = datetime.date.today()  # 오늘자 날짜객체
            date2 = date1 + datetime.timedelta(days=1)  # +1 일
            date3 = date2 + datetime.timedelta(days=1)  # +2 일
            date4 = date3 + datetime.timedelta(days=1)  # +3 일
            date5 = date4 + datetime.timedelta(days=1)  # +4 일
            date6 = date5 + datetime.timedelta(days=1)  # +5 일
            date7 = date6 + datetime.timedelta(days=1)  # +6 일

            days.append('{:04d}{:02d}{:02d}'.format(date1.year, date1.month, date1.day))  # 오늘의 날짜
            if self.dateRage >= 1:
                days.append('{:04d}{:02d}{:02d}'.format(date2.year, date2.month, date2.day))  # 오늘+1의 날짜
            if self.dateRage >= 2:
                days.append('{:04d}{:02d}{:02d}'.format(date3.year, date3.month, date3.day))  # 오늘+2의 날짜
            if self.dateRage >= 3:
                days.append('{:04d}{:02d}{:02d}'.format(date4.year, date4.month, date4.day))  # 오늘+3의 날짜
            if self.dateRage >= 4:
                days.append('{:04d}{:02d}{:02d}'.format(date5.year, date3.month, date5.day))  # 오늘+4의 날짜
            if self.dateRage >= 5:
                days.append('{:04d}{:02d}{:02d}'.format(date6.year, date6.month, date6.day))  # 오늘+5의 날짜
            if self.dateRage >= 6:
                days.append('{:04d}{:02d}{:02d}'.format(date7.year, date7.month, date7.day))  # 오늘+6의 날짜

            # 1 ~ 7 일간 자료 가져오기
            for today in days:
                dicLoop[loopCnt] = [theatherCd, theatherNm, today,  False]
                loopCnt = loopCnt + 1
                #self.crawl_kobis_theaters_JobB_sub(dicSchedule, schNo, theatherCd, today)
            #
        # for key in self.dicTheather.keys():  # 극장리스트 만큼 순환

        isDone = False  # 종료여부를 확인!
        while not isDone:
            cntTry = 0

            _theatherCdOld = ""
            for i in range(0, loopCnt):
                _theatherCd = dicLoop[i][0]
                _theatherNm = dicLoop[i][1]
                _today = dicLoop[i][2]
                _isDone = dicLoop[i][3]

                if _theatherCdOld != _theatherCd:
                    dicSchedule = {}  # 해당극장의 일자별 스케쥴

                if not _isDone:
                    cntTry = cntTry + 1

                    if self.isPrnConsole:  # ################
                        self.logger.info('-------------------------------------')
                        self.logger.info('극장 : (' + _theatherCd + ') ' + _theatherNm)
                        self.logger.info('일자,극장코드,관,no,상영시간,영화코드,영화명')
                        self.logger.info('-------------------------------------')

                    try:
                        self.crawl_kobis_theaters_JobB_sub(dicSchedule, _theatherCd, _today)
                    except JSONDecodeError as e:  #  json decode 오류발생시
                        dicLoop[i][3] = False  # 실폐!!
                    finally:
                        dicLoop[i][3] = True  # 성공!!!
                #
                _theatherCdOld = _theatherCd
            #

            if cntTry == 0:  # 단 한번도 시도되지 않았다면 완전 수행됨으로 빠져나간다.
                isDone = True
    #

    def crawl_kobis_theaters_JobB_sub(self, dicSchedule, theatherCd, today):

        # time.sleep(self.delayTime)
        url = 'http://www.kobis.or.kr/kobis/business/mast/thea/findSchedule.do'
        fields = {"showDt": today, "theaCd": theatherCd}

        r = self.http.request('POST', url, fields)
        data = r.data.decode('utf-8')
        # print(data)

        json_obj = json.loads(data)  # json 로딩 성공하면.....

        schedule_list = json_obj["schedule"]
        if len(schedule_list) == 0:  # 해당날에 해당극장에 상영하는 영화가 아애 없다
            dicSchedule[today + ';' + "0"] = ['', '', '']
            (self.dicTheather[theatherCd])[1] = dicSchedule

        schNo = 0
        for val in schedule_list:
            movieCd = val['movieCd']
            movieNm = html.unescape(val['movieNm'])  # 특수문자 때문
            movieNm = movieNm.replace('-', '-')  # 특수문자 때문
            movieNm = movieNm.replace('–', '-')  # 특수문자 때문
            scrnNm = val['scrnNm']
            showTms = val['showTm']

            lstTms = showTms.split(',')
            for showTm in lstTms:

                if self.isPrnConsole:  # ################
                    self.logger.info('{0}, {1}, {2}, {3}, {4}, {5}'.format(today, theatherCd, scrnNm, showTm[:2] + ':' + showTm[-2:], movieCd, movieNm))
                #dicSchedule[today + ';' + str(schNo)] = [scrnNm, showTm, movieCd, movieNm]  # dicSchedule[today + ';' + str(schNo)] = [theatherCd, theatherNm, scrnNm, showTm, movieCd, movieNm]
                dicSchedule[today + ';' + str(schNo)] = [scrnNm, showTm, movieCd]  # movieNm 제거
                schNo = schNo + 1

                self.dicMovies[movieCd] = movieNm
            #
            (self.dicTheather[theatherCd])[1] = dicSchedule

    #
    #
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) 에서 개별상영관정보를 가지고 온다. (dicTheaters)
    #
    def __crawl_kobis_theaters_JobC(self):

        self.logger.info('')
        self.logger.info('### 영화정보검색/영화상영관상세정보(http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=[theaterCd]) ### [__crawl_kobis_theaters_JobC(self)]')

        for key in self.dicTheather.keys():  # 극장리스트 만큼 순환

            dicScreen = {}  # 해당극장의 상영관

            theatherCd = key
            theatherNm = (self.dicTheather[key])[0]

            url = 'http://www.kobis.or.kr/kobis/business/mast/thea/findTheaterCodeLayer.do?theaCd=' + theatherCd
            r = self.http.request('GET', url)

            data = r.data.decode('utf-8')
            # print(data)

            soup = BeautifulSoup(data, 'html.parser')

            tags1 = soup.select("div.title_pop02 > strong.tit")  #
            for tag1 in tags1:
                # print(tag1.text.strip())
                theaterNm = tag1.text.strip()

            tags1 = soup.select("div#pop_content02 > table.tbl_99 > tbody > tr")  #
            for tag1 in tags1:
                for tag2 in tag1.children:
                    if tag2 != '\n':
                        tagNm = tag2.name  # th 아니면 td
                        # print(tag2.name)
                        for tag3 in tag2:
                            tagVal = tag3.strip()
                            # print(tag3.strip())

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

            if self.isPrnConsole:  # ################
                self.logger.info('{0}, {1}, {2}, {3}, {4}, {5}, {6}'.format(theaterCd, theaterNm, businessOper, telNo, openDt, homePage, address))

            lstScreenCd = []
            lstScreenNm = []
            lstSeatNum = []

            tags1 = soup.select("div#pop_content02 > table.tbl3 > thead > tr")  #
            for tag1 in tags1:
                tags2 = tag1.select("th.tac")
                for tag2 in tags2:
                    # print(tag2)
                    lstScreenCd.append(tag2.text.strip())  # 상영관 코드
            #

            tags1 = soup.select("div#pop_content02 > table.tbl3 > tbody > tr")  #
            for tag1 in tags1:
                tags2 = tag1.select("th.tac")
                for tag2 in tags2:
                    # print(tag2)
                    lstScreenNm.append(tag2.text.strip())  # 스크린명
                tags2 = tag1.select("td.tac")
                for tag2 in tags2:
                    # print(tag2)
                    lstSeatNum.append(tag2.text.strip())  # 좌석수
            #

            if self.isPrnConsole:  # ################
                self.logger.info(lstScreenCd)
                self.logger.info(lstScreenNm)
                self.logger.info(lstSeatNum)

            i = 0
            for screenCd in lstScreenCd:
                dicScreen[screenCd] = (lstScreenNm[i], lstSeatNum[i])

                i += 1
            #

            (self.dicTheather[theatherCd])[2] = dicScreen

        # for key in self.dicTheather.keys():  # 극장리스트 만큼 순환

        # print(self.dicTheather)
    #
    #
    # ---------------------------------------------------------------------------------------------

    # ---------------------------------------------------------------------------------------------
    # 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) 에서 상영내역을 가지고 온다.
    #
    def __crawl_kobis_theaters_JobE(self):

        self.logger.info('')
        self.logger.info('### 영화정보검색/영화상영관/상영내역(http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistory.do) ###  [__crawl_kobis_theaters_JobE(self)]')

        dateSt = datetime.date.today()  # 오늘자 날짜객체
        dateEd = dateSt + datetime.timedelta(days=self.dateRage)  # +self.dateRage 일

        strDateSt = format('{:04d}-{:02d}-{:02d}'.format(dateSt.year, dateSt.month, dateSt.day))  #
        strDateEd = format('{:04d}-{:02d}-{:02d}'.format(dateEd.year, dateEd.month, dateEd.day))  #

        for key in self.dicTheather.keys():  # 극장리스트 만큼 순환

            dicShowRoom = {}  # 해당극장의 상영관
            dicPlaying = {}  # 해당극장의 상영정보

            theatherCd = key
            theatherNm = (self.dicTheather[key])[0]

            if self.isPrnConsole:  # ################
                self.logger.info('{0}, {1}'.format(theatherCd, theatherNm))

            if theatherCd != "015070":  # 디버깅용 (CGV 인천가정)
                continue

            url = 'http://www.kobis.or.kr/kobis/business/mast/thea/findShowHistorySc.do'
            fields = {# "CSRFToken": "ZRJQ_SVbJiXj_PDDbYGl_QPRaRF9G9mepDvLVaXGiRQ",
                      "theaCd": "",
                      "theaArea": "Y",
                      "showStartDt": strDateSt,
                      "showEndDt": strDateEd,
                      "sWideareaCd": "",
                      "sBasareaCd": "",
                      "sTheaCd": theatherCd,
                      "choice": "1",
                      "sTheaNm": ""
                      # "sTheaNm": theatherNm
            }
            r = self.http.request('POST', url, fields)

            data = r.data.decode('utf-8')
            # print(fields)
            # print(data)

            soup = BeautifulSoup(data, 'html.parser')

            # 영화상영관 정보
            lstShowroom = []
            lstSeatnum = []

            tags1 = soup.select("table.tbl3.info2 > thead > tr")  # 상영관
            for tag1 in tags1:
                tags2 = tag1.select("th")  #
                for tag2 in tags2:
                    # print(tag2.text.strip())
                    tmpStr = tag2.text.strip()
                    if not (tmpStr.find('상영관') == 0 or (tmpStr.find('총') == 0 and tmpStr.find('관') > 0)):
                        # print(tmpStr)
                        lstShowroom.append(tmpStr)

            tags1 = soup.select("table.tbl3.info2 > tbody > tr")  # 좌석수
            for tag1 in tags1:
                for tag2 in tag1.findChildren(recursive=False):
                    # print(tag2)
                    tmpStr = tag2.text.strip()
                    if not (tmpStr.find('좌석수') == 0 or (tmpStr.find('총') == 0 and tmpStr.find('개') > 0)):
                        # print(tmpStr)
                        lstSeatnum.append(tmpStr)

            if self.isPrnConsole:  # ################
                self.logger.info('{0}, {1}'.format('상영관', lstShowroom))
                self.logger.info('{0}, {1}'.format('좌석수', lstSeatnum))

            dicPlayDt = {}
            dicShowroom = {}
            i = 0
            for showroom in lstShowroom:
                dicShowRoom[showroom] = lstSeatnum[i]

                i += 1
            #

            # 상영내역
            lstInningNm = []
            tags1 = soup.select("table.tbl3.info3 > thead > tr")  # 상영일자, 상영관, 1회,  2회, 3회, ......
            for tag1 in tags1:
                tags2 = tag1.select("th")  #
                for tag2 in tags2:
                    # print(tag2.text.strip())
                    tmpStr = tag2.text.strip()
                    if not (tmpStr.find('상영관') == 0 or tmpStr.find('상영일자') == 0):
                        # print(tmpStr.replace("회", ""))
                        lstInningNm.append(tmpStr.replace("회", ""))

            j = 0
            rowspan = 1
            dicInning = {}  # 회차 정보
            # 상영내역 일자별 상영관별
            tags1 = soup.select("table.tbl3.info3 > tbody > tr")  #
            for tag1 in tags1:
                playTm = ''
                movieNm = ''
                unitprice = ''

                i = 0
                minusVal = 1  # 2 번째부터 0

                tags2 = tag1.select("td")  #
                if (len(lstInningNm) + 1 == len(tags2)) or (len(tags2) == len(lstInningNm) + 2):  # 현대예술관시네마
                    for tag2 in tags2:
                        # if i == 0 and len(tags2) == len(lstInningNm)+2:  # 첫컬럼이 '상영일자' 가 있는 태그
                        if i == 0 and tag2.has_attr("rowspan"):  # 첫컬럼이 rowspan의 속성을 가지고 있는 태그
                            minusVal = 2  # 3 번째부터 0
                            rowspan = int(tag2.get('rowspan'))
                            playDt = tag2.text.strip()  # 상영일자
                            playDt = playDt[0:4] + playDt[5:7] + playDt[8:10]

                            i += 1
                            continue

                        if i == (minusVal-1):  # '상영관'
                            showroom = tag2.text.strip()
                            # print(tag2.text.strip())
                        else:
                            listDate = list(tag2.stripped_strings)  # 내용이 붉은 색이여도 바로 잡아준다!!
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
                                movieNm = html.unescape(listDate[1].strip())  # 특수문자 때문
                                movieNm = movieNm.replace('-', '-')  # 특수문자 때문
                                movieNm = movieNm.replace('–', '-')  # 특수문자 때문
                                movieNm = movieNm.replace('\xa0', ' ')  # 특수문자 때문
                                movieNm = movieNm.replace('\xA0', ' ')  # 특수문자 때문

                                dicInning[lstInningNm[i - minusVal]] = [playTm, unitprice, movieNm]
                        i += 1

                    dicShowroom[showroom] = dicInning
                    dicInning = {}

                    j += 1
                    if rowspan == j:   # rowspan의 끝
                        dicPlayDt[playDt] = dicShowroom
                        dicShowroom = {}
                        j = 0
            no = 0
            for keyDt, playDt in dicPlayDt.items():
                for keyRm, showroom in playDt.items():
                    for keyInn, inning in showroom.items():
                        if self.isPrnConsole:  # ################
                            self.logger.info('{0}, {1}, {2}, {3}'.format(keyDt, keyRm, keyInn, inning))

                        dicPlaying[no] = (keyDt, keyRm, keyInn, inning[0], inning[2], inning[1])  # [0].playTm, [1].unitprice, [2].movieNm
                        no += 1

            (self.dicTheather[theatherCd])[3] = dicShowRoom
            # (self.dicTheather[theatherCd])[4] = dicPlaying # ??!!

            # print(dicShowRoom)
            # print(dicPlaying)
        # for key in self.dicTheather.keys():  # 극장리스트 만큼 순환
    #
    #
    # ---------------------------------------------------------------------------------------------

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

    #

    # kobis["theather"] = self.dicTheather

    # list(self.dicTheather)[10]  # 9 번째의 키를 리턴한다.
    # len(self.dicTheather)  # 딕셔너리의 갯수
    # d = {'a': 'aaa', 'b': 'bbb', 'c': 'ccc'}
    # newd = dict((k, d[k]) for k in ("a", "b"))  # a,b 의 부분만 새로 딕셔너리를 복사한다.

    # kobis = {"boxoffice": self.dicBoxoffice, "theather": self.dicTheather, "movies": self.dicMovies}
    def uplodding(self, baseTime):
        try:
            self.logger.info('')
            self.logger.info('=====================')
            self.logger.info('json 파일로 저장')
            self.logger.info('---------------------')

            gubunNm = "movies"
            with open("jsons/kobis_" + gubunNm + ".json", "w", encoding="utf-8") as fp:
                json.dump({gubunNm: self.dicMovies}, fp, ensure_ascii=False)

            cntPage = 0  # 페이지 수 카운트
            pageUnit = 10  # 페이징 단위..

            lenTheather = len(self.dicTheather)  # 극장 총 수
            page, rest = divmod(lenTheather, pageUnit)  # pageUnit개씩 페이징 ( 몫,나머지 )

            gubunNm = "theather"
            for i in range(0, page):
                cntPage = cntPage + 1

                tmpDic = dict((k, self.dicTheather[k]) for k in list(self.dicTheather)[i * pageUnit: i * pageUnit + pageUnit])
                with open("jsons/kobis_" + gubunNm + "_"+str(i).zfill(3)+".json", "w", encoding="utf-8") as fp:
                    json.dump({gubunNm: tmpDic}, fp, ensure_ascii=False)

            if rest > 0:
                cntPage = cntPage + 1

                tmpDic = dict((k, self.dicTheather[k]) for k in list(self.dicTheather)[page * pageUnit: page * pageUnit + rest])
                with open("jsons/kobis_" + gubunNm + "_" + str(page).zfill(3) + ".json", "w", encoding="utf-8") as fp:
                    json.dump({gubunNm: tmpDic}, fp, ensure_ascii=False)

            gubunNm = "boxoffice"
            with open("jsons/kobis_" + gubunNm + ".json", "w", encoding="utf-8") as fp:
                json.dump({gubunNm: self.dicBoxoffice}, fp, ensure_ascii=False)
            # cntPage =0
            """
            self.logger.info('---------------------')
            self.logger.info('kobis.zip 파일로 압축')
            self.logger.info('---------------------')
            zip_file = zipfile.ZipFile("jsons/kobis.zip", "w")
            for file in os.listdir("."):
                if file.endswith('jsons/kobis.json'):
                    zip_file.write(os.path.join(".", file), compress_type=zipfile.ZIP_DEFLATED)
            zip_file.close()
            """

            self.logger.info('')
            self.logger.info('=====================')
            self.logger.info('json 파일들 업로드')
            self.logger.info('---------------------')

            dt = datetime.datetime.today()  # 오늘자 날짜객체
            self.logger.info("### KOBIS 서버 전송 시작 ({:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}) ###".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))

            baseUrl = "http://www.mtns7.co.kr/totalscore/upload_kobis_file.php?baseTime={}".format(baseTime)

            gubunNm = "jsons/kobis_movies.json"
            r = requests.post(baseUrl, files={'upload': open(gubunNm, "rb")})
            # os.remove(gubunNm)
            self.logger.info(r.text)  # unicode(str, 'utf-8').encode('euc-kr')

            gubunNm = "jsons/kobis_theather"
            for i in range(0, cntPage):
                files = {'upload': open(gubunNm + "_" + str(i).zfill(3) + ".json", "rb")}
                r = requests.post(baseUrl, files=files)
                # os.remove(gubunNm + "_" + str(i).zfill(3) + ".json")
                self.logger.info(r.text)  # unicode(str, 'utf-8').encode('euc-kr')

            gubunNm = "jsons/kobis_boxoffice.json"
            r = requests.post(baseUrl, files={'upload': open(gubunNm, "rb")})
            # os.remove(gubunNm)
            self.logger.info(r.text)  # unicode(str, 'utf-8').encode('euc-kr')

            #url = 'http://www.mtns7.co.kr/totalscore/upload_kobis.php'
            #r = self.http.request('POST', url, kobis)
            #data = r.data.decode('utf-8')
            #print('[', data, ']')
        except:
            self.logger.error('KOBIS 전송 중 오류발생!')
            raise
        finally:
            dt = datetime.datetime.today()  # 오늘자 날짜객체
            self.logger.info("### KOBIS 서버 전송 완료 ({:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}) ###".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
            self.logger.info('')
    #
# def uplodding(self):


if __name__ == '__main__':

    maxDateRage = 6  # 최대 일수
    dateRage = 2  # 디폴트 크롤링 일수 (+6일)

    if len(sys.argv) == 2:
        try:
            dateRage = int(sys.argv[1])

            if dateRage < 0:  # 0 이면 당일
                dateRage = 0
            if dateRage > maxDateRage:
                dateRage = maxDateRage
        except ValueError:
            dateRage = maxDateRage

    logger = get_logger('kobis')

    now = time.localtime()
    crawlKobis = CrawlKobis(True, logger, dateRage)  # Kobis
    crawlKobis.crawling()
    crawlKobis.uplodding("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

    clean_logger('kobis')

#  if __name__ == '__main__':