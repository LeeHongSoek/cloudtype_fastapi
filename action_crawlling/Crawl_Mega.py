"""

MAGA BOX

http://www.megabox.co.kr/

"""

import sys
import html
import json
import datetime
from urllib.request import urlopen
from bs4 import BeautifulSoup  # pip install beautifulsoup4
import urllib3  # pip install urllib3
import time

from Crawl_Supper import Crawl
from Crawling_Logger import get_logger, clean_logger

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # https://sun2day.tistory.com/226

class CrawlMega(Crawl):

    # -----------------------------------------------------------------------------------
    def __init__(self, isPrnConsole, logger, dateRage):

        self.dateRage = dateRage
        self.http = urllib3.PoolManager()
        self.logger = logger  # 파이션 로그
        self.isPrnConsole = isPrnConsole  # 출력여부

        #  지역이름 : 지역코드
        self.regions = {'서울': '10',
                        '경기': '30',
                        '인천': '35',
                        '대전/충청/세종': '45',
                        '부산/대구/경상': '55',
                        '광주/전라': '65',
                        '강원': '70',
                        '제주': '80'}

        self.dicMovies = {}  # 영화 코드 정보
        self.dicMoviesNm = {}  # 영화 이름 정보 '영웅: 천하의 시작' 때문에...
        self.dicRegions = {}  # 지역코드 정보
        self.dicCinemas = {}  # 극장코드 정보

        self.dicTicketingData = {}  # 티켓팅 정보

    # -----------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------
    # 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다. (dicMovies)
    #
    def __crawl_mega_movie(self):

        self.logger.info('')
        self.logger.info('### 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다. ###')

        mov_count = 0

        url = 'https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do'
        fields = {"currentPage": "1",
                  "recordCountPerPage": "1",
                  "pageType": "ticketing",
                  "ibxMovieNmSearch": "",
                  "onairYn": "N",
                  "specialType": ""
                  }
        r = self.http.request('POST', url, fields)
        time.sleep(self.delayTime)

        data = r.data.decode('utf-8')
        # self.logger.info(data)

        json_obj = json.loads(data)

        tot_cnt = json_obj["totCnt"]

        url = 'https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do'
        fields = {"currentPage": "1",
                  "recordCountPerPage": tot_cnt,
                  "pageType": "ticketing",
                  "ibxMovieNmSearch": "",
                  "onairYn": "N",
                  "specialType": ""
                  }
        r = self.http.request('POST', url, fields)
        time.sleep(self.delayTime)

        data = r.data.decode('utf-8')
        # self.logger.info(data)

        json_obj = json.loads(data)

        movie_list = json_obj["movieList"]

        if self.isPrnConsole:  # ################
            self.logger.info('-------------------------------------')
            self.logger.info('no, 코드, 개봉일자, 구분, 영화명')
            self.logger.info('-------------------------------------')

        for val in movie_list:
            moviecode = val['movieNo']
            releasedate = val['rfilmDeReal']
            moviegbn = val['admisClassNm']
            moviename = html.unescape(val['movieNm'])
            moviename = moviename.replace("'", "")

            self.dicMovies[moviecode] = [releasedate, moviegbn, moviename]  # 영화데이터 정보
            self.dicMoviesNm[moviename] = moviecode  # 영화이름을 코드체크

            if self.isPrnConsole:  # ################
                mov_count += 1
                self.logger.info('{} : {}, {}, {}, {}'.format(mov_count, moviecode, releasedate, moviegbn, moviename))
        #

    #
    #
    # -----------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------------------------------
    # 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다. (dicCinemas)
    #
    def __crawl_mega_cinema(self):

        self.logger.info('')
        self.logger.info('### 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다. ###')

        region_count = 0
        cinema_count = 0

        if self.isPrnConsole:  # ################
            self.logger.info('-------------------------------------')
            self.logger.info('no, 코드, 지역명')
            self.logger.info('+- no, 코드, 극장명')
            self.logger.info('-------------------------------------')

        url = urlopen("https://www.megabox.co.kr/theater/list")
        data = url.read().decode('utf-8')
        # print(data)

        soup = BeautifulSoup(data, 'html.parser')

        tags1 = soup.select("div#contents > div > div.theater-box > div.theater-place > ul > li ")  # > button.sel-city
        for tag1 in tags1:
            # print(tag1)

            region_cd = ''
            tags2 = tag1.select("button")
            for tag2 in tags2:
                region_nm = str(tag2.text.strip())  # 지역이름
                region_cd = self.regions[region_nm]  # 지역코드를 지역이름으로 찾는다.
                # print(regionCd+' ['+regionNm+']')

                if self.isPrnConsole:  # ################
                    region_count += 1
                    self.logger.info('{} : {}, {}'.format(region_count, region_cd, region_nm))

                self.dicRegions[region_cd] = region_nm  # 지역코드 저장
            #

            tags2 = tag1.select("div.theater-list")
            for tag2 in tags2:
                # print(tag2)

                tags3 = tag2.select("li > a")
                for tag3 in tags3:
                    # print(tag3)

                    cinemaname = tag3.text.strip()  # 극장명
                    href = tag3['href']
                    midxs = href.split('=')
                    cinemacode = ''

                    if len(midxs) == 2:
                        cinemacode = midxs[1]

                    self.dicCinemas[cinemacode] = [region_cd, cinemaname, '']

                    if self.isPrnConsole:  # ################
                        cinema_count += 1
                        self.logger.info('+- {} : {}, {}'.format(cinema_count, cinemacode, cinemaname))
                    #
                #
            #
        #

    #
    #
    # -------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------
    # 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다. (dicRegions,dicCinemas)
    #
    def __crawl_mega_schedule(self):

        self.logger.info('')
        self.logger.info('### 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다. ###')

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
                fields = {"masterType": "brch",
                          "detailType": "area",
                          "brchNo": cinema_cd,
                          "firstAt": "N",
                          "brchNo1": cinema_cd,
                          "crtDe": play_de,
                          "playDe": play_de
                          }

                r = self.http.request('POST', url, fields)
                time.sleep(self.delayTime)

                data = r.data.decode('utf-8')

                json_obj = json.loads(data)
                # print(json_obj['megaMap']['movieFormList'])

                moviecode = ''
                cnt_room = 1

                for schl in json_obj['megaMap']['movieFormList']:

                    # print(schl)

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

                            if self.isPrnConsole:  # ################
                                self.logger.info('{} -> {} : {}'.format(old_moviecode, moviecode, moviename))
                        else:
                            self.dicMovies[moviecode] = ['', '', moviename]  # 영화데이터 정보
                            self.dicMoviesNm[moviename] = moviecode  # 영화이름을 코드체크

                    if self.isPrnConsole:  # ################
                        self.logger.info('{} : /{}/ {}, {}, {}, {}, {}, {}, {}, {}, {}, {}'.format(no_rooms, play_de, cinema_cd, moviecode, moviename, moviegubun, moviegbn, cnt_room, cinemaroom, str(rest_seat_cnt) + '/' + str(theab_seat_cnt), start_time, end_time))

                    dic_sch_rooms[no_rooms] = [moviecode, moviename, moviegubun, moviegbn, cnt_room, cinemaroom, rest_seat_cnt, theab_seat_cnt, start_time, end_time]  # 일단 다 펴와서..
                #

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
                    dic_sch_movies[km].append(dic_movies_room)
                # print(dic_sch_movies)
                dic_playdate[cinema_cd] = dic_sch_movies

            #
            self.dicTicketingData[play_de] = dic_playdate

        # print(self.dicTicketingData)

    #
    #
    # -----------------------------------------------------------------------------------------------------------

    def crawling(self):
        try:
            self.__crawl_mega_movie()  # 영화(https://www.megabox.co.kr/on/oh/oha/Movie/selectMovieList.do) 에서 영화데이터를 가지고 온다. (dicMovies)
            self.__crawl_mega_cinema()  # 영화관(https://www.megabox.co.kr/theater/list)에서 영화관데이터를 가지고 온다. (dicCinemas)
            self.__crawl_mega_schedule()  # 상영시간표 > 극장별 (https://www.megabox.co.kr/booking/timetable)에서 영화관에 스케줄데이터를 가지고 온다. (dicRegions,dicCinemas)
        except:
            self.logger.error('MEGA 크롤링 중 오류발생!')
            raise

    #

    def uplodding(self):
        try:
            self.logger.info('')
            self.logger.info('### MEGA 서버 전송 시작 ###')

            fields = {"movies": str(self.dicMovies),
                      "regions": str(self.dicRegions),
                      "cinemas": str(self.dicCinemas),
                      "ticketingdata": str(self.dicTicketingData)
                      }
            url = 'http://www.mtns7.co.kr/totalscore/upload_mega.php'

            r = self.http.request('POST', url, fields)
            data = r.data.decode('utf-8')

            print('[', data, ']')

            self.logger.info('### MEGA 서버 전송 종료 ###')
        except:
            self.logger.error('MEGA 전송 중 오류발생!')
            raise
    #


#


if __name__ == '__main__':

    maxDateRage = 12  # 최대 일수
    dateRage = maxDateRage  # 디폴트 크롤링 일수 (+12일)

    if len(sys.argv) == 2:
        try:
            dateRage = int(sys.argv[1])

            if dateRage < 0:  # 0 이면 당일
                dateRage = 0
            if dateRage > maxDateRage:
                dateRage = maxDateRage
        except ValueError:
            dateRage = maxDateRage

    logger = get_logger('mega')

    crawlMega = CrawlMega(True, logger, dateRage)  # Mega
    crawlMega.crawling()
    crawlMega.uplodding()

    clean_logger('mega')
#
