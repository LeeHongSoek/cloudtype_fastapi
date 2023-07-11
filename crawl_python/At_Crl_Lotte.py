from At__Supper import ActCrlSupper
from At__Logger import get_logger, clear_logger

import sys
import traceback
import sqlite3
import platform
import time
import json

from selenium import webdriver # pip install selenium
from selenium.webdriver.common.by import By

from jsonpath_rw import parse  # pip install jsonpath-rw  https://pypi.python.org/pypi/jsonpath-rw
from browsermobproxy import Server  # pip install browsermob-proxy
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from urllib.parse import parse_qs, urlparse


class ActCrlLotte(ActCrlSupper):

    def __init__(self, date_range): # 생성자

        self.logger = get_logger('Lotte')   # 파이션 로그
        self.date_range = date_range        # 크롤링 할 날 수

        super().__init__(type(self).__name__)
    # [def __init__(self, date_range): # 생성자]

    def __del__(self): # 소멸자

        clear_logger('Lotte')  # 한달전 로그파일을 삭제한다.
        super().__del__()
    # [def __del__(self): # 소멸자]


    def crawling(self):
        
        # =====================================================================================================================================================
        #  1. 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. 
        #
        def _1_crawlLotte_boxoffice(chm_driver):

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 1. 영화 / 현재상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1),                               ')
            self.logger.info('    영화 / 상영예정작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=5) 에서 영화데이터를 가지고 온다. ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('코드, 영화명, 장르, 예매, 개봉일, 관람등급                                     ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'DELETE_lotte_movie'}']").text.strip())            

            arrUrl = ["https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1", "https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=5"]  # 상영영화와 상영예정영화
            for url in arrUrl:
                chm_driver.get(url)  # 웹사이트로 이동
                chm_driver.implicitly_wait(1)  # 1초 대기
    
                for entry in proxy.har['log']['entries']:  # 각 캡처된 요청의 세부 정보 출력
                    request = entry['request']
                    response = entry['response']

                    if response['content']['size'] == 0:
                        continue

                    if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx":                        

                        # JSON 파싱
                        json_obj = json.loads(response['content']['text'])
                        
                        for match in parse('Movies.Items[*]').find(json_obj):

                            representationmoviecode = str(match.value['RepresentationMovieCode'])
                            movienamekr = str(match.value['MovieNameKR']).strip()
                            moviegenrename = str(match.value['MovieGenreName'])
                            bookingyn = str(match.value['BookingYN'])
                            releasedate = str(match.value['ReleaseDate'])
                            releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                            viewgradenameus = str(match.value['ViewGradeNameUS'])

                            if movienamekr == '' or movienamekr == 'AD': continue

                            self.logger.info(f'{representationmoviecode},{movienamekr},{moviegenrename},{bookingyn},{releasedate},{viewgradenameus}')

                            query = self.sqlxmp.find(f"query[@id='{'INSERT_lotte_movie'}']").text.strip()                            
                            parameters = (representationmoviecode, movienamekr, moviegenrename, bookingyn, releasedate, viewgradenameus)
                            self.sql_cursor.execute(query, parameters)
                        # [for match in parse('Movies.Items[*]').find(json_obj):]

                        self.sql_conn.commit()
                    # [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx": ]
                # [for entry in proxy.har['log']['entries']:  # 각 캡처된 요청의 세부 정보 출력 ]

                proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 복수 실행을 위해 캡처된 요청 초기화

            # [for url in arrUrl: # 상영영화와 상영예정영화 ]
        # [def _crawlLotte_1_boxoffice(chm_driver):]

        # =====================================================================================================================================================
        #  2. 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. 
        #
        def _2_crawlLotte_cinema(chm_driver):

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 2. 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __2_parse_links(tag1, arrUrl):

                tag_lst = ''
                tags2 = tag1.select('li > a:not([href="#"])')
                for tag2 in tags2:  # print(tag2)
                    tag_lst += tag2.prettify()

                a_tags = BeautifulSoup(tag_lst, 'html.parser').find_all('a')

                pas_links = []

                for a_tag in a_tags:
                    link = a_tag['href']
                    parsed_url = urlparse(link)
                    params = parse_qs(parsed_url.query)

                    url = link.split('?')[0]
                    query_params = {ikey: ivalue[0] for ikey, ivalue in params.items()}
                    text = a_tag.text.replace("\n", "").strip()

                    if  url in arrUrl: # 스폐셜 영화관과 일반영화관 url만 파싱한다.
                        pas_links.append({'url': url, 'query_params': query_params, 'text': text, 'link': link})
                        # print("URL:", parsed_link['url'],", Query Params:", parsed_link['query_params'],", Text:", parsed_link['text'], link:", parsed_link['link'])

                return pas_links
            # [def __2_parse_links(tag1, arrUrl):]

            chm_driver.get('https://www.lottecinema.co.kr/NLCHS')
            chm_driver.implicitly_wait(1)

            html = chm_driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
            soup = BeautifulSoup(html, "html.parser")

            if tag1 := soup.select_one("#nav > ul > li:nth-child(3) > div > ul"):  # 메인 메뉴의 '영화관' 하위 메뉴 탐색                

                # 스폐셜 영화관과 일반영화관 url만 파싱한다.
                arrUrl = ['https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema','https://www.lottecinema.co.kr/NLCHS/Cinema/Detail']
                parsed_links = __2_parse_links(tag1, arrUrl)  # <a> 태그 분해

                self.sql_cursor.execute(self.sqlxmp.find(f"query[@id='{'DELETE_lotte_cinema'}']").text.strip())            

                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                self.logger.info('코드, 스페셜관, 극장명, 링크, 성공여부')
                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                for parsed_link in parsed_links:  # print(parsed_link)                    
                    
                    if parsed_link['url'] == arrUrl[0]:  # 극장(스페셜관)정보저장
                        spacialyn = 'Y'
                        cinemacode = parsed_link['query_params']['screendivcd']

                    if parsed_link['url'] == arrUrl[1]:  # 극장(일반)정보저장                        
                        spacialyn = 'N'
                        cinemacode = parsed_link['query_params']['cinemaID']

                    self.logger.info(f"{cinemacode}, {spacialyn}, {parsed_link['text']}, {parsed_link['link']}, '_'")

                    query = self.sqlxmp.find(f"query[@id='{'INSERT_INTO_lotte_cinema'}']").text.strip()                            
                    parameters = (cinemacode, spacialyn, parsed_link['text'], parsed_link['link'])
                    self.sql_cursor.execute(query, parameters)
                # [for parsed_link in parsed_links:]

                self.sql_conn.commit()
            
            # [if tag1 := soup.select_one("#nav > ul > li:nth-child(3) > div > ul"):  # 메인 메뉴의 '영화관' 하위 메뉴 탐색]    
        # [def _crawlLotte_2_cinema(chm_driver):]

        # =====================================================================================================================================================
        # 3. 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다.
        #
        def _3_crawlLotte_ticketing(chm_driver):

            self.logger.info('')
            self.logger.info('===============================================================================================================================')
            self.logger.info(' 3. 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __3_daily_ticketingdata(cinemacode, link):
                
                def ___3_get_ability_day(chm_driver, date_range): # 유효한 날짜들의 인덱스만 배열로 구성한다.                    

                    buttons = chm_driver.find_elements(By.XPATH, '//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div')  # 전체 상영일 버튼들..

                    arr_ability_day = []
                    for i in range(1, (len(buttons) + 1)):  # 전체 상영일 순환
                        day_a_tag = chm_driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a')  # 일자 선택 버튼

                        if i <= (date_range+1):
                            if 'disabled' not in day_a_tag.get_attribute('class'):
                                arr_ability_day.append(i)  # 무효한 상영일

                    return arr_ability_day
                # [def ___3_get_ability_day(chm_driver, date_range):]

                chm_driver.get(link)   # 웹사이트로 이동
                chm_driver.implicitly_wait(1)  # 1초 대기

                theather_nm = chm_driver.find_elements(By.XPATH,  '//h3[@class="tit"]')[0].text  # 타이틀의 극장명을 읽는다.

                button = chm_driver.find_elements(By.XPATH, '//*[text()="확인"]')  # 난데없는 팝업창이 나오면 '확인'을 누를다...
                if len(button) > 0:  # 버튼이 발견되면...
                    element = button[0]
                    element.click()
                    time.sleep(1)
                # [if soup.select_one("ul > li"):]

                arr_ablity_days = ___3_get_ability_day(chm_driver, self.date_range) # 유효한 날짜들의 인덱스만 배열로 구성한다.                    
                for ablityDay in arr_ablity_days:  # 유효한 상영일만 순환

                    chm_driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{ablityDay}]/li/a').click()  # 상영일 누르기..!!!
                    chm_driver.implicitly_wait(0.5)  # 1초 대기

                    for entry in proxy.har['log']['entries']:  # 캡처된 각 요청의 세부 정보 출력
                        request = entry['request']
                        response = entry['response']

                        if response['content']['size'] == 0:
                            continue

                        if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":

                            json_obj = json.loads(response['content']['text'])  # JSON 파싱

                            jsonpath_expr = parse('PlaySeqsHeader.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info(' 영화코드,    영화명,    더빙/자막')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                                moviecode_old = ''
                                for match1 in jsonpath_expr[0].value:
                                    moviecode = match1['MovieCode']  # 영화코드

                                    if moviecode_old != moviecode:  # 같은 영화정보가(영화코드가) 여러번 들어오는걸 거른다.
                                        moviename = match1['MovieNameKR']  # 영화명 ex) 엘리멘탈
                                        filmnamekr = match1['FilmNameKR']  # 필름종류  ex) 2D
                                        gubun = match1['TranslationDivisionNameKR']  # 더빙/자막

                                        query = self.root.find(f"query[@id='{'SELECT_count_lotte_movie_moviecode'}']").text.strip()                            
                                        parameters = (moviecode,)
                                        self.sql_cursor.execute(query, parameters)
                                        result = self.sql_cursor.fetchone() # 첫 번째 결과 행 가져오기

                                        if result['cnt'] > 0:
                                            query = self.root.find(f"query[@id='{'UPDATE_lotte_movie_filmname_gubun'}']").text.strip()                            
                                            parameters = (filmnamekr, gubun, moviecode)
                                            self.sql_cursor.execute(query, parameters)
                                        else:
                                            orgcode = ''
                                            
                                            # 영화명이 같지만 영화코드가 다르다면 원래 코드하나로 통일한다.
                                            query = self.root.find(f"query[@id='{'SELECT_moviecode_lotte_movie_moviecode_moviename'}']").text.strip()                            
                                            parameters = (moviecode, moviename)
                                            self.sql_cursor.execute(query, parameters)
                                            self.sql_cursor.row_factory = sqlite3.Row
                                            results = self.sql_cursor.fetchall() # 결과 가져오기

                                            for row in results:
                                                orgcode = row['moviecode']

                                                query = self.root.find(f"query[@id='{'INSERT_lotte_movie'}']").text.strip()                               
                                                parameters = (moviecode, moviename, filmnamekr, gubun, orgcode)
                                                self.sql_cursor.execute(query, parameters)
                                        # [if result['cnt'] > 0: else:]

                                        self.logger.info(f"{moviecode}, {moviename}, {filmnamekr}, {gubun}")

                                        moviecode_old = moviecode

                                    # [if moviecode_old != moviecode:  # 같은 영화정보가(영화코드가) 여러번 들어오는걸 거른다. ]

                                # [for match1 in jsonpath_expr[0].value: ]
                            # [if len(parse('PlaySeqsHeader.Items').find(json_obj)) == 1: ]

                            jsonpath_expr = parse('PlayDates.ItemCount').find(json_obj)
                            item_count = jsonpath_expr[0].value if jsonpath_expr else None

                            jsonpath_expr = parse('PlayDates.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info(f'상영일 리스트 ({item_count}일간)    ')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                                self.sql_cursor.execute(self.root.find(f"query[@id='{'DELETE_lotte_playdate_cinemacode'}']").text.strip(),(cinemacode,))

                                for items in jsonpath_expr[0].value:
                                    self.logger.info(str(items['PlayDate']))

                                    query = self.root.find(f"query[@id='{'INSERT_lotte_playdate'}']").text.strip()
                                    parameters = (cinemacode, str(items['PlayDate']))
                                    self.sql_cursor.execute(query, parameters)

                                # [for items in jsonpath_expr[0].value:]
                            # [if len(parse('PlayDates.Items').find(json_obj)) == 1:]

                            jsonpath_expr = parse('PlaySeqs.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info('상영관(코드), 좌석수')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                                screenid_old = None
                                for play_data in jsonpath_expr[0].value:
                                    screenid = str(play_data['ScreenID'])  # 상영관 코드
                                    screennamekr = play_data['ScreenNameKR']  # 상영관명
                                    totalseatcount = play_data['TotalSeatCount']  # 총좌석수

                                    cinemaid = str(play_data['CinemaID'])  # 극장코드  (1016) (월드타워)
                                    screendivcode = str(play_data['ScreenDivisionCode']) # 부상영관코드 (960)
                                    screendivnamekr = play_data['ScreenDivisionNameKR']  # 부상영관명 (씨네패밀리)

                                    if screenid_old != screenid:

                                        self.logger.info(f'{screennamekr}({screenid}), {totalseatcount}석')
                                        
                                        query = self.root.find(f"query[@id='{'INSERT_lotte_screen'}']").text.strip()
                                        parameters = (screenid, cinemacode, screennamekr, screendivnamekr, totalseatcount)
                                        self.sql_cursor.execute(query, parameters)

                                        screenid_old = screenid
                                    # [if screenid_old != screenid:]

                                # [for PlayDate in jsonpath_expr[0].value:]


                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info(f'[{theather_nm}] 일자, 상영관, 회차, 시작시간~끝시간, 예약좌석수/총좌석수, 영화')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                                screenid_old = None
                                degree_no = 0
                                for play_data in jsonpath_expr[0].value:
                                    cinemanamekr = play_data['CinemaNameKR']  # 극장명
                                    sequencenogroupnamekr = play_data['SequenceNoGroupNameKR']  # 상영관그룹명
                                    screenid = str(play_data['ScreenID'])  # 상영관 코드
                                    screennamekr = play_data['ScreenNameKR']  # 상영관명
                                    moviecode = play_data['MovieCode']  # 영화코드 [영화명 + 필름종류 + 더빙/자막]
                                    bookingseatcount = play_data['BookingSeatCount']  # 예약좌석수
                                    totalseatcount = play_data['TotalSeatCount']  # 총좌석수
                                    playdate_ = play_data['PlayDt']  # 상영일자
                                    playdt = playdate_[0:4] + playdate_[5:7] + playdate_[8:10]  # 상영일자(조정)
                                    starttime = play_data['StartTime']  # 상영시간(시작)
                                    endtime = play_data['EndTime']  # 상영시간(끝)

                                    cinemaid = str(play_data['CinemaID'])  # 극장코드 (월드타워)
                                    screendivcode = str(play_data['ScreenDivisionCode'])  # 부상영관코드 (960)
                                    screendivnamekr = play_data['ScreenDivisionNameKR']  # 부상영관명 (씨네패밀리)

                                    if screendivnamekr != "일반":  # '월드타워' 점 '씨네패밀리' 관 같이 특별관인경우    
                                        screenid = screenid + "*"
                                    #

                                    if screenid_old != screenid:
                                        degree_no = 0
                                        screenid_old = screenid
                                    #
                                    degree_no += 1

                                    query = self.root.find(f"query[@id='{'SELECT_screencode_totalseatcount_lotte_screen_cinemacode_screenname'}']").text.strip()
                                    parameters = (cinemacode, screennamekr)
                                    self.sql_cursor.execute(query, parameters)
                                    self.sql_cursor.row_factory = sqlite3.Row
                                    if result := self.sql_cursor.fetchone(): # 첫 번째 결과 행 가져오기                      
                                        screencode     = result['screencode']
                                        totalseatcount = result['totalseatcount']
                                        
                                    query = self.root.find(f"query[@id='{'SELECT_moviecode_moviename_moviegenrename_filmname_lotte_movie_moviecode'}']").text.strip()
                                    parameters = (moviecode,)
                                    self.sql_cursor.execute(query, parameters)
                                    if result := self.sql_cursor.fetchone(): # 첫 번째 결과 행 가져오기                      

                                        self.logger.info(f'{playdt[-2:]}, {screennamekr}({screencode}), {degree_no}, {starttime} ~ {endtime}, {bookingseatcount} / {totalseatcount}, ({moviecode}){result["moviename"]}[{result["moviegenrename"]}/{result["filmname"]}]')

                                        query = self.root.find(f"query[@id='{'INSERT_lotte_ticketing'}']").text.strip()
                                        parameters = (cinemacode, playdt, screencode, degree_no, moviecode, starttime, endtime, bookingseatcount)
                                        self.sql_cursor.execute(query, parameters)
                                    else:
                                        self.logger.info(f'{playdt[-2:]}, {screennamekr}({screencode}), {degree_no}, {starttime} ~ {endtime}, {bookingseatcount} / {totalseatcount}, [영화정보매칭실패]({moviecode})')
                                    # [if result := self.sql_cursor.fetchone():]

                                # [for PlayDate in jsonpath_expr[0].value:]
                            # [if len(parse('PlaySeqs.Items').find(json_obj)) == 1:]

                        # [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":]

                    # [for entry in proxy.har['log']['entries']:  # 캡처된 각 요청의 세부 정보 출력]

                    proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 복수 실행을 위해 캡처된 요청 초기화
                    # break  # ------------------------------------- 디버깅용

                # [for i in range(nMin, (nMax+1)):  # 유효한 상영일만 순환  ]
            # [def __3_daily_ticketingdata(cinemacode, link):]

            while True:  # 루프를 계속해서 반복합니다.

                doit = False

                # 스페셜 극장은 빠진다. 이미 크롤링에 성공한 상영관은 열외 실패하면 다시 반복~!!
                self.sql_cursor.execute(self.root.find(f"query[@id='{'SELECT_cinemacode_spacialyn_cinemaname_link_succese_lotte_cinema_spacialyn'}']").text.strip())
                self.sql_cursor.row_factory = sqlite3.Row
                for row in self.sql_cursor.fetchall(): # 결과 가져오기
                    cinemacode = row['cinemacode']
                    spacialyn  = row['spacialyn']
                    cinemaname = row['cinemaname']
                    link       = row['link']
                    succese    = row['succese']

                    if cinemacode not in [  '1016',  '1013', """, '9102' """]:  # --------------------------------------------------------------- 디버깅용
                        continue

                    try:
                        doit = True

                        self.logger.info('')
                        self.logger.info('')
                        self.logger.info('===============================================================================================================================')
                        self.logger.info(f'--  [{spacialyn}][{succese}] ({cinemacode}){cinemaname}   ')
                        self.logger.info(f'--  {link}  ')
                        self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                        __3_daily_ticketingdata(cinemacode, link)  #  일자별로 순회 하면서 크롤링한다.  #  예외발생 test (0 / 0)

                    except Exception as e:    
                        self.sql_conn.rollback()

                        # 크롤링에 예외가 발생되어 실패
                        query = self.root.find(f"query[@id='{'UPDATE_lotte_cinema_succese_cinemacode'}']").text.strip()
                        parameters = ('X', cinemacode)
                        self.sql_cursor.execute(query, parameters)
                        self.sql_conn.commit()

                        self.logger.error('-----------------------------------------------------------------------')
                        self.logger.error(f'상영관({cinemaname})크롤링에 예외가 발생되어 실패')
                        self.logger.error(f'오류 내용! {e}')
                        self.logger.error(f'{traceback.print_exc()}')
                        self.logger.error('-----------------------------------------------------------------------')

                        # 드라이버 재 실행 !!
                        chm_driver.quit()
                        server.stop()

                        server.start()
                        chm_driver = webdriver.Chrome(options=chrome_options)

                    else:
                        # 정상적으로 크롤링된 상영관
                        query = self.root.find(f"query[@id='{'UPDATE_lotte_cinema_succese_cinemacode'}']").text.strip()
                        parameters = ('O', cinemacode)
                        self.sql_cursor.execute(query, parameters)
                        self.sql_conn.commit()

                    finally: 
                        pass  # 예외 발생 여부와 관계없이 항상 실행되는 코드

                #  [for cinemacode, cn_value in self.dicCinemas.items():  # 전체 극장을 순회한다.]

                if doit == False:  # 완전히 모든 상영관이 크롤링에 성공 했을시 빠저나간다.
                    break
            # [while True:  # 루프를 계속해서 반복합니다.]
        # [def _crawlLotte_3_ticketing(chm_driver):]


        try:

            if platform.system() == 'Windows':
                server_path = 'C://Crawlling2//browsermob-proxy-2.1.4//bin//browsermob-proxy.bat'
            else:
                server_path = '/browsermobproxy/browsermob-proxy-2.1.4/bin/browsermob-proxy'
            server = Server(server_path)
            server.start()

            proxy = server.create_proxy()
            chrome_options = webdriver.ChromeOptions()
            #chrome_options.add_argument('--headless')  # Headless 모드 설정
            #chrome_options.add_argument("--start-maximized")  # 창을 최대화로 시작
            chrome_options.add_argument("--blink-settings=imagesEnabled=false") #  이미지가 로드되지 않으므로 페이지 로딩 속도가 향상
            chrome_options.add_argument('--excludeSwitches=enable-automation')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--start-minimized')  # 최소화된 상태로 창을 시작
            chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
            chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
            chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_driver = webdriver.Chrome(options=chrome_options)

            proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 요청 캡처 활성화

            _1_crawlLotte_boxoffice(chrome_driver)  # 1. 영화/현재상영작 (https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. 
            _2_crawlLotte_cinema(chrome_driver)     # 2. 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다.             
            _3_crawlLotte_ticketing(chrome_driver)  # 3. 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다.

            chrome_driver.quit()
            server.stop()
        except Exception as e:

            self.logger.error('Lotte 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
    # [def crawling(self):]
    
    def uploading(self):
        
        super().uploading()
        print("Uploading Lotte data...")
    # [def uploading(self):]
# [class ActCrlLotte(ActCrlSupper):]   

if __name__ == '__main__':

    maxDateRage = 12  # 최대 일수

    if len(sys.argv) == 2:
        try:
            dateRange = min(max(int(sys.argv[1]), 0), maxDateRage)
        except ValueError:
            dateRange = maxDateRage
    else:
        dateRange = maxDateRage

    actCrlLotte = ActCrlLotte(date_range = dateRange)  # Lotte
    actCrlLotte.crawling()
    actCrlLotte.uploading()
    
# [if __name__ == '__main__':]    
