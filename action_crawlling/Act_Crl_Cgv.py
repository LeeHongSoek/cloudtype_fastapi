from Act__Supper import ActCrlSupper
from Act__Logger import get_logger, clear_logger

import requests
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


    def crawling(self):

        # =====================================================================================================================================================
        # 1. 영화/무비차트(http://www.cgv.co.kr/movies/?ft=0) 애서 영화정보를 가지고온다.
        #
        def _1_crawl_cgv_moviechart(chm_driver):

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 1. ### 영화/무비차트(http://www.cgv.co.kr/movies/) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            chm_driver.get('http://www.cgv.co.kr/movies/')
            chm_driver.implicitly_wait(3)

            chm_driver.find_element(By.XPATH, '//*[@class="btn-more-fontbold"]').click()  # '더보기' 클릭
            chm_driver.implicitly_wait(3)  # 초 단위 지연...

            html = chm_driver.page_source  # 패이지 소스를 읽어온다.....
            chm_driver.quit()

            soup = BeautifulSoup(html, "html.parser")
            
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('렝킹, [코드], 영화명(개봉일자), 점유율, 개봉여부, 등급')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

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

                    self.logger.info(f'{rank} : [{moviecode}] {moviename}({releasedate[:4]}/{releasedate[4:6]}/{releasedate[6:]}), {percent}, {open_type}, {grade}')

                    query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_movie'}']").text.strip()
                    parameters = ( moviecode, moviename, releasedate)
                    self.sql_cursor.execute(query, parameters)
            # [for tag1 in soup.select("div.sect-movie-chart > ol > li"):  # 영화 리스트 순환단위]

            self.sql_conn.commit()
        # [def _1_crawl_cgv_moviechart():]

        # =====================================================================================================================================================
        # 2. 영화/무비차트/상영예정작(http://www.cgv.co.kr/movies/pre-movies.aspx) 애서 영화정보를 가지고온다.
        #
        def _2_crawl_cgv_moviescheduled():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 2. ### 영화/무비차트/상영예정작(http://www.cgv.co.kr/movies/pre-movies.aspx) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            url = 'http://www.cgv.co.kr/movies/pre-movies.aspx'
            r = requests.post(url)
            time.sleep(self.delayTime)

            soup = BeautifulSoup(r.text, 'html.parser') # print(data)

            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('no, 코드, 영화명(개봉일자)   ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            mov_count = 0
            for tagOL in soup.select("div.sect-movie-chart > ol"):  # print( tag1 )                

                for tagLI in tagOL.select("li"):  # print( tag2 )                    

                    moviecode = ''
                    moviename = ''
                    releasedate = ''

                    if len(tagLI.select("div.box-contents > a")) == 0:
                        break

                    for tagA in tagLI.select("div.box-contents > a"):

                        href = tagA['href']
                        hrefs = href.split('=')

                        moviecode = hrefs[1]
                        moviename = tagA.text.strip()
                        # print( '{},{}'.format(moviecode, moviename) )

                        for tagA in tagLI.select("span.txt-info"):
                            # for lin in tag3.text.splitlines():
                            #     print( ' +{}+ '.format(lin.strip()) )

                            releasedate = tagA.text.splitlines()[2].strip()
                            if releasedate != '개봉예정':
                                releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                            else:
                                releasedate = ''
                                # print( ' +{}+ '.format( releasedate ) )
                        
                            mov_count += 1
                            self.logger.info(f'{mov_count} : {moviecode}, {moviename}({releasedate})')

                            query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_movie'}']").text.strip()
                            parameters = ( moviecode, moviename, releasedate)
                            self.sql_cursor.execute(query, parameters)
                        # [for tagA in tagLI.select("span.txt-info"):]
                    # [for tagA in tagLI.select("div.box-contents > a"):]
                # [for tagLI in tagOL.select("li"):]
            # [for tagOL in soup.select("div.sect-movie-chart > ol"):]

            self.sql_conn.commit()
        # [def _2_crawl_cgv_moviescheduled():]
        
        # =====================================================================================================================================================
        # 3. 영화/무비파인더(http://www.cgv.co.kr/movies/finder.aspx) 에서 영화데이터를 가지고 온다.
        #
        def _3_crawl_cgv_moviefinder():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 3. ### 영화/무비파인더(http://www.cgv.co.kr/movies/finder.aspx) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            date1 = datetime.date.today()  # 오늘자 날짜객체
            date2 = date1 + datetime.timedelta(days=-365)  # 1년전

            # ###year_from = date2.year # 1년전 개봉작부터...
            year_from = 1960
            
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('no: 코드, 영화명(개봉일자)')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            # 1 ~ 페이지 에서 부터 영화정보 (코드+이름+개봉일) 를 가지고 온다...
            mov_count = 0
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
                r = requests.post(url, data=fields)
                time.sleep(self.delayTime)

                soup = BeautifulSoup(r.text, 'html.parser')

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

                                query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_movie'}']").text.strip()
                                parameters = ( moviecode, moviename, releasedate)
                                self.sql_cursor.execute(query, parameters)
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

                                query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_movie'}']").text.strip()
                                parameters = ( moviecode, moviename, releasedate)
                                self.sql_cursor.execute(query, parameters)
                            #
                        #
                    #
                #
                i += 1
            #

            self.sql_conn.commit()
        # [def _3_crawl_cgv_moviefinder():]

        # =====================================================================================================================================================
        # 4. 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/) 극장정보를 가지고 온다.
        #
        def _4_crawl_cgv_theaters():

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 4. ## 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            
            r = requests.post('http://www.cgv.co.kr/reserve/show-times/')            
            time.sleep(self.delayTime)

            data_lines = r.text.splitlines()

            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('no : [코드] 지역명, 극장명')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            dicRegions = {}
            theater_count = 0
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
                            
                            dicRegions[regioncode] = regionnames[i];  # 지역코드 정보 추가 (지역코드+지역명)

                            query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_region'}']").text.strip()
                            parameters = ( regioncode, regionnames[i] )
                            self.sql_cursor.execute(query, parameters)
                            i += 1
                        # [for regioncode in regioncodes:]    

                        for theater in json_theater['AreaTheaterDetailList']:

                            # print(theater)
                            regioncode = theater['RegionCode']  # 극장지역코드
                            theatercode = theater['TheaterCode']  # 극장코드
                            theatername = theater['TheaterName']  # 극장명
                            
                            theater_count += 1
                            self.logger.info(f'{theater_count} : [{theatercode}] {dicRegions[regioncode]}, {theatername}')

                            query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_theater'}']").text.strip()
                            parameters = ( theatercode, regioncode, dicRegions[regioncode], theatername )
                            self.sql_cursor.execute(query, parameters)
                        # [for theater in json_theater['AreaTheaterDetailList']:]
                    # [for json_theater in json_obj:]
                #
            
                region_count = 0

                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                self.logger.info('no, [코드] 지역명')
                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                for region in dicRegions:

                    region_count += 1
                    self.logger.info(f'{region_count} : [{region}] {dicRegions[region]}')
                #
            # [if find_jsondata != -1:  # 발견하면...]

            self.sql_conn.commit()
        # [def _4_crawl_cgv_theaters():]

        # =====================================================================================================================================================
        # 5. 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/)의 프래임에서 상영정보를 가지고 온다.
        #
        def _5_crawl_cgv_showtimes(chm_driver):

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 5. ## 예매/상영시간표의 프레임 (http://www.cgv.co.kr/reserve/show-times/iframeTheater.aspx?areacode=&theatercode=&date=) ###  ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __5_get_date_range(date_range):
                days = []

                date1 = datetime.date.today()  # 오늘자 날짜객체
                days.append('{:04d}{:02d}{:02d}'.format(date1.year, date1.month, date1.day))  # 오늘의 날짜

                for i in range(1, date_range + 1):
                    date = date1 + datetime.timedelta(days=i)  # 오늘부터 i일 후의 날짜
                    days.append('{:04d}{:02d}{:02d}'.format(date.year, date.month, date.day))  # 오늘부터 i일 후의 날짜를 추가

                return days
            # [def __5_get_date_range(date_range):]            

            for itday in __5_get_date_range(dateRange): # 1 ~ 13 일간 자료 가져오기
                #if today != '20200224':
                #    continue  # 디버깅용

                # if  today!='{:04d}{:02d}{:02d}'.format( date1.year, date1.month, date1.day ):  # 일단 오늘 자료만 가지고 온다.
                #    continue  # 디버깅용

                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                self.logger.info(' 상영일 :  지역, 극장')
                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                dicTicketingData = {}  # 티켓팅 정보

                self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'SELECT_cgv_theater'}']").text.strip())
                self.sql_cursor.row_factory = sqlite3.Row                
                for row in self.sql_cursor.fetchall():  # 극장을 하나씩 순회한다.

                    theatercode = row['theatercode']
                    regioncode = row['regioncode']
                    regionname = row['regionname']
                    theatername = row['theatername']

                    #if theaterkey != '0056' and theaterkey != '0001':  # 일단 특정극장(서울, CGV강남)
                    #    continue  # 디버깅용
                    
                    self.logger.info(f' {itday[:4]}/{itday[4:6]}/{itday[6:]} 일 :  {regionname}, ({theatercode}){theatername} ')

                    url = 'http://www.cgv.co.kr/reserve/show-times/?areacode=' + regioncode + '&theatercode=' + theatercode + '&date=' + itday + ''
                    chrome_driver.get(url)
                    chrome_driver.switch_to.frame('ifrm_movie_time_table')

                    try:
                        element = WebDriverWait(chrome_driver, timeout=1).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sect-showtimes']")))

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
                            # [for tag2 in tag1.find_elements(By.TAG_NAME, "div.info-movie > a"):]

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
                            # [for tag2 in tag1.find_elements(By.TAG_NAME, "div.info-movie > i"):]

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
                                # [for tag3 in tag2.find_elements(By.TAG_NAME, "div.info-hall > ul > li"):]

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

                                            #반드시 저녁에 확인 할것,,,
                                            early = tag4.get_property("early")
                                            midnight = tag4.get_attribute('midnight')
                                            for v in tag4.attrs.values():
                                                if v[0] == 'early':
                                                    playetc = '조조' # print( "조조" )
                                                if v[0] == 'midnight':
                                                    playetc = '심야' # print( "심야" )
                                        # [for tag4 in tag3.find_elements(By.TAG_NAME, "a > span"):]
                                    else:  # print( '마감' )

                                        for tag4 in tag3.find_elements(By.TAG_NAME, "em"):
                                            playtime = tag4.text  # print( tag4.text )                                            

                                        for tag4 in tag3.find_elements(By.TAG_NAME, "span"):
                                            playinfo = tag4.text  # print( tag4.text )                                            
                                    # [if len(tag3.find_elements(By.TAG_NAME, "a")) > 0:]

                                    dicTicketTimes[k] = [playtime, playinfo, playetc]
                                #  self.logger.info(dicTicketTimes)

                                dicTicketRooms[j] = [filmtype, roomfloor, totalseat, dicTicketTimes]
                            # [for tag2 in tag1.find_elements(By.TAG_NAME, "div.type-hall"):]

                            dicTicketMovies[moviecode] = [moviename, moviegrade, movieplaying, moviegenre, movieruntime, moviereleasedate, dicTicketRooms]
                        # [for tag1 in element.find_elements(By.TAG_NAME, "ul > li > div.col-times"):]

                        dicTicketingData[theatercode] = dicTicketMovies
                        #    self.logger.info(dicTicketingData)

                    except TimeoutException as e:    
                        self.sql_conn.rollback()

                        self.logger.error('-----------------------------------------------------------------------')
                        self.logger.error('해당 페이지에 cMain 을 ID 로 가진 태그가 존재하지 않거나, 해당 페이지가 10초 안에 열리지 않았습니다.')
                        self.logger.error(f'오류 내용! {e}')
                        self.logger.error(f'{traceback.print_exc()}')
                        self.logger.error('-----------------------------------------------------------------------')

                        # 드라이버 재 실행 !!
                        chm_driver.quit()

                        chm_driver = webdriver.Chrome(options=chrome_options)
                    # [try]
                # [for row in self.sql_cursor.fetchall():  # 극장을 하나씩 순회한다.]

                for theatercode, v1 in dicTicketingData.items():
                    for moviecode, v2 in v1.items(): # dicTicketMovies.items() # moviename, moviegrade, movieplaying, moviegenre, movieruntime, moviereleasedate, dicTicketRooms
                        for j, v3 in v2[6].items(): # dicTicketRooms.items() # filmtype, roomfloor, totalseat, dicTicketTimes
                            for k, v4 in v3[4].items(): # dicTicketTimes.items() # playtime, playinfo, playetc
                                query = self.sqlxmp.find(f"query[@id='{'INSERT_cgv_ticket'}']").text.strip()
                                parameters = ( itday, theatercode, moviecode, filmtype, roomfloor, totalseat, playtime, playinfo, playetc )
                                self.sql_cursor.execute(query, parameters)
                # [for theatercode, v1 in dicTicketingData.items():]
            # [for itday in __5_get_date_range(dateRange): # 1 ~ 13 일간 자료 가져오기]

            chm_driver.quit()
            self.sql_conn.commit()
        # [def _5_crawl_cgv_showtimes():]

 
        try:

            chrome_options = webdriver.ChromeOptions()
            #chrome_options.add_argument('--headless')  # Headless 모드 설정
            #chrome_options.add_argument("--start-maximized")  # 창을 최대화로 시작
            chrome_options.add_argument("--blink-settings=imagesEnabled=false") #  이미지가 로드되지 않으므로 페이지 로딩 속도가 향상
            chrome_options.add_argument('--excludeSwitches=enable-automation')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-minimized')  # 최소화된 상태로 창을 시작
            chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
            chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_driver = webdriver.Chrome(options=chrome_options)            

            #_1_crawl_cgv_moviechart(chrome_driver)  # 1. 영화/무비차트(http://www.cgv.co.kr/movies/?ft=0) 애서 영화정보를 가지고온다.
            #_2_crawl_cgv_moviescheduled()           # 2. 영화/무비차트/상영예정작(http://www.cgv.co.kr/movies/pre-movies.aspx) 애서 영화정보를 가지고온다.
            #_3_crawl_cgv_moviefinder()              # 3. 영화/무비파인더(http://www.cgv.co.kr/movies/finder.aspx) 에서 영화데이터를 가지고 온다. - 화면 서비스가 정지 될 수 있어서.. 그 경우 위의 함수를 호출한다.
            _4_crawl_cgv_theaters()                 # 4. 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/) 극장정보를 가지고 온다.
            _5_crawl_cgv_showtimes(chrome_driver)   # 5. 예매/상영시간표(http://www.cgv.co.kr/reserve/show-times/)의 프래임에서 상영정보를 가지고 온다.
        except Exception as e:

            self.logger.error('Cgv 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):]

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
