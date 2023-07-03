"""

"""
from Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import traceback
import platform
import os
import time
import json
from jsonpath_rw import parse  # pip install jsonpath-rw  https://pypi.python.org/pypi/jsonpath-rw

from browsermobproxy import Server  # pip install browsermob-proxy

from selenium import webdriver # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup  # pip install beautifulsoup4
from urllib.parse import parse_qs, urlparse

class ActCrlLotte(ActCrlSupper):

    # __init__, __del__ =================================================================
    def __init__(self, date_range): # 생성자

        super().__init__()

        self.logger = get_logger('lotte')   # 파이션 로그
        self.dateRage = date_range           # 크롤링 할 날 수

        self.dicTickecting = {}  # 티켓팅 정보     

    def __del__(self): # 소멸자

        clear_logger('lotte')  # 한달전 로그파일을 삭제한다.
        super().__del__()

    # -----------------------------------------------------------------------------------

    # def crawling(self): ===============================================================
    def crawling(self):
        # -----------------------------------------------------------------------------------
        #  영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. 
        #
        def _crawlingLotte_boxoffice(chm_driver):

            self.logger.info('========================================================================================================')
            self.logger.info('영화 / 현재상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1),                               ')
            self.logger.info('영화 / 상영예정작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=5) 에서 영화데이터를 가지고 온다. ')
            self.logger.info('--------------------------------------------------------------------------------------------------------')

            self.sql_cursor.execute(' DELETE FROM lotte_movie ')

            self.logger.info('-------------------------------------------------------------------------------')
            self.logger.info('코드, 영화명, 장르, 예매, 개봉일, 관람등급                                     ')
            self.logger.info('-------------------------------------------------------------------------------')

            arrUrl = ["https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1", "https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=5"]
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

                        query = ''' INSERT OR REPLACE 
                                                 INTO lotte_movie (moviecode, movienamekr, moviegenrename, bookingyn, releasedate, viewgradenameus)
                                               VALUES             (?,         ?,           ?,              ?,         ?,           ?              )   '''
                        
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

                            parameters = (representationmoviecode, movienamekr, moviegenrename, bookingyn, releasedate, viewgradenameus)
                            self.sql_cursor.execute(query, parameters)                            

                        # end of [for match in parse('Movies.Items[*]').find(json_obj):]

                        self.sql_conn.commit()

                    # end of [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx": ]

                # end of [for entry in proxy.har['log']['entries']:  # 각 캡처된 요청의 세부 정보 출력 ]

                proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 복수 실행을 위해 캡처된 요청 초기화

            # end of [for url in arrUrl:]

        # end of [def _crawlingLotte_boxoffice(chm_driver):]

        # -----------------------------------------------------------------------------------
        #  영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. 
        #
        def _crawlingLotte_cinema(chm_driver):

            self.logger.info('=========================================================================================')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. ')
            self.logger.info('-----------------------------------------------------------------------------------------')

            def __parse_links(tag_lst):

                a_tags = BeautifulSoup(tag_lst, 'html.parser').find_all('a')

                pas_links = []

                for a_tag in a_tags:
                    link = a_tag['href']
                    parsed_url = urlparse(link)
                    params = parse_qs(parsed_url.query)

                    url = link.split('?')[0]
                    query_params = {ikey: ivalue[0] for ikey, ivalue in params.items()}
                    text = a_tag.text.replace("\n", "").strip()

                    pas_links.append({'url': url, 'query_params': query_params, 'text': text, 'link': link})
                    # print("URL:", parsed_link['url'],", Query Params:", parsed_link['query_params'],", Text:", parsed_link['text'], link:", parsed_link['link'])

                return pas_links

            # ----------------- end of [ def parse_links(html): ]

            chm_driver.get('https://www.lottecinema.co.kr/NLCHS')
            chm_driver.implicitly_wait(1)

            html = chm_driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
            soup = BeautifulSoup(html, "html.parser")

            if tag1 := soup.select_one("#nav > ul > li:nth-child(3) > div > ul"):  # 메인 메뉴의 '영화관' 하위 메뉴 탐색

                tag_lst = ''
                tags2 = tag1.select('li > a:not([href="#"])')
                for tag2 in tags2:  # print(tag2)
                    tag_lst += tag2.prettify()

                parsed_links = __parse_links(tag_lst)  # <a> 태그 분해

                self.sql_cursor.execute(' DELETE FROM lotte_cinema ')

                self.logger.info('--------------------------------------')
                self.logger.info('코드, 스페셜관, 극장명, 링크, 성공여부')
                self.logger.info('--------------------------------------')

                arrUrl = ['https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema','https://www.lottecinema.co.kr/NLCHS/Cinema/Detail']
                query = ''' INSERT OR REPLACE 
                                         INTO lotte_cinema (cinemacode, spacialyn, cinemaname, link, succese )
                                       VALUES              (?,          ?,         ?,          ?,    '_'     )   '''
                for parsed_link in parsed_links:  # print(parsed_link)
                    if parsed_link['url'] in arrUrl:
                    
                        if parsed_link['url'] == arrUrl[0]:  # 극장(스페셜관)정보저장
                            spacialyn = 'Y'
                            cinemacode = parsed_link['query_params']['screendivcd']

                        if parsed_link['url'] == arrUrl[1]:  # 극장(일반)정보저장                        
                            spacialyn = 'N'
                            cinemacode = parsed_link['query_params']['cinemaID']

                        self.logger.info(f"{cinemacode}, {spacialyn}, {parsed_link['text']}, {parsed_link['link']}")

                        parameters = (cinemacode, spacialyn, parsed_link['text'], parsed_link['link'])
                        self.sql_cursor.execute(query, parameters)                            

                self.sql_conn.commit()
            
            # end of [if tag1 := soup.select_one("#nav > ul > li:nth-child(3) > div > ul"):  # 메인 메뉴의 '영화관' 하위 메뉴 탐색]    

        # end of [def _crawlingLotte_cinema(chm_driver):]

        # -----------------------------------------------------------------------------------
        # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다.
        #
        def _crawlingLotte_ticketing(chm_driver):

            self.logger.info('========================================================================================================')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. ')
            self.logger.info('--------------------------------------------------------------------------------------------------------')

            def __daily_ticketingdata(cinemacode, cinemaname, link):

                _arrTickectRaw = []  # 상영정보( 0.일자, 1.상영관코드, 2.회차번호, 3.상영관명, 4.시작시간, 5.종료시간, 6.예약좌석수, 7.총좌석수, 8.영화코드, 9.영화명 )의 배열 - 한개 극장단위 리턴값

                movie_count = 0

                self.logger.info(f'{spacialyn} {cinemaname}({cinemacode}[{succese}]) : URL {link}')

                chm_driver.get(link)   # 웹사이트로 이동
                time.sleep(0.5)

                html = chm_driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
                soup = BeautifulSoup(html, 'html.parser')

                if soup.select_one("ul > li"):  # 메인 메뉴의 '영화관' 하위 메뉴 탐색
                    button = chm_driver.find_elements(By.XPATH, '//*[text()="확인"]')  # 난데없는 팝업창이 나오면 '확인'을 누를다...
                    if len(button) > 0:  # 버튼이 발견되면...
                        element = button[0]
                        element.click()
                        time.sleep(1)
                    #
                #

                theather_nm = chm_driver.find_elements(By.XPATH, '//*[@id="contents"]/div[1]/div[1]/h3')[0].text  # 타이틀의 극장명을 읽는다.

                button = chm_driver.find_elements(By.XPATH, '//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div')  # 전체 상영일들을 구한다.

                arr_ablity_day = []

                for i in range(1, (len(button) + 1)):  # 전체 상영일 순환

                    day_a_tag = chm_driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a')  # 일자 선택 버튼

                    if i <= (self.dateRage+1):
                        if 'disabled' in day_a_tag.get_attribute('class'):
                            arr_ablity_day.append('F')  # 무효한 상영일
                        else:
                            arr_ablity_day.append('T')  # 유효한 상영일
                    else:
                        arr_ablity_day.append('F')  # 무효한 상영일
                # end of [for i in range(1, (count+1)):  # 전체 상영일 순환 ]

                i = 0
                for ablityDay in arr_ablity_day:  # 유효한 상영일만 순환

                    i = i + 1

                    if ablityDay == 'F' or i > 14:  # 다음 페이지 문제로 인해 무조건 14 일자 까지만..
                        continue

                    div_act = chm_driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}][contains(@class, "active")]')
                    if not div_act:
                        chm_driver.find_element(By.XPATH, '//*[@id="timeTable"]/div[1]/div/ul/div[2]/button[2]').click()  # 다음페이지 누르기..!!!
                        time.sleep(1)

                    chm_driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a').click()  # 상영일 누르기..!!!
                    time.sleep(0.5)

                    play_date = ''

                    for entry in proxy.har['log']['entries']:  # 캡처된 각 요청의 세부 정보 출력
                        request = entry['request']
                        response = entry['response']

                        if response['content']['size'] == 0:
                            continue

                        if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":

                            json_obj = json.loads(request['postData']['text'].split('\r\n')[3])

                            jsonpath_expr = parse('playDate').find(json_obj)
                            play_date = jsonpath_expr[0].value if jsonpath_expr else None

                            # JSON 파싱
                            try:
                                json_obj = json.loads(response['content']['text'])  ###########################
                            except Exception as e:
                                self.logger.error(f'오류 내용! {e}')
                                raise e

                            jsonpath_expr = parse('PlaySeqsHeader.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                self.logger.info('-------------------------------------')
                                self.logger.info('no: 영화코드, 영화명,       더빙/자막')
                                self.logger.info('-------------------------------------')

                                moviecode_old = ''
                                for match1 in jsonpath_expr[0].value:
                                    moviecode = match1['MovieCode']  # 영화코드

                                    if moviecode_old != moviecode:  # 같은 영화정보가(영화코드가) 여러번 들어오는걸 거른다.
                                        moviename = match1['MovieNameKR']  # 영화명
                                        filmnamekr = match1['FilmNameKR']  # 필름종류
                                        gubun = match1['TranslationDivisionNameKR']  # 더빙/자막

                                        self.dicMovies[moviecode] = [moviename, filmnamekr, gubun]  # 영화정보를 저장한다. 영화명 + 필름종류 + 더빙/자막

                                        if moviecode not in self.dicMovieData:  # 박스 오피스에서 긁어온 영화리스트에 없는 영화코드가 발생되면..

                                            findkey = -1
                                            for md_key, md_value in self.dicMovieData.items():
                                                if md_value[0] == moviename and md_value[5] == -1 and moviecode != md_key:  # 영화명이 같지만 영화코드가 다르다면 원래 코드하나로 통일한다.
                                                    findkey = md_key

                                            self.dicMovieData[moviecode] = [moviename, filmnamekr, "", "", "", findkey]  # 영화데이터 정보 (박스 오피스에서 긁어온 영화리스트에 추가한다...)
                                        #

                                        movie_count += 1
                                        self.logger.info(f"{movie_count} : {moviecode}, {moviename}({filmnamekr}), {gubun}")

                                        moviecode_old = moviecode
                                    # end of [if moviecode_old != moviecode:  # 같은 영화정보가(영화코드가) 여러번 들어오는걸 거른다. ]
                                # end of [for match1 in jsonpath_expr[0].value: ]
                            # end of [if len(parse('PlaySeqsHeader.Items').find(json_obj)) == 1: ]

                            jsonpath_expr = parse('PlayDates.ItemCount').find(json_obj)
                            item_count = jsonpath_expr[0].value if jsonpath_expr else None

                            jsonpath_expr = parse('PlayDates.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                self.logger.info('-------------------------------------')
                                self.logger.info(f'상영일 ({item_count})')
                                self.logger.info('-------------------------------------')

                                for items in jsonpath_expr[0].value:
                                    self.logger.info(str(items['PlayDate']))
                            #

                            jsonpath_expr = parse('PlaySeqs.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                # dicScreen를 먼저구하기 위해 2번 돈다.
                                dic_screen = {}

                                for play_data in jsonpath_expr[0].value:
                                    screenid = str(play_data['ScreenID'])  # 상영관 코드
                                    screennamekr = play_data['ScreenNameKR']  # 상영관명
                                    totalseatcount = play_data['TotalSeatCount']  # 총좌석수

                                    cinemaid = str(play_data['CinemaID'])  # 극장코드 (월드타워)
                                    screendivnamekr = play_data['ScreenDivisionNameKR']  # 부상영관명 (씨네패밀리)
                                    screendivcode = str(play_data['ScreenDivisionCode'])  # 부상영관코드 (960)

                                    if cinemaid == "1016" and screendivcode == "960":  # 월드타워 점 씨네패밀리 관 인경우
                                        screenid = screenid + "*"
                                        screennamekr = screennamekr + " " + screendivnamekr

                                    dic_screen[screenid] = [screennamekr, totalseatcount]

                                # end of [for PlayDate in jsonpath_expr[0].value:]

                                self.logger.info('----------------')
                                self.logger.info('관(코드), 좌석수')
                                self.logger.info('----------------')

                                for scr_key, scr_value in dic_screen.items():
                                    self.logger.info(f'{scr_value[0]}({scr_key}), {scr_value[1]}석')


                                self.logger.info('-------------------------------------------------------------------------------')
                                self.logger.info(f'[{theather_nm}] 일자, 상영관, 회차, 영화, 시작시간~끝시간, 예약좌석수/총좌석수')
                                self.logger.info('-------------------------------------------------------------------------------')

                                screenid_old = None
                                screen_no = 0
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
                                    screendivnamekr = play_data['ScreenDivisionNameKR']  # 부상영관명 (씨네패밀리)
                                    screendivcode = str(play_data['ScreenDivisionCode'])  # 부상영관코드 (960)

                                    if cinemaid == "1016" and screendivcode == "960":  # 월드타워 점 씨네패밀리 관 인경우
                                        screenid = screenid + "*"
                                        screennamekr = screennamekr + " " + screendivnamekr
                                    # print(self.dicMovies[moviecode][1]+':'+self.dicMovies[moviecode][0])

                                    if screenid_old != screenid:

                                        screen_no += 1
                                        degree_no = 0
                                        screenid_old = screenid
                                    #

                                    degree_no += 1                                    
                                     
                                    self.logger.info(f'{playdt[-2:]}, {screennamekr}, {(screen_no * 100) + degree_no}, {self.dicMovies[moviecode][0]}[{self.dicMovies[moviecode][1]}]({self.dicMovies[moviecode][2]}), {starttime} ~ {endtime}, {bookingseatcount} / {totalseatcount}')

                                    # 상영정보( 0.일자, 1.상영관코드, 2.회차번호, 3.상영관명, 4.시작시간, 5.종료시간, 6.예약좌석수, 7.총좌석수, 8.영화코드, 9.영화명 )의 배열
                                    _arrTickectRaw.append([playdt, screenid, (screen_no * 100) + degree_no, screennamekr, starttime, endtime, bookingseatcount, totalseatcount, moviecode, self.dicMovies[moviecode][0]])

                                # end of [for PlayDate in jsonpath_expr[0].value:]

                            # end of [ if len(jsonpath_expr = parse('PlaySeqs.Items').find(json_obj)) == 1:]

                        # end of [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":]

                    # end of [for entry in proxy.har['log']['entries']:  # 캡처된 각 요청의 세부 정보 출력]

                    proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 복수 실행을 위해 캡처된 요청 초기화

                    #break  # ------------------------------------- 디버깅용

                # end of [for i in range(nMin, (nMax+1)):  # 유효한 상영일만 순환  ]

                return _arrTickectRaw
            # end of [def __read_cinemas():]

            def __makedic_ticketingdata(_arrTickectRaw):

                _arrTickect1 = []  # 티켓팅 정보1 [playdate, cinemaid, cinemaname] 극장에 상영예정일 리스트
                _arrTickect2 = []  # 티켓팅 정보2 [playdate, cinemaid, screenid, cinemaname, screennamekr, totalseatcount] 상영관 리스트
                _arrTickect3 = []  # 티켓팅 정보3 [playdate, cinemaid, screenid, degreeNo, cinemaname, screennamekr, starttime, endtime, bookingseatcount, moviecode, moviename, filmnamekr, gubun ] 상영시간 리스트

                play_dates = np.unique(np.array(_arrTickectRaw)[:, 0]) # playdt 값을 추출하여 중복 제거 후 numpy 배열로 변환
                for play_date in play_dates:
                    # 티켓팅 정보1 [playdate, cinemaid, cinemaname] 극장에 상영예정일 리스트
                    _arrTickect1.append([play_date, cinemacode, cinemaname])  

                sorted_input = sorted(_arrTickectRaw, key=lambda x: (x[0], x[1], x[3], x[7]))  # 입력을 playdt, screenid, screennamekr, totalseatcount 순서로 정렬
                groups = groupby(sorted_input, key=lambda x: (x[0], x[1], x[3], x[7]))  # playdt, screenid, screennamekr, totalseatcount로 그룹핑
                for idx1, (key, group) in enumerate(groups):  # 그룹화된 결과 출력
                    play_date, screenid, screennamekr, totalseatcount = key  # key 언패킹

                    # 티켓팅 정보2 [playdate, cinemaid, screenid, cinemaname, screennamekr, totalseatcount] 상영관 리스트
                    _arrTickect2.append([play_date, cinemacode, screenid,  cinemaname, screennamekr, totalseatcount]) 

                    for item in group:
                        # 티켓팅 정보3 [playdate, cinemaid, screenid, degreeNo, cinemaname, screennamekr, starttime, endtime, bookingseatcount, moviecode, moviename, filmnamekr, gubun ] 상영시간 리스트
                        _arrTickect3.append([play_date, cinemacode, screenid,  item[2], cinemaname, screennamekr, item[4], item[5], item[6], item[7], item[8], item[9]])  

                #self.logger.error( f'json.dumps(_arrTickect1) => {json.dumps(_arrTickect1)}')
                #self.logger.error( f'json.dumps(_arrTickect2) => {json.dumps(_arrTickect2)}')    
                #self.logger.error( f'json.dumps(_arrTickect3) => {json.dumps(_arrTickect3)}')

                # _arrTickect1을 딕셔너리(dicTickecting1)로 변경
                for data in _arrTickect1:
                    play_date = data[0]  # 상영일자. 
                    arting1_values = data[1:] # ex ['1013', '가산디지털'] ['101705', '독산']
    
                    matching_entries1 = [
                        entry for entry in _arrTickect2   # .append([arting1_playdt, cinemacode, screenid,  cinemaname, screennamekr, totalseatcount])
                        if entry[0] == play_date and entry[1] == arting1_values[0]  # [상영일자, 극장코드]로 그룹핑
                    ]
                    
                    for entry1 in matching_entries1:                                    
                        #new_entry2 = [entry[2], entry[3], entry[4], entry[5]] # 상영코드, [극장명], 상영관명, 총좌석수
                        new_entry2 = [entry1[2],  entry1[4], entry1[5]] # 상영코드,  상영관명, 총좌석수

                        matching_entries2 = [
                            entry for entry in _arrTickect3 
                            if entry[0] == play_date and entry[1] == arting1_values[0] and entry[2] == entry1[2]  # [상영일자, 극장코드, 상영코드]로 그룹핑
                        ]

                        for entry2 in matching_entries2:                                    
                            # [degreeNo, cinemaname, screennamekr, starttime, endtime, bookingseatcount, moviecode, moviename, filmnamekr]
                            new_entry3 = [entry2[3],  entry2[4], entry2[5],  entry2[6], entry2[7], entry2[8], entry2[9], entry2[10], entry2[11]]  

                            new_entry2.append(new_entry3)
                                            
                        arting1_values.append(new_entry2)
                                                
                    dicTickecting.setdefault(play_date, []).append(arting1_values)

                return dicTickecting
            # end of [def __makedic_ticketingdata(_arrTickectRaw):]


            while True:  # 루프를 계속해서 반복합니다.

                doit = False

                # 스페셜 극장은 빠진다.  이미 크롤링에 성공한 상영관은 열외
                query = ''' SELECT cinemacode, spacialyn, cinemaname, link, succese  FROM lotte_cinema  WHERE spacialyn='N' AND succese = '_' '''  
                self.sql_cursor.execute(query)                
                results = self.sql_cursor.fetchall() # 결과 가져오기

                for row in results:
                    cinemacode  = row[0]
                    spacialyn   = row[1]
                    cinemaname  = row[2]
                    link        = row[3]
                    succese     = row[4]

                    #if cinemacode not in ['1024'
                    #                 #, '9098'
                    #                 #, '9101'
                    #                 #, '9102'
                    #                 ]:  # --------------------------------------------------------------- 디버깅용
                    #    continue

                    try:
                        doit = True

                        # 상영정보( 0.일자, 1.상영관코드, 2.회차번호, 3.상영관명, 4.시작시간, 5.종료시간, 6.예약좌석수, 7.총좌석수, 8.영화코드, 9.영화명 )의 배열
                        _arrTickectRaw = __daily_ticketingdata(cinemacode, spacialyn, cinemaname, link, succese)  #  일자별로 순회 하면서 크롤링한다.  #  예외발생 test

                        if len(_arrTickectRaw) > 0:
                            dicTickecting = __makedic_ticketingdata(_arrTickectRaw)

                            self.dicTickecting.update(dicTickecting)

                        #self.logger.error( json.dumps(self.dicTickecting))

                    except Exception as e:    
                        # 크롤링에 예외가 발생되어 실패
                        query = ''' UPDATE lotte_cinema
                                       SET succese = ?
                                     WHERE cinemacode  = ?   '''
                        parameters = ('X', cinemacode)
                        self.sql_cursor.execute(query, parameters)

                        self.logger.error('-----------------------------------------------------------------------')
                        self.logger.error(f'상영관({cinemaname})크롤링에 예외가 발생되어 실패')
                        self.logger.error(f'오류 내용! {e}')
                        self.logger.error(f'{traceback.print_exc()}')
                        self.logger.error('-----------------------------------------------------------------------')

                        chm_driver.quit()
                        server.stop()

                        server.start()
                        chm_driver = webdriver.Chrome(options=chrome_options)
                    else:
                        # 정상적으로 크롤링된 상영관
                        query = ''' UPDATE lotte_cinema
                                       SET succese = ?
                                     WHERE cinemacode  = ?   '''
                        parameters = ('O', cinemacode)
                        self.sql_cursor.execute(query, parameters)

                    finally: 
                        pass  # 예외 발생 여부와 관계없이 항상 실행되는 코드

                #  end of [for cinemacode, cn_value in self.dicCinemas.items():  # 전체 극장을 순회한다.]

                if doit == False:  # 완전히 모든 상영관이 크롤링에 성공 했을시 빠저나간다.
                    break

            # end of [while True:  # 루프를 계속해서 반복합니다.]
            
        # end of [def _crawlingLotte_ticketing(chm_driver):]

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

            # ------------------------------
            #_crawlingLotte_boxoffice(chrome_driver)  # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. 
            _crawlingLotte_cinema(chrome_driver)     # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. 
            _crawlingLotte_ticketing(chrome_driver)  # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
            # ------------------------------

            chrome_driver.quit()
            server.stop()

        except Exception as e:
            self.logger.error('LOTTE 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
        
    # end of [def crawling(self):] ------------------------------------------------------
    
    # def uploading(self): ==============================================================
    def uploading(self):
        print("Uploading Lotte data...")
    # -----------------------------------------------------------------------------------
    
# end of [class ActCrlLotte(ActCrlSupper):]   



if __name__ == '__main__':

    actCrlLotte = ActCrlLotte(date_range=12)  # Lotte
    actCrlLotte.crawling()
    actCrlLotte.uploading()
    
# end of [if __name__ == '__main__':]    
