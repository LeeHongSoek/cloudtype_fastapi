"""

"""
from Crawlling2.Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import sys
import traceback
import sqlite3
import time
import json
import html
import datetime

from urllib.request import urlopen
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import urllib3  # pip install urllib3

class ActCrlMega(ActCrlSupper):

    # __init__, __del__ =======================================================================================================================================

    def __init__(self, date_range): # 생성자

        self.logger = get_logger('Mega')   # 파이션 로그
        self.date_range = date_range        # 크롤링 할 날 수

        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('Mega')  # 한달전 로그파일을 삭제한다.
        super().__del__(type(self).__name__)
    # [def __del__(self): # 소멸자]


    # def crawling(self): =====================================================================================================================================

    def crawling(self):

        # =====================================================================================================================================================
        # 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다.
        #
        def _1_crawl_mega_movie():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('### 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다. ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            self.logger.info('-------------------------------------')
            self.logger.info('영화코드 : 개봉일자, 구분, 영화명    ')
            self.logger.info('-------------------------------------')

            url = 'https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do'
            fields = { "currentPage": "1"
                     , "recordCountPerPage": "1"
                     , "pageType": "ticketing"
                     , "ibxMovieNmSearch": ""
                     , "onairYn": "N"
                     , "specialType": ""
                     }
            data1 = self.http.request('POST', url, fields).data.decode('utf-8') # self.logger.info(data)
            time.sleep(self.delayTime)

            url = 'https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do'
            fields = { "currentPage": "1"
                     , "recordCountPerPage": json.loads(data1)["totCnt"]
                     , "pageType": "ticketing"
                     , "ibxMovieNmSearch": ""
                     , "onairYn": "N"
                     , "specialType": ""
                     }
            data2 = self.http.request('POST', url, fields).data.decode('utf-8')
            time.sleep(self.delayTime)
            
            for val in json.loads(data2)["movieList"]:

                moviecode = val['movieNo']
                releasedate = val['rfilmDeReal']
                moviegbn = val['admisClassNm']
                moviename = html.unescape(val['movieNm'])
                moviename = moviename.replace("'", "")

                self.dicMovies[moviecode] = [releasedate, moviegbn, moviename]  # 영화데이터 정보
                self.dicMoviesNm[moviename] = moviecode                         # 영화이름을 코드체크

                self.logger.info(f'{moviecode} : {releasedate}, {moviegbn}, {moviename}')
            #
        # [1_crawl_mega_movie():]

        # =====================================================================================================================================================
        # 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다.
        #
        def _2_crawl_mega_cinema():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('### 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다. ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            self.logger.info('-------------------------------------')
            self.logger.info('코드 : 지역명                        ')
            self.logger.info('+-   코드 : 극장명                     ')
            self.logger.info('-------------------------------------')

            data = urlopen("https://www.megabox.co.kr/theater/list").read().decode('utf-8') 
            soup = BeautifulSoup(data, 'html.parser') # print(data)

            for tag1 in soup.select("div#contents > div > div.theater-box > div.theater-place > ul > li "):  # > button.sel-city # print(tag1)

                region_cd = ''
                for tag2 in tag1.select("button"):

                    region_nm = str(tag2.text.strip())  # 지역이름
                    region_cd = self.regions[region_nm]  # 지역코드를 지역이름으로 찾는다. # print(regionCd+' ['+regionNm+']')

                    self.logger.info(f'{region_cd} : {region_nm}')

                    self.dicRegions[region_cd] = region_nm  # 지역코드 저장
                #

                for tag2 in tag1.select("div.theater-list"): # print(tag2)

                    for tag3 in tag2.select("li > a"): # print(tag3)

                        cinemaname = tag3.text.strip()  # 극장명
                        href = tag3['href']
                        midxs = href.split('=')
                        cinemacode = ''

                        if len(midxs) == 2:
                            cinemacode = midxs[1]                        

                        self.logger.info(f'+-   {cinemacode} : {cinemaname}')

                        self.dicCinemas[cinemacode] = [region_cd, cinemaname, '']
                    #
                #
            # [for tag1 in soup.select("div#contents > div > div.theater-box > div.theater-place > ul > li "):]
        # [def _2_crawl_mega_cinema():]

        # =====================================================================================================================================================
        # 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다.
        #
        def _3_crawl_mega_schedule():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('### 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다. ###')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            days = []

            date1 = datetime.date.today()  # 오늘자 날짜객체
            date2 = date1 + datetime.timedelta(days=1)  # +1 일
            date3 = date2 + datetime.timedelta(days=1)  # +2 일
            date4 = date3 + datetime.timedelta(days=1)  # +3 일
            date5 = date4 + datetime.timedelta(days=1)  # +4 일
            date6 = date5 + datetime.timedelta(days=1)  # +5 일
            date7 = date6 + datetime.timedelta(days=1)  # +6 일
            date8 = date7 + datetime.timedelta(days=1)  # +7 일
            date9 = date8 + datetime.timedelta(days=1)  # +8 일
            date10 = date9 + datetime.timedelta(days=1)  # +9 일
            date11 = date10 + datetime.timedelta(days=1)  # +10 일
            date12 = date11 + datetime.timedelta(days=1)  # +11 일
            date13 = date12 + datetime.timedelta(days=1)  # +12 일

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
            if self.dateRage >= 7:
                days.append('{:04d}{:02d}{:02d}'.format(date8.year, date8.month, date8.day))  # 오늘+7의 날짜
            if self.dateRage >= 8:
                days.append('{:04d}{:02d}{:02d}'.format(date9.year, date9.month, date9.day))  # 오늘+8의 날짜
            if self.dateRage >= 9:
                days.append('{:04d}{:02d}{:02d}'.format(date10.year, date10.month, date10.day))  # 오늘+9의 날짜
            if self.dateRage >= 10:
                days.append('{:04d}{:02d}{:02d}'.format(date11.year, date11.month, date11.day))  # 오늘+10의 날짜
            if self.dateRage >= 11:
                days.append('{:04d}{:02d}{:02d}'.format(date12.year, date12.month, date12.day))  # 오늘+11의 날짜
            if self.dateRage >= 12:
                days.append('{:04d}{:02d}{:02d}'.format(date13.year, date13.month, date13.day))  # 오늘+12의 날짜

            no_rooms = 0

            # 1 ~ 13 일간 자료 가져오기
            for play_de in days:

                #if play_de != '20210128':
                #    continue
                # if play_de != '20200602' and play_de != '20200603' and play_de != '20200604' and play_de != '20200605' and play_de != '20200606' and play_de != '20200607' and play_de != '20200608' and play_de != '20200609':
                #    continue
                dic_playdate = {}  # 상영일자

                for cinema_cd in self.dicCinemas:  # 극장리스트 만큼 순환

                    #if cinema_cd != '6906':
                    #    continue
                    dic_sch_rooms = {}  # 스케쥴 원시정보
                    dic_sch_movies = {}

                    url = 'https://www.megabox.co.kr/on/oh/ohc/Brch/schedulePage.do'
                    fields = { "masterType": "brch"
                             , "detailType": "area"
                             , "brchNo": cinema_cd
                             , "firstAt": "N"
                             , "brchNo1": cinema_cd
                             , "crtDe": play_de
                             , "playDe": play_de
                             }
                    data = self.http.request('POST', url, fields).data.decode('utf-8')
                    time.sleep(self.delayTime)

                    json_obj = json.loads(data) # print(json_obj['megaMap']['movieFormList'])

                    moviecode = ''
                    cnt_room = 1

                    for schl in json_obj['megaMap']['movieFormList']:  # print(schl)

                        no_rooms += 1
                        cnt_room += 1
                        # if moviecode == schl['movieNo']:
                        # else:
                        #    cnt_room = 1

                        moviecode = schl['movieNo']
                        moviegbn = schl['admisClassCdNm']
                        moviename = '' if schl['movieNm'] is None else html.unescape(schl['movieNm'])  # 삼항연산자
                        moviename = moviename.replace("'", "")
                        cinemaroom = '' if schl['theabExpoNm'] is None else html.unescape(schl['theabExpoNm'])  # 삼항연산자
                        start_time = schl['playStartTime']
                        end_time = schl['playEndTime']
                        moviegubun = '' if schl['playKindNm'] is None else html.unescape(schl['playKindNm'])  # 삼항연산자
                        rest_seat_cnt = schl['restSeatCnt']
                        theab_seat_cnt = schl['theabSeatCnt']

                        if not self.dicMovies.get(moviecode):

                            old_moviecode = moviecode

                            if self.dicMoviesNm.get(moviename):

                                moviecode = self.dicMoviesNm[moviename]
                                self.logger.info(f'{old_moviecode} -> {moviecode}, {moviename}')
                            else:
                                self.dicMovies[moviecode] = ['', '', moviename]  # 영화데이터 정보
                                self.dicMoviesNm[moviename] = moviecode  # 영화이름을 코드체크

                        self.logger.info(f'{no_rooms} : /{play_de}/ {cinema_cd}, {moviecode}, {moviename}, {moviegubun}, {moviegbn}, {cnt_room}, {cinemaroom}, {str(rest_seat_cnt)} / {str(theab_seat_cnt)}, {start_time}, {end_time}')

                        dic_sch_rooms[no_rooms] = [moviecode, moviename, moviegubun, moviegbn, cnt_room, cinemaroom, rest_seat_cnt, theab_seat_cnt, start_time, end_time]  # 일단 다 펴와서..
                    # [for schl in json_obj['megaMap']['movieFormList']: ]

                    # 영화별로 추려내고
                    old_moviecode = ''
                    for k, v in dic_sch_rooms.items():

                        if old_moviecode != str(v[0]):

                            if len(str(v[0])) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                moviecode8 = str(v[0]) + '00'
                            else:
                                moviecode8 = str(v[0])
                            dic_sch_movies[moviecode8] = [v[1], v[2], v[3]]  # dic_sch_movies[moviecode] = [moviename, moviegubun, moviegbn] 만 이동..
                            old_moviecode = str(v[0])

                    # 영화별 아래 관 추가
                    for km, vm in dic_sch_movies.items():

                        dic_movies_room = {}
                        for k, v in dic_sch_rooms.items():

                            if len(str(km)) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                moviecode8_km = str(km) + '00'
                            else:
                                moviecode8_km = str(km)
                            if len(str(v[0])) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                moviecode8 = str(v[0]) + '00'
                            else:
                                moviecode8 = str(v[0])

                            if moviecode8_km == moviecode8:  # 같은 영화 [moviecode[0], moviename, moviegubun, moviegbn[3], cnt_room[4], cinemaroom[5], rest_seat_cnt, theab_seat_cnt[7], start_time, end_time]
                                dic_movies_room[str(v[5])] = [v[3], v[4], v[7]]

                        for kr, vr in dic_movies_room.items():
                            dic_sch_movies_room_time = {}
                            for k, v in dic_sch_rooms.items():

                                if len(str(km)) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                    moviecode8_km = str(km) + '00'
                                else:
                                    moviecode8_km = str(km)
                                if len(str(v[0])) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                    moviecode8 = str(v[0]) + '00'
                                else:
                                    moviecode8 = str(v[0])

                                if moviecode8_km == moviecode8 and str(kr) == str(v[5]):  # 같은 영화,관 [moviecode[0], moviename, moviegubun, moviegbn, cnt_room[4], cinemaroom[5], rest_seat_cnt[6], theab_seat_cnt, start_time[8], end_time[9]]
                                    dic_sch_movies_room_time[str(v[8])] = [v[6], v[9]]

                            dic_movies_room[kr].append(dic_sch_movies_room_time)
                        dic_sch_movies[km].append(dic_movies_room) # print(dic_sch_movies)
                    dic_playdate[cinema_cd] = dic_sch_movies
                #

                self.dicTicketingData[play_de] = dic_playdate # print(self.dicTicketingData)
        # [def _3_crawl_mega_schedule():]


        try:
            
            _1_crawl_mega_movie()    # 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다.
            _2_crawl_mega_cinema()   # 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다.
            _3_crawl_mega_schedule() # 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다.        
        except Exception as e:    

            self.logger.error('Mega 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):]

    # def uploading(self): ====================================================================================================================================
    
    def uploading(self):
        
        print("Uploading Mega data...")
    # [def uploading(self):]
# [class ActCrlMega(ActCrlSupper):]

if __name__ == '__main__':

    maxDateRage = 12  # 최대 일수

    if len(sys.argv) == 2:
        try:
            dateRange = min(max(int(sys.argv[1]), 0), maxDateRage)
        except ValueError:
            dateRange = maxDateRage
    else:
        dateRange = maxDateRage

    actCrlMega = ActCrlMega(date_range = dateRange)  # Mega
    actCrlMega.crawling()
    actCrlMega.uploading()
    
# [if __name__ == '__main__':]    
