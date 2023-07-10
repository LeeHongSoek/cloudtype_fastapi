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


class ActCrlMega(ActCrlSupper):

    def __init__(self, date_range): # 생성자

        self.logger = get_logger('Mega')   # 파이션 로그
        self.date_range = date_range        # 크롤링 할 날 수
        
        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('Mega')  # 한달전 로그파일을 삭제한다.
        super().__del__()
    # [def __del__(self): # 소멸자]


    def crawling(self):

        # =====================================================================================================================================================
        # 1. 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다.
        #
        def _1_crawl_mega_movie():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 1. ### 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다. ###                  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            url = 'https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do'
            fields = { "currentPage": "1"
                     , "recordCountPerPage": "1"
                     , "pageType": "ticketing"
                     , "ibxMovieNmSearch": ""
                     , "onairYn": "N"
                     , "specialType": ""
                     }
            r = requests.post(url, data=fields)
            time.sleep(self.delayTime)

            # 페이지당 레코드수를 조정해서 한번에 읽어오도록 한다.
            fields = { "currentPage": "1"
                     , "recordCountPerPage": r.json()["totCnt"]
                     , "pageType": "ticketing"
                     , "ibxMovieNmSearch": ""
                     , "onairYn": "N"
                     , "specialType": ""
                     }
            r = requests.post(url, data=fields)
            time.sleep(self.delayTime)

            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('영화코드 : 개봉일자, 구분, 영화명    ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            for movieList in r.json()["movieList"]:

                moviecode = movieList['movieNo']
                releasedate = movieList['rfilmDeReal']
                moviegbn = movieList['admisClassNm']
                moviename = html.unescape(movieList['movieNm'])
                moviename = moviename.replace("'", "")

                self.logger.info(f'{moviecode} : {releasedate}, {moviegbn}, {moviename}')

                query = self.sqlxmp.find(f"query[@id='{'INSERT_mega_movie'}']").text.strip()
                parameters = (moviecode, releasedate, moviegbn, moviename)
                self.sql_cursor.execute(query, parameters)
            # [for val in r.json()["movieList"]:]

            self.sql_conn.commit()
        # [def _1_crawl_mega_movie():]

        # =====================================================================================================================================================
        # 2. 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다.
        #
        def _2_crawl_mega_cinema():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 2. ### 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다. ###                                     ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            
            r = requests.get('https://www.megabox.co.kr/theater/list')
            time.sleep(self.delayTime)

            soup = BeautifulSoup(r.text, 'html.parser') # print(data)

            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('코드 : 지역명                        ')
            self.logger.info('+-   코드 : 극장명                   ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            for tagLI in soup.select("div#contents > div > div.theater-box > div.theater-place > ul > li "):  # > button.sel-city # print(tag1)

                region_cd = ''
                for tagBUTTON in tagLI.select("button"):

                    region_nm = str(tagBUTTON.text.strip())  # 지역이름

                    # 지역이름으로 지역코드를 찾는다.  지역코드 정보가 별도로 없다.  
                    query = self.sqlxmp.find(f"query[@id='{'SELECT_regioncode_mega_region_regionname'}']").text.strip()                            
                    self.sql_cursor.execute(query, (region_nm,))
                    self.sql_cursor.row_factory = sqlite3.Row
                    result = self.sql_cursor.fetchone() # 첫 번째 결과 행 가져오기
                    if result is not None:
                        region_cd = result['regioncode']
                    else:
                        region_cd = ''

                    self.logger.info(f'{region_cd} : {region_nm}')

                    query = self.sqlxmp.find(f"query[@id='{'INSERT_mega_region'}']").text.strip()
                    parameters = (region_cd, region_nm)
                    self.sql_cursor.execute(query, parameters)
                # [for tagBUTTON in tagLI.select("button"):]

                for tagDIV in tagLI.select("div.theater-list"): # print(tag2)

                    for tagA in tagDIV.select("li > a"): # print(tag3)

                        cinemaname = tagA.text.strip()  # 극장명
                        href = tagA['href']
                        midxs = href.split('=')
                        cinemacode = ''

                        if len(midxs) == 2:
                            cinemacode = midxs[1]  # 극장코드         

                        self.logger.info(f'+-   {cinemacode} : {cinemaname}')

                        query = self.sqlxmp.find(f"query[@id='{'INSERT_mega_cinema'}']").text.strip()
                        parameters = (cinemacode, region_cd, cinemaname)
                        self.sql_cursor.execute(query, parameters)
                    # [for tagA in tagDIV.select("li > a"):]
                # [for tagDIV in tagLI.select("div.theater-list"):]
            # [for tagLI in soup.select("div#contents > div > div.theater-box > div.theater-place > ul > li "):]

            self.sql_conn.commit()
        # [def _2_crawl_mega_cinema():]

        # =====================================================================================================================================================
        # 3. 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다.
        #
        def _3_crawl_mega_schedule():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 3. ### 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다. ###         ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __3_get_date_range(dateRage):
                days = []

                date1 = datetime.date.today()  # 오늘자 날짜객체
                days.append(date1.strftime('%Y%m%d'))  # 오늘의 날짜

                for i in range(1, dateRage + 1):
                    future_date = date1 + datetime.timedelta(days=i)
                    days.append(future_date.strftime('%Y%m%d'))

                return days
            #  [def __3_get_date_range(dateRage):] 
        
            no_rooms = 0

            for playdt in __3_get_date_range(dateRange): # 1 ~ 13 일간 자료 가져오기

                #if playdt != '20210128':
                #    continue

                dic_playdate = {}  # 상영일자

                self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'SELECT_mega_cinema'}']").text.strip())
                self.sql_cursor.row_factory = sqlite3.Row
                for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환

                    cinema_cd = row['cinemacode']

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
                             , "crtDe": playdt
                             , "playDe": playdt
                             }
                    r = requests.post(url, data=fields)
                    time.sleep(self.delayTime)

                    moviecode = ''
                    cnt_room = 0

                    for schl in r.json()['megaMap']['movieFormList']:  # print(schl)

                        no_rooms += 1
                        cnt_room += 1

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

                        self.logger.info(f'{no_rooms} : /{playdt}/ {cinema_cd}, {moviecode}, {moviename}, {moviegubun}, {moviegbn}, {cnt_room}, {cinemaroom}, {str(rest_seat_cnt)} / {str(theab_seat_cnt)}, {start_time}, {end_time}')

                        dic_sch_rooms[no_rooms] = [moviecode, moviename, moviegubun, moviegbn, cnt_room, cinemaroom, rest_seat_cnt, theab_seat_cnt, start_time, end_time]  # 일단 다 펴와서..

                        query = self.sqlxmp.find(f"query[@id='{'INSERT_mega_movie_releasedate'}']").text.strip()
                        parameters = (moviecode, moviegbn, moviename)
                        self.sql_cursor.execute(query, parameters)
                    # [for schl in json_obj['megaMap']['movieFormList']: ]

                    # 영화별로 추려내고
                    old_moviecode = ''
                    for k, val_sh_rm in dic_sch_rooms.items():

                        if old_moviecode != str(val_sh_rm[0]):

                            if len(str(val_sh_rm[0])) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                moviecode8 = str(val_sh_rm[0]) + '00'
                            else:
                                moviecode8 = str(val_sh_rm[0])

                            dic_sch_movies[moviecode8] = [val_sh_rm[1], val_sh_rm[2], val_sh_rm[3]]  # dic_sch_movies[moviecode] = [moviename, moviegubun, moviegbn] 만 이동..
                            old_moviecode = str(val_sh_rm[0])
                    # [for k, val_sh_rm in dic_sch_rooms.items():]        

                    # 영화별(8자리) 아래 관 추가
                    for ky_sh_mv, v in dic_sch_movies.items():

                        dic_movies_room = {}
                        for k, val_sh_rm in dic_sch_rooms.items():

                            if len(str(ky_sh_mv)) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                moviecode8_km = str(ky_sh_mv) + '00'
                            else:
                                moviecode8_km = str(ky_sh_mv)

                            if len(str(val_sh_rm[0])) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                moviecode8 = str(val_sh_rm[0]) + '00'
                            else:
                                moviecode8 = str(val_sh_rm[0])

                            if moviecode8_km == moviecode8:  # 같은 영화
                                dic_movies_room[str(val_sh_rm[5])] = [val_sh_rm[3], val_sh_rm[4], val_sh_rm[7]] # [cinemaroom] = [moviegbn, cnt_room, theab_seat_cnt]
                        # [for k, val_sh_rm in dic_sch_rooms.items():]

                        for key_mv_rm, v in dic_movies_room.items():

                            dic_sch_movies_room_time = {}
                            for k, val_sh_rm in dic_sch_rooms.items():

                                if len(str(ky_sh_mv)) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                    moviecode8_km = str(ky_sh_mv) + '00'
                                else:
                                    moviecode8_km = str(ky_sh_mv)
                                if len(str(val_sh_rm[0])) == 6:  # 코드가 6자리이면 8자리로 확장한다.
                                    moviecode8 = str(val_sh_rm[0]) + '00'
                                else:
                                    moviecode8 = str(val_sh_rm[0])

                                if moviecode8_km == moviecode8 and str(key_mv_rm) == str(val_sh_rm[5]):  # 같은 영화,관 
                                    dic_sch_movies_room_time[str(val_sh_rm[8])] = [val_sh_rm[6], val_sh_rm[9]]  # [start_time] = [rest_seat_cnt], [end_time]
                            # [for k, val_sh_rm in dic_sch_rooms.items():]

                            dic_movies_room[key_mv_rm].append(dic_sch_movies_room_time)
                        # [for key_mv_rm in dic_movies_room.items():]

                        dic_sch_movies[ky_sh_mv].append(dic_movies_room)
                    # [for ky_sh_mv in dic_sch_movies.items():] 

                    dic_playdate[cinema_cd] = dic_sch_movies
                # [for row in self.sql_cursor.fetchall():  # 극장리스트 만큼 순환]

                for cinema_cd, v1 in dic_playdate.items():
                    for moviecode8, v2 in v1.items(): # dic_sch_movies.items()
                        for cinemaroom, v3 in v2[3].items(): # dic_movies_room.items()
                            for start_time, v4 in v3[3].items(): # dic_sch_movies_room_time.items()
                                rest_seat_cnt = v4[0]
                                end_time      = v4[1]

                                query = self.sqlxmp.find(f"query[@id='{'INSERT_mega_play'}']").text.strip()
                                parameters = (playdt, cinema_cd, moviecode8, cinemaroom, start_time, rest_seat_cnt, end_time)
                                self.sql_cursor.execute(query, parameters)

            # [for playdt in __3_get_date_range(dateRange): # 1 ~ 13 일간 자료 가져오기]

            

            self.sql_conn.commit()

        # [def _3_crawl_mega_schedule():]


        try:
            
            _1_crawl_mega_movie()    # 1. 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다.
            _2_crawl_mega_cinema()   # 2. 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다.
            _3_crawl_mega_schedule() # 3. 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다.        
        except Exception as e:    

            self.logger.error('Mega 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):]

    def uploading(self):
        
        super().uploading()
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
