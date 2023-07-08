"""

"""
from Crawlling2.Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import sys
import traceback
import datetime
import sqlite3
import json
import time

import urllib3  # pip install urllib3
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from selenium import webdriver  # pip install selenium
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class ActCrlCgv(ActCrlSupper):

    
                        
    def __init__(self, date_range): # 생성자

        self.logger = get_logger('Cgv')   # 파이션 로그
        self.date_range = date_range      # 크롤링 할 날 수

        self.http = urllib3.PoolManager()

        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('Cgv')  # 한달전 로그파일을 삭제한다.
        super().__del__()
    # [def __del__(self): # 소멸자]


    # def crawling(self): =====================================================================================================================================

    def crawling(self):

        # =====================================================================================================================================================
        # 영화/무비차트(http://www.cgv.co.kr/movies/?ft=0) 애서 영화정보를 가지고온다.
        #
        def _1_crawl_cgv_moviechart():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('### 영화/무비차트(http://www.cgv.co.kr/movies/) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            options = webdriver.ChromeOptions()
            options.add_argument('--whitelisted-ips')        

            driver = webdriver.Chrome(executable_path='C:\\Crawlling2\\chromedriver.exe', options=options)  # 다운받은 파일을 압축푼 후 실행파일을 해당경로에 푼다.....
            driver.implicitly_wait(3)

            driver.get('http://www.cgv.co.kr/movies/')
            driver.implicitly_wait(3)

            driver.find_element(By.XPATH, '//*[@class="btn-more-fontbold"]').click()  # '더보기' 클릭
            driver.implicitly_wait(3)

            time.sleep(self.delayTime)  # 초 단위 지연...

            html = driver.page_source  # 패이지 소스를 읽어온다.....
            driver.quit()

            soup = BeautifulSoup(html, "html.parser")

            
            self.logger.info('------------------------------------------------------')
            self.logger.info('렝킹, [코드], 영화명(개봉일자), 점유율, 개봉여부, 등급')
            self.logger.info('------------------------------------------------------')

            for tag1 in soup.select("div.sect-movie-chart > ol > li"):  # 영화 리스트 순환단위  # print( tag1 )                

                moviecode = ''  # 영화코드
                grade = ''  # 관람등급
                rank = ''  # 순위
                moviename = ''  # 영화명
                percent = ''  # 예매율
                releasedate = ''  # 개봉일
                open_type = ''  # 개봉종류

                for tag2 in tag1.select("div.box-image > a"):  # 영화코드
                    # movecode = tag2.text.strip()
                    href = tag2['href']
                    hrefs = href.split('?')

                    if len(hrefs) == 2:
                        midxs = hrefs[1].split('=')

                        if len(midxs) == 2:
                            moviecode = midxs[1]
                    #
                #

                for tag2 in tag1.select("span.ico-grade"):  # 관람등급
                    grade = tag2.text.strip()
                    # print(grade)

                for tag2 in tag1.select("strong.rank"):  # 순위
                    rank = tag2.text.strip()
                    # print(rank)

                for tag2 in tag1.select("strong.title"):  # 영화명
                    moviename = tag2.text.strip()
                    # print(title)

                for tag2 in tag1.select("strong.percent > span"):  # 예매율
                    percent = tag2.text.strip()
                    # print(percent)

                for tag2 in tag1.select("span.txt-info"):  # 개봉일
                    for tag3 in tag2.select("span"):
                        open_type = tag3.text.strip()
                        tag3.extract()  # 자식태그를 제거한다.
                    # print(open_type)

                    releasedate = tag2.text.strip().replace('.', '')
                    # print(opened)

                    self.logger.info('{0} : [{1}] {2}({3}/{4}/{5}), {6}, {7}, {8}'.format(rank, moviecode, moviename, releasedate[:4], releasedate[4:6], releasedate[6:], percent, open_type, grade))
                #                    

                self.dicMovies[moviecode] = [moviename, releasedate]  # 영화데이터 정보
        # [def _1_crawl_cgv_moviechart():]

        # =====================================================================================================================================================
        # 영화/무비차트/상영예정작(http://www.cgv.co.kr/movies/pre-movies.aspx) 애서 영화정보를 가지고온다.
        #
        def _2_crawl_cgv_moviescheduled():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('### 영화/무비차트/상영예정작(http://www.cgv.co.kr/movies/pre-movies.aspx) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            self.logger.info('-------------------------------------')
            self.logger.info('no, 코드, 영화명(개봉일자)')
            self.logger.info('-------------------------------------')

            url = 'http://www.cgv.co.kr/movies/pre-movies.aspx'
            data = self.http.request( 'POST', url ).data.decode('utf-8')
            soup = BeautifulSoup(data, 'html.parser')

            mov_count = 0

            for tag1 in soup.select("div.sect-movie-chart > ol"):  # print( tag1 )                

                for tag2 in tag1.select("li"):  # print( tag2 )                    

                    moviecode = ''
                    moviename = ''
                    releasedate = ''

                    if len(tag2.select("div.box-contents > a")) == 0:
                        break

                    for tag3 in tag2.select("div.box-contents > a"):
                        href = tag3['href']
                        hrefs = href.split('=')

                        moviecode = hrefs[1]
                        moviename = tag3.text.strip()
                        # print( '{},{}'.format(moviecode, moviename) )

                        for tag3 in tag2.select("span.txt-info"):
                            # for lin in tag3.text.splitlines():
                            #     print( ' +{}+ '.format(lin.strip()) )

                            releasedate = tag3.text.splitlines()[2].strip()
                            if releasedate != '개봉예정':
                                releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                            else:
                                releasedate = ''

                                # print( ' +{}+ '.format( releasedate ) )

                        
                            mov_count += 1
                            self.logger.info(f'{mov_count} : {moviecode}, {moviename}({releasedate})')

                        self.dicMovies[moviecode] = [moviename, releasedate]  # 영화데이터 정보
                    #
                #
            #
        # [def _2_crawl_cgv_moviescheduled():]
        
        # =====================================================================================================================================================
        # 영화/무비파인더(http://www.cgv.co.kr/movies/finder.aspx) 에서 영화데이터를 가지고 온다.
        #
        def _3_crawl_cgv_moviefinder():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('### 영화/무비파인더(http://www.cgv.co.kr/movies/finder.aspx) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            mov_count = 0

            date1 = datetime.date.today()  # 오늘자 날짜객체
            date2 = date1 + datetime.timedelta(days=-365)  # 1년전

            # ###year_from = date2.year # 1년전 개봉작부터...
            year_from = 1960
            
            self.logger.info('-------------------------------------')
            self.logger.info('no: 코드, 영화명(개봉일자)')
            self.logger.info('-------------------------------------')

            # 1 ~ 페이지 에서 부터 영화정보 (코드+이름+개봉일) 를 가지고 온다...
            i = 0
            while True:
                # if i != 1:       # 일단 하나만 가지고 온다.
                #     continue

                if i == 0:  # 아무 옵션없이 첫 화면..
                    url = 'http://www.cgv.co.kr/movies/finder.aspx'
                else:
                    url = 'http://www.cgv.co.kr/movies/finder.aspx?s=true&kt=0&searchtxt=&genre=&indi=false&national=&grade=&sdate=' + str(year_from) + '&edate=2020&page=' + str(i)  # 무비파인더 에서 영화 리스트
                #

                url = 'http://www.cgv.co.kr/movies/finder.aspx'
                fields={ 's': 'true'
                       , 'kt': '0'
                       , 'searchtxt': ''
                       , 'genre': ''
                       , 'indi': 'false'
                       , 'national': ''
                       , 'grade': ''
                       , 'sdate': str(year_from)
                       , 'edate': '2020'
                       , 'page': str(i)
                       }
                data = self.http.request('POST', url, fields).data.decode('utf-8')
                soup = BeautifulSoup(data, 'html.parser')

                if i == 0:  # 첫페이지 (검색전)
                    for tag1 in soup.select("div.sect-movie-chart > ol"):  # print( tag1 )                        

                        for tag2 in tag1.select("li"):  # print( tag2 )                            

                            moviecode = ''
                            moviename = ''
                            releasedate = ''

                            if len(tag2.select("div.box-contents > a")) == 0:
                                break

                            for tag3 in tag2.select("div.box-contents > a"):
                                href = tag3['href']
                                hrefs = href.split('=')

                                moviecode = hrefs[1]
                                moviename = tag3.text.strip()
                                # print( '{},{}'.format(moviecode, moviename) )

                                for tag3 in tag2.select("span.txt-info"):
                                    # for lin in tag3.text.splitlines():
                                    #     print( ' +{}+ '.format(lin.strip()) )

                                    releasedate = tag3.text.splitlines()[2].strip()
                                    if releasedate != '개봉예정':
                                        releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                                    else:
                                        releasedate = ''

                                        # print( ' +{}+ '.format( releasedate ) )

                                
                                    mov_count += 1
                                    self.logger.info(f'{mov_count} : {moviecode}, {moviename}({releasedate[:4]}/{releasedate[4:6]}/{releasedate[6:]})')

                                self.dicMovies[moviecode] = [moviename, releasedate]  # 영화데이터 정보
                            #
                        #
                    #
                # if i == 0:  # 첫페이지 (검색전)

                if i > 0:  # 검색후 n 페이지
                    # 아래의 선택조건에 해당하는 영화가 총 0건 검색되었습니다. 를 체크
                    find_num = 0
                    for tag1 in soup.select("h3.sub > span > strong > i"):
                        find_num = tag1.text.strip()
                        # print( find_num )

                    if find_num == '0':  # 아래의 선택조건에 해당하는 영화가 총 0건 검색되었습니다.
                        break

                    if len(soup.select("div.sect-search-chart > ol")) == 0:
                        break

                    for tag1 in soup.select("div.sect-search-chart > ol"):  # print( tag1 )                        

                        for tag2 in tag1.select("li"):  # print( tag2 )                            

                            moviecode = ''
                            moviename = ''
                            releasedate = ''
                            # 페이지마다 아래 테그가 추가되므로 style이 없는 건만 파싱한다.# <li style="width:100%;text-align:center;padding:40px 0 40px 0;display:none">검색결과가 존재하지 않습니다.</li>

                            style = str(tag2.get('style'))
                            # print('style = ' + style)
                            if style == 'None':

                                for tag3 in tag2.select("div.box-contents > a"):
                                    href = tag3['href']
                                    hrefs = href.split('=')

                                    moviecode = hrefs[1]
                                    moviename = tag3.text.strip()
                                    # print( '{} {}'.format(moviecode, moviename) )

                                for tag3 in tag2.select("span.txt-info"):
                                    # for lin in tag3.text.splitlines():
                                    #     print( ' +{}+ '.format(lin.strip()) )
                                    releasedate = tag3.text.splitlines()[2].strip()
                                    if releasedate != '개봉예정':
                                        releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                                    else:
                                        releasedate = ''

                                        # print( ' +{}+ '.format( releasedate ) )

                                
                                    mov_count += 1
                                    self.logger.info(f'{mov_count} : {moviecode}, {moviename}({releasedate})')

                                self.dicMovies[moviecode] = [moviename, releasedate]  # 영화데이터 정보
                            #
                        #
                    #
                #
                i += 1
            #
        # [def _3_crawl_cgv_moviefinder():]

        # =====================================================================================================================================================
        # 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/) 극장정보를 가지고 온다.
        #
        def _4_crawl_cgv_theaters():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('## 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            theater_count = 0

            url = 'http://www.cgv.co.kr/reserve/show-times/'
            data = self.http.request('GET', url).data.decode('utf-8')
            
            self.logger.info('-------------------------------------')
            self.logger.info('no : [코드] 지역명, 극장명')
            self.logger.info('-------------------------------------')

            data_lines = data.splitlines()

            for data_line in data_lines:

                jsondata = 'theaterJsonData = '  # 지역별 극장전체 정보를 가지고 있는 json 변수
                len_jsondata = len(jsondata)
                find_jsondata = data_line.find(jsondata)

                if find_jsondata != -1:  # 발견하면...

                    json_txt = data_line[find_jsondata + len_jsondata:].split(';')  # print( json_txt[0] )

                    json_obj = json.loads(str(json_txt[0]))  # text json 을 json 객체로 변환
                    for json_theater in json_obj:

                        # print( json_theater['DisplayOrder'] ) # 출력 순서
                        # print( json_theater['RegionCode'] ) # 지역코드
                        # print( json_theater['RegionName'] ) # 지역
                        regioncode = json_theater['RegionCode']
                        regionname = json_theater['RegionName']

                        regioncodes = regioncode.split(',')
                        regionnames = regionname.split('/')
                        # print(str(len(regionnames)))

                        # 복합지역인 경우는 개별 분리한다.
                        i = 0
                        for regioncode in regioncodes:
                            self.dicRegions[regioncode] = regionnames[i];  # 지역코드 정보 추가 (지역코드+지역명)
                            i += 1

                        for theater in json_theater['AreaTheaterDetailList']:
                            # print(theater)
                            regioncode = theater['RegionCode']  # 극장지역코드
                            theatercode = theater['TheaterCode']  # 극장코드
                            theatername = theater['TheaterName']  # 극장명
                            
                            theater_count += 1
                            self.logger.info(f'{theater_count} : [{theatercode}] {self.dicRegions[regioncode]}, {theatername}')

                            self.dicTheaters[theatercode] = [regioncode, self.dicRegions[regioncode], theatername]  # 극장코드 정보 추가 (지역코드+지역명+극장명)
                        #
                    #
                #
            
                region_count = 0

                self.logger.info('-------------------------------------')
                self.logger.info('no, [코드] 지역명')
                self.logger.info('-------------------------------------')

                for region in self.dicRegions:

                    region_count += 1
                    self.logger.info('{} : [{}] {}'.format(region_count, region, self.dicRegions[region]))
                #
            #
        # [def _4_crawl_cgv_theaters():]

        # =====================================================================================================================================================
        # 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/)의 프래임에서 상영정보를 가지고 온다.
        #
        def _5_crawl_cgv_showtimes():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info('## 예매/상영시간표의 프레임 (http://www.cgv.co.kr/reserve/show-times/iframeTheater.aspx?areacode=&theatercode=&date=) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
            chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
            driver = webdriver.Chrome(options=chrome_options)

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
                days.append('{:04d}{:02d}{:02d}'.format(date12.year, date2.month, date2.day))  # 오늘+11의 날짜
            if self.dateRage >= 12:
                days.append('{:04d}{:02d}{:02d}'.format(date13.year, date3.month, date3.day))  # 오늘+12의 날짜

            # 1 ~ 13 일간 자료 가져오기
            for today in days:
                #if today != '20200224':
                #    continue  # 디버깅용

                # if  today!='{:04d}{:02d}{:02d}'.format( date1.year, date1.month, date1.day ):  # 일단 오늘 자료만 가지고 온다.
                #    continue  # 디버깅용

                dicTicketingData = {}  # 티켓팅 정보

                for theaterkey in self.dicTheaters.keys():  # 극장을 하나씩 순회한다.

                    #if theaterkey != '0056' and theaterkey != '0001':  # 일단 특정극장(서울, CGV강남)
                    #    continue  # 디버깅용
                    
                    self.logger.info(f' {today[:4]}/{today[4:6]}/{today[6:]} 일 :  {self.dicTheaters[theaterkey][1]}, {self.dicTheaters[theaterkey][2]} ({theaterkey})')

                    url = 'http://www.cgv.co.kr/reserve/show-times/?areacode=' + self.dicTheaters[theaterkey][0] + '&theatercode=' + theaterkey + '&date=' + today + ''
                    driver.get(url)
                    driver.switch_to.frame('ifrm_movie_time_table')

                    try:
                        element = WebDriverWait(driver, timeout=1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sect-showtimes']")))

                        dicTicketMovies = {}  #

                        for tag1 in element.find_elements(By.TAG_NAME, "ul > li > div.col-times"):
                            moviecode = ''
                            moviename = ''
                            movieplaying = ''
                            moviegenre = ''
                            movieruntime = ''
                            moviereleasedate = ''

                            for tag2 in tag1.find_elements(By.TAG_NAME, "div.info-movie > a"):
                                href = tag2.get_attribute('href')
                                hrefs = href.split('=')

                                moviecode = hrefs[1]

                                tag2.find_elements(By.TAG_NAME, "strong")
                                moviename = tag2.text.strip()

                            moviegrade = ''
                            for tag2 in tag1.find_elements(By.TAG_NAME, "div.info-movie > span.ico-grade"):
                                moviegrade = tag2.text.strip()

                            for tag2 in tag1.find_elements(By.TAG_NAME, "div.info-movie > span.round > em"):
                                movieplaying = tag2.text.strip()

                            j = 0
                            for tag2 in tag1.find_elements(By.TAG_NAME, "div.info-movie > i"):
                                j += 1
                                if j == 1: moviegenre = tag2.text.strip().replace('\xa0', ' ').replace("\r\n", "")
                                if j == 2: movieruntime = tag2.text.strip().replace('\xa0', ' ').replace("\r\n", "")
                                if j == 3:
                                    moviereleasedate = tag2.text.strip().replace('\xa0', ' ').replace("\r\n", "")
                                    moviereleasedate = moviereleasedate[0:4] + moviereleasedate[5:7] + moviereleasedate[8:10]
                                    # print( str( j ) + ' ] ' + tag2.text.strip().replace( '\xa0', ' ' ).replace( "\r\n", "" ) )

                            dicTicketRooms = {}  #

                            j = 0
                            for tag2 in tag1.find_elements(By.TAG_NAME, "div.type-hall"):

                                j = j + 1

                                k = 0
                                for tag3 in tag2.find_elements(By.TAG_NAME, "div.info-hall > ul > li"):

                                    k += 1
                                    if k == 1:
                                        filmtype = tag3.text.strip().replace("\r\n", "")
                                    if k == 2:
                                        roomfloor = tag3.text.strip().replace("\r\n", "")
                                    if k == 3:
                                        totalseat = tag3.text.strip().replace("\r\n", "").split()
                                        totalseat = totalseat[1]
                                        # print( str(j) + ' / ' + tag3.text.strip().replace("\r\n", "") )
                                #

                                dicTicketTimes = {}  #

                                k = 0
                                for tag3 in tag2.find_elements(By.TAG_NAME, "div.info-timetable > ul > li"):

                                    k += 1

                                    playtime = ''
                                    playinfo = ''
                                    playetc = ''

                                    if len(tag3.find_elements(By.TAG_NAME, "a")) > 0:  # print( '일반' )

                                        for tag4 in tag3.find_elements(By.TAG_NAME, "a > em"):
                                            playtime = tag4.text  # print( tag4.text )                                            

                                        for tag4 in tag3.find_elements(By.TAG_NAME, "a > span"):
                                            playinfo = tag4.text  # print( tag4.text )                                            

                                            ''' 
                                            #반드시 저녁에 확인 할것,,,
                                            early = tag4.get_property("early")
                                            midnight = tag4.get_attribute('midnight')
                                            for v in tag4.attrs.values():
                                                if v[0] == 'early':
                                                    playetc = '조조'
                                                    # print( "조조" )
                                                if v[0] == 'midnight':
                                                    playetc = '심야'
                                                    # print( "심야" )
                                            '''
                                        #
                                    #

                                    else:  # print( '마감' )

                                        for tag4 in tag3.find_elements(By.TAG_NAME, "em"):
                                            playtime = tag4.text  # print( tag4.text )                                            

                                        for tag4 in tag3.find_elements(By.TAG_NAME, "span"):
                                            playinfo = tag4.text  # print( tag4.text )                                            
                                    #
                                    dicTicketTimes[k] = [playtime, playinfo, playetc]
                                #  self.logger.info(dicTicketTimes)
                                dicTicketRooms[j] = [filmtype, roomfloor, totalseat, dicTicketTimes]
                            #

                            dicTicketMovies[moviecode] = [moviename, moviegrade, movieplaying, moviegenre, movieruntime, moviereleasedate, dicTicketRooms]
                        #     print( dicTicketMovies )

                        dicTicketingData[theaterkey] = dicTicketMovies
                        #    self.logger.info(dicTicketingData)

                    except TimeoutException:
                        print("해당 페이지에 cMain 을 ID 로 가진 태그가 존재하지 않거나, 해당 페이지가 10초 안에 열리지 않았습니다.")
                # for theaterkey in self.dicTheaters.keys(): # 극장을 하나씩 순회한다.

                self.dicTicketingDays[today] = dicTicketingData
            # for today in days: # 1 ~ 13 일간 자료 가져오기

            driver.quit()
        # [def _5_crawl_cgv_showtimes():]

 
        try:

            _1_crawl_cgv_moviechart()     # 영화/무비차트(http://www.cgv.co.kr/movies/?ft=0) 애서 영화정보를 가지고온다.
            _2_crawl_cgv_moviescheduled() # 영화/무비차트/상영예정작(http://www.cgv.co.kr/movies/pre-movies.aspx) 애서 영화정보를 가지고온다.
            _3_crawl_cgv_moviefinder()    # 영화/무비파인더(http://www.cgv.co.kr/movies/finder.aspx) 에서 영화데이터를 가지고 온다. - 화면 서비스가 정지 될 수 있어서.. 그 경우 위의 함수를 호출한다.
            _4_crawl_cgv_theaters()       # 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/) 극장정보를 가지고 온다.
            _5_crawl_cgv_showtimes()      # 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/)의 프래임에서 상영정보를 가지고 온다.
        except Exception as e:

            self.logger.error('Cgv 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):]

    # def uploading(self): ====================================================================================================================================
    
    def uploading(self):
        
        print("Uploading Cgv data...")
    # [def uploading(self):]s
# [class ActCrlCgv(ActCrlSupper):]

if __name__ == '__main__':

    maxDateRage = 12  # 최대 일수

    if len(sys.argv) == 2:
        try:
            dateRange = min(max(int(sys.argv[1]), 0), maxDateRage)
        except ValueError:
            dateRange = maxDateRage
    else:
        dateRange = maxDateRage

    actCrlCgv = ActCrlCgv(date_range = dateRange)  # Cgv
    actCrlCgv.crawling()
    actCrlCgv.uploading()
    
# [if __name__ == '__main__':]    
