'''
Chrome의 보안 설정을 변경하여 스크립트 실행을 허용하도록 설정하는 방법은 다음과 같이 진행할 수 있습니다. 그러나 이는 보안 위험이 있을 수 있으므로 주의해야 합니다.
Chrome 브라우저를 엽니다.
주소창에 chrome://flags를 입력하고 Enter 키를 눌러 Chrome의 은폐된 설정 페이지에 접속합니다.
검색 상자에 "unsafely-treat-insecure-origin-as-secure"라고 입력하여 해당 설정을 찾습니다.
"Insecure origins treated as secure" 옵션을 찾고 해당 옵션의 드롭다운 메뉴를 클릭합니다.
드롭다운 메뉴에서 "Enable"을 선택합니다.
변경 사항을 적용하기 위해 Chrome을 재시작합니다.
이제 Chrome은 보안 연결이 아닌 원본(예: HTTPS가 아닌 사이트)에서 실행되는 스크립트도 허용할 것입니다. 이로 인해 "A parser-blocking, cross site script"와 관련된 오류가 발생하지 않을 수 있습니다.
하지만 이 방법은 Chrome의 보안 기능을 일시적으로 약화시키므로 주의해야 합니다. 보안 상의 이유로 이 설정을 영구적으로 유지하지 않는 것이 좋습니다. 가능한 경우, 해당 사이트 또는 서비스 제공자와 협력하여 인증서 문제를 해결하는 것이 더 안전한 방법입니다.
'''
import sys
import json
import time
import requests
import traceback

import numpy as np  # pip install numpy
from itertools import groupby

from bs4 import BeautifulSoup  # pip install beautifulsoup4
from browsermobproxy import Server  # pip install browsermob-proxy
from jsonpath_rw import parse  # pip install jsonpath-rw  https://pypi.python.org/pypi/jsonpath-rw
from urllib.parse import parse_qs, urlparse

from selenium import webdriver # pip install selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from Crawl_Supper import Crawl
from Crawling_Logger import get_logger, clean_logger


class CrawlLotte(Crawl):

    # ===================================================================================
    def __init__(self, log_lotte, date_rage):

        self.logger = log_lotte  # 파이션 로그
        self.dateRage = date_rage  # 크롤링 할 날수

        self.dicMovieData = {}  # 영화데이터 정보
        self.dicCinemas = {}  # 극장 코드 정보
        self.dicMovies = {}  # 영화 코드 정보

        self.dicTicketingData = {}  # 티켓팅 정보
        self.dicTickecting = {}        

    # ===================================================================================

    # ===================================================================================
    def crawling(self):

        # -----------------------------------------------------------------------------------
        #  영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
        #
        def _crawl_lotte_boxoffice(chm_driver):

            self.logger.info('===============================================================================================================================')
            self.logger.info('영화 / 현재상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1),                                                      ')
            self.logger.info('영화 / 상영예정작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=5) 에서 영화데이터를 가지고 온다. (dicMovieData)         ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            movie_count = 1

            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
            self.logger.info('no, 코드, 영화명, 장르, 예매, 개봉일, 관람등급')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

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

                        for match in parse('Movies.Items[*]').find(json_obj):

                            representationmoviecode = str(match.value['RepresentationMovieCode'])
                            movienamekr = str(match.value['MovieNameKR']).strip()
                            moviegenrename = str(match.value['MovieGenreName'])
                            bookingyn = str(match.value['BookingYN'])
                            releasedate = str(match.value['ReleaseDate'])
                            releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                            viewgradenameus = str(match.value['ViewGradeNameUS'])

                            if movienamekr == '' or movienamekr == 'AD': continue

                            self.dicMovieData[representationmoviecode] = [movienamekr, moviegenrename, bookingyn, releasedate, viewgradenameus, -1]  # 영화데이터 정보

                            self.logger.info(f'{movie_count} : {representationmoviecode},{movienamekr},{moviegenrename},{bookingyn},{releasedate},{viewgradenameus}')
                            movie_count += 1
                        #

                    # end of [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx": ]
                # end of [for entry in proxy.har['log']['entries']:  # 각 캡처된 요청의 세부 정보 출력 ]

                proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 복수 실행을 위해 캡처된 요청 초기화

            # end of [for url in arrUrl:]
            pass
        # end of [def _crawl_lotte_boxoffice(self): ]

        # -----------------------------------------------------------------------------------
        #  영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
        #
        def _crawl_lotte_cinema(chm_driver):

            self.logger.info('===============================================================================================================================')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)     ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

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

                sortsequence = 0
                for parsed_link in parsed_links:  # print(parsed_link)
                    sortsequence = sortsequence + 1

                    if parsed_link['url'] == 'https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema':  # 극장(스페셜관)정보저장                        
                        self.dicCinemas[parsed_link['query_params']['screendivcd']] = ['Y', sortsequence, parsed_link['text'], parsed_link['link'], '_']

                    if parsed_link['url'] == 'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail':  # 극장(일반)정보저장                        
                        self.dicCinemas[parsed_link['query_params']['cinemaID']] = ['N', sortsequence, parsed_link['text'], parsed_link['link'], '_']


                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                self.logger.info(' 코드, 스페셜관, 정렬일련번호, 극장명')
                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                for key, value in self.dicCinemas.items():
                    self.logger.info(f'{key} : {value[0]},{value[1]},{value[2]},{value[3]}')

        # end of [def _crawl_lotte_cinema(self):]

        # -----------------------------------------------------------------------------------
        # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
        #
        def _crawl_lotte_ticketing(chm_driver):

            self.logger.info('=================================================================================================================++++==========')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)     ')
            self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

            def __daily_ticketingdata():                

                _arrTickectRaw = []  # 상영정보( 0.일자, 1.상영관코드, 2.회차번호, 3.상영관명, 4.시작시간, 5.종료시간, 6.예약좌석수, 7.총좌석수, 8.영화코드, 9.영화명 )의 배열 - 한개 극장단위 리턴값

                movie_count = 0

                self.logger.info(f'{cn_value[0]}/{cn_value[2]} ({cn_key}[{cn_value[4]}]) : URL {cn_value[3]}')

                chm_driver.get(cn_value[3])   # 웹사이트로 이동
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
                                self.logger.error(f'{traceback.print_exc()}')
                                raise e

                            jsonpath_expr = parse('PlaySeqsHeader.Items').find(json_obj)
                            if len(jsonpath_expr) == 1:

                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info('no: 영화코드, 영화명,       더빙/자막')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

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

                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info(f'상영일 ({item_count})')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

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

                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info('관(코드), 좌석수')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

                                for scr_key, scr_value in dic_screen.items():
                                    self.logger.info(f'{scr_value[0]}({scr_key}), {scr_value[1]}석')


                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')
                                self.logger.info(f'[{theather_nm}] 일자, 상영관, 회차, 영화, 시작시간~끝시간, 예약좌석수/총좌석수')
                                self.logger.info('-------------------------------------------------------------------------------------------------------------------------------')

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
                    _arrTickect1.append([play_date, cn_key, cn_value[2]])  

                sorted_input = sorted(_arrTickectRaw, key=lambda x: (x[0], x[1], x[3], x[7]))  # 입력을 playdt, screenid, screennamekr, totalseatcount 순서로 정렬
                groups = groupby(sorted_input, key=lambda x: (x[0], x[1], x[3], x[7]))  # playdt, screenid, screennamekr, totalseatcount로 그룹핑
                for idx1, (key, group) in enumerate(groups):  # 그룹화된 결과 출력
                    play_date, screenid, screennamekr, totalseatcount = key  # key 언패킹

                    # 티켓팅 정보2 [playdate, cinemaid, screenid, cinemaname, screennamekr, totalseatcount] 상영관 리스트
                    _arrTickect2.append([play_date, cn_key, screenid,  cn_value[2], screennamekr, totalseatcount]) 

                    for item in group:
                        # 티켓팅 정보3 [playdate, cinemaid, screenid, degreeNo, cinemaname, screennamekr, starttime, endtime, bookingseatcount, moviecode, moviename, filmnamekr, gubun ] 상영시간 리스트
                        _arrTickect3.append([play_date, cn_key, screenid,  item[2], cn_value[2], screennamekr, item[4], item[5], item[6], item[7], item[8], item[9]])  

                #self.logger.error( f'json.dumps(_arrTickect1) => {json.dumps(_arrTickect1)}')
                #self.logger.error( f'json.dumps(_arrTickect2) => {json.dumps(_arrTickect2)}')    
                #self.logger.error( f'json.dumps(_arrTickect3) => {json.dumps(_arrTickect3)}')

                # _arrTickect1을 딕셔너리(dicTickecting1)로 변경
                for data in _arrTickect1:
                    play_date = data[0]  # 상영일자. 
                    arting1_values = data[1:] # ex ['1013', '가산디지털'] ['101705', '독산']
    
                    matching_entries1 = [
                        entry for entry in _arrTickect2   # .append([arting1_playdt, cn_key, screenid,  cn_value[2], screennamekr, totalseatcount])
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

            #####################################################

            dicTickecting = {} 

            while True:  # 루프를 계속해서 반복합니다.

                doit = False

                for cn_key, cn_value in self.dicCinemas.items():  # 전체 극장을 순회한다.

                    #if cn_key not in ['1024'
                    #                 #, '9098'
                    #                 #, '9099'
                    #                 #, '9100'
                    #                 #, '9101'
                    #                 #, '9102'
                    #                 ]:  # --------------------------------------------------------------- 디버깅용
                    #    continue

                    if cn_value[0] == 'Y':  # 스페셜 극장은 빠진다.
                        continue
                    if cn_value[4] == 'O':  # 이미 크롤링에 성공한 상영관은 열외
                        continue

                    try:
                        doit = True

                        # 상영정보( 0.일자, 1.상영관코드, 2.회차번호, 3.상영관명, 4.시작시간, 5.종료시간, 6.예약좌석수, 7.총좌석수, 8.영화코드, 9.영화명 )의 배열
                        _arrTickectRaw = __daily_ticketingdata()  #  일자별로 순회 하면서 크롤링한다.  #  예외발생 test

                        # self.logger.error( json.dumps(_arrTickectRaw))
                        #if cn_key == '1017':
                        #    1 / 0
                        if len(_arrTickectRaw) > 0:
                            dicTickecting = __makedic_ticketingdata(_arrTickectRaw)

                            self.dicTickecting.update(dicTickecting)

                        #self.logger.error( json.dumps(self.dicTickecting))

                    except Exception as e:    
                        self.dicCinemas[cn_key][4] = 'X'  # 크롤링에 예외가 발생되어 실패

                        self.logger.error('-----------------------------------------------------------------------')
                        self.logger.error(f'상영관({cn_value[2]})크롤링에 예외가 발생되어 실패')
                        self.logger.error(f'오류 내용! {e}')
                        self.logger.error(f'{traceback.print_exc()}')
                        self.logger.error('-----------------------------------------------------------------------')

                        chm_driver.quit()
                        server.stop()

                        server.start()
                        chm_driver = webdriver.Chrome(options=chrome_options)
                    else:
                        self.dicCinemas[cn_key][4] = 'O'  # 정상적으로 크롤링된 상영관
                    finally: 
                        pass  # 예외 발생 여부와 관계없이 항상 실행되는 코드
                #  end of [for cn_key, cn_value in self.dicCinemas.items():  # 전체 극장을 순회한다.]

                if doit == False:  # 완전히 모든 상영관이 크롤링에 성공 했을시 빠저나간다.
                    break

            # end of [while True:  # 루프를 계속해서 반복합니다.]
            
        # end of [def _crawl_lotte_ticketing(chm_driverdriver):]

        ############################################

        try:
            server_path = 'C://Crawlling2//browsermob-proxy-2.1.4//bin//browsermob-proxy.bat'
            server = Server(server_path)
            server.start()

            proxy = server.create_proxy()
            chrome_options = webdriver.ChromeOptions()
            """
            chrome_options.add_argument('--headless')  # Headless 모드 설정
            chrome_options.add_argument('--start-maximized')  # 창을 최대화로 시작
            """
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
            _crawl_lotte_boxoffice(chrome_driver)  # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
            _crawl_lotte_cinema(chrome_driver)     # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
            _crawl_lotte_ticketing(chrome_driver)  # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
            # ------------------------------

            chrome_driver.quit()
            server.stop()

        except Exception as e:
            self.logger.error('LOTTE 크롤링 중 오류발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e

    # ===================================================================================

    # ===================================================================================
    def uplodding(self):
        try:
            self.logger.info('')
            self.logger.info('')
            self.logger.info('### LOTTE 서버 전송 시작 ###')

            for key in self.dicCinemas.keys():  # dicCinemas의 모든 키들을 얻음
                self.dicCinemas[key] = self.dicCinemas[key][:-1]  # 마지막 '성공여부'는 삭제
                self.dicCinemas[key] = self.dicCinemas[key][:-1]  # 마지막 'link'는 삭제

            url = 'http://www.mtns7.co.kr/totalscore/upload_lotte.php'  # POST 요청을 보낼 PHP 스크립트의 URL
            
            # self.dicMovieData = json.loads('{"12523": ["곤지암","공포(호러)","Y","20180328","만15세이상관람가",-1],"12900": ["미션 임파서블: 폴아웃","액션","Y","20180725","만15세이상관람가",-1],"17630": ["랑종","공포(호러)","Y","20210714","청소년관람불가",-1],"17726": ["여름날 우리","코미디","Y","20230628","만12세이상관람가",-1],"19438": ["엘리멘탈","애니메이션","Y","20230614","전체관람가",-1],"19481": ["스즈메의 문단속","애니메이션","Y","20230308","만12세이상관람가",-1],"19586": ["아기공룡 둘리-얼음별 대모험","애니메이션","Y","20230524","전체관람가",-1],"19621": ["수라","다큐멘터리","Y","20230621","전체관람가",-1],"19667": ["거울 속 외딴 성","애니메이션","Y","20230412","만12세이상관람가",-1],"19764": ["포켓 몬스터 DP: 아르세우스 초극의 시공으로","애니메이션","Y","20230531","전체관람가",-1],"19775": ["스파이더맨: 어크로스 더 유니버스","애니메이션","Y","20230621","전체관람가",-1],"19776": ["가디언즈 오브 갤럭시: Volume 3","액션","Y","20230503","만12세이상관람가",-1],"19786": ["분노의 질주: 라이드 오어 다이","액션","Y","20230517","만15세이상관람가",-1],"19796": ["극장판 리틀 슈퍼맨 샘샘","애니메이션","Y","20230518","전체관람가",-1],"19803": ["범죄도시3","범죄","Y","20230531","만15세이상관람가",-1],"19832": ["파이어하트","애니메이션","Y","20230628","전체관람가",-1],"19850": ["트랜스포머: 비스트의 서막","액션","Y","20230606","만12세이상관람가",-1],"19864": ["귀공자","액션","Y","20230621","청소년관람불가",-1],"19869": ["라방","드라마","Y","20230628","청소년관람불가",-1],"19874": ["인어공주","뮤지컬","Y","20230524","전체관람가",-1],"19875": ["애스터로이드 시티","드라마","Y","20230628","만12세이상관람가",-1],"19882": ["206: 사라지지 않는","다큐멘터리","Y","20230621","만12세이상관람가",-1],"19888": ["하나님의 마음","드라마","Y","20230628","만12세이상관람가",-1],"19891": ["손","공포(호러)","Y","20230621","만15세이상관람가",-1],"19893": ["엽문의 시작","액션","Y","20230623","만15세이상관람가",-1],"19903": ["인드림","액션","Y","20230621","청소년관람불가",-1],"19907": ["플래시","액션","Y","20230614","만12세이상관람가",-1],"19909": ["엘리멘탈","2D","","","","19438"],"19940": ["슈가: 로드 투 디데이","다큐멘터리","Y","20230616","만12세이상관람가",-1],"19956": ["살롱 드 서울","드라마","Y","20230621","만15세이상관람가",-1],"19962": ["인디아나 존스: 운명의 다이얼","어드벤쳐","Y","20230628","만12세이상관람가",-1],"19969": ["나비효과","코미디","Y","20230622","만12세이상관람가",-1],"19976": ["룸 203","공포(호러)","Y","20230628","만15세이상관람가",-1]}')
            # self.dicCinemas = json.loads('{"200": ["Y",9,"씨네커플"],"300": ["Y",2,"샤롯데"],"930": ["Y",5,"수퍼 4D"],"940": ["Y",3,"수퍼플렉스"],"950": ["Y",10,"씨네비즈"],"960": ["Y",8,"씨네패밀리"],"980": ["Y",4,"수퍼 S"],"986": ["Y",7,"씨네컴포트(리클라이너)"],"988": ["Y",6,"컬러리움"],"1001": ["N",26,"에비뉴엘(명동)"],"1002": ["N",27,"영등포"],"1003": ["N",16,"노원"],"1004": ["N",14,"건대입구"],"1005": ["N",34,"홍대입구"],"1007": ["N",25,"신림"],"1008": ["N",32,"청량리"],"1009": ["N",15,"김포공항"],"1010": ["N",33,"합정"],"1012": ["N",20,"서울대입구"],"1013": ["N",11,"가산디지털"],"1014": ["N",28,"용산"],"1015": ["N",24,"신도림"],"1016": ["N",29,"월드타워"],"1017": ["N",18,"독산"],"1021": ["N",30,"은평(롯데몰)"],"1023": ["N",17,"도곡"],"1024": ["N",23,"신대방(구로디지털역)"],"2004": ["N",130,"부산본점"],"2006": ["N",133,"센텀시티"],"2007": ["N",126,"동래"],"2008": ["N",132,"서면(전포동)"],"2009": ["N",122,"광복"],"2010": ["N",127,"동부산아울렛"],"2011": ["N",136,"오투(부산대)"],"2012": ["N",125,"대영"],"3003": ["N",47,"부평"],"3004": ["N",60,"안산"],"3007": ["N",63,"안양(안양역)"],"3008": ["N",49,"부평역사"],"3010": ["N",75,"진접"],"3011": ["N",45,"부천(신중동역)"],"3012": ["N",54,"센트럴락"],"3017": ["N",44,"병점"],"3018": ["N",78,"평촌(범계역)"],"3020": ["N",38,"광주터미널"],"3021": ["N",42,"마석"],"3024": ["N",56,"수원(수원역)"],"3025": ["N",37,"광명아울렛"],"3026": ["N",39,"구리아울렛"],"3027": ["N",36,"광명(광명사거리)"],"3028": ["N",61,"안산고잔"],"3029": ["N",55,"송탄"],"3030": ["N",35,"광교아울렛"],"3031": ["N",51,"산본피트인"],"3032": ["N",64,"안양일번가"],"3033": ["N",70,"의정부민락"],"3034": ["N",76,"파주운정"],"3035": ["N",72,"인천아시아드"],"3036": ["N",81,"향남"],"3037": ["N",69,"위례"],"3038": ["N",73,"인천터미널"],"3039": ["N",67,"용인기흥"],"3040": ["N",68,"용인역북"],"3041": ["N",53,"성남중앙(신흥역)"],"3043": ["N",52,"서수원"],"3044": ["N",57,"수지"],"3045": ["N",50,"북수원(천천동)"],"3046": ["N",43,"별내"],"3047": ["N",77,"판교(창조경제밸리)"],"3048": ["N",40,"동탄"],"3049": ["N",59,"시흥장현"],"3050": ["N",48,"부평갈산"],"4002": ["N",83,"대전(백화점)"],"4004": ["N",88,"서청주(아울렛)"],"4005": ["N",89,"아산터미널"],"4006": ["N",85,"대전둔산(월평동)"],"4007": ["N",92,"청주용암"],"4008": ["N",86,"대전센트럴"],"4009": ["N",84,"대전관저"],"5001": ["N",137,"울산(백화점)"],"5002": ["N",141,"창원"],"5004": ["N",113,"성서"],"5005": ["N",110,"동성로"],"5006": ["N",108,"대구율하"],"5009": ["N",140,"진해"],"5011": ["N",124,"김해아울렛(장유)"],"5012": ["N",107,"대구광장"],"5013": ["N",106,"구미공단"],"5014": ["N",138,"울산성남"],"5015": ["N",123,"김해부원"],"5016": ["N",111,"상인"],"5017": ["N",139,"진주혁신(롯데몰)"],"6001": ["N",94,"광주(백화점)"],"6002": ["N",100,"전주(백화점)"],"6004": ["N",98,"수완(아울렛)"],"6006": ["N",102,"전주평화"],"6007": ["N",96,"군산나운"],"6009": ["N",97,"군산몰"],"6010": ["N",153,"제주연동"],"7002": ["N",146,"동해"],"7003": ["N",148,"원주무실"],"9010": ["N",13,"강동"],"9013": ["N",150,"서귀포"],"9036": ["N",142,"통영"],"9042": ["N",128,"마산(합성동)"],"9044": ["N",87,"서산"],"9047": ["N",103,"충장로"],"9054": ["N",46,"부천역"],"9056": ["N",19,"브로드웨이(신사)"],"9057": ["N",120,"프리미엄칠곡"],"9059": ["N",144,"프리미엄해운대(장산역)"],"9064": ["N",114,"영주"],"9065": ["N",95,"광주광산"],"9066": ["N",118,"프리미엄만경"],"9067": ["N",117,"프리미엄구미센트럴"],"9068": ["N",151,"제주삼화지구"],"9070": ["N",99,"익산모현"],"9071": ["N",152,"제주아라"],"9072": ["N",143,"프리미엄경남대"],"9074": ["N",119,"프리미엄안동"],"9075": ["N",79,"평택비전(뉴코아)"],"9077": ["N",65,"영종하늘도시"],"9078": ["N",93,"충주(모다아울렛)"],"9079": ["N",66,"오산(원동)"],"9080": ["N",112,"상주"],"9081": ["N",149,"춘천"],"9082": ["N",121,"거창"],"9083": ["N",31,"중랑"],"9084": ["N",131,"사천"],"9085": ["N",82,"당진"],"9087": ["N",74,"주엽"],"9088": ["N",58,"시화(정왕역)"],"9089": ["N",147,"속초"],"9090": ["N",104,"경주"],"9091": ["N",105,"경주황성"],"9092": ["N",129,"부산명지"],"9094": ["N",12,"가양"],"9095": ["N",41,"라페스타"],"9097": ["N",116,"포항"],"9098": ["N",115,"영천"],"9099": ["N",21,"수락산"],"9100": ["N",71,"인덕원"],"9101": ["N",90,"천안불당"],"9102": ["N",101,"전주송천"],"9103": ["N",134,"양산물금"],"9104": ["N",22,"수유"],"9105": ["N",135,"엠비씨네(진주)"],"9106": ["N",62,"안성"],"9107": ["N",109,"대구현풍"],"9108": ["N",145,"남원주"],"9111": ["N",80,"하남미사"],"9112": ["N",91,"천안청당"]}')
            # self.dicTickecting = json.loads('{"20230628": [["9098","영천",["909801","1관",102,[601,"영천","1관","22:30","24:59",102,102,"19775","스파이더맨: 어크로스 더 유니버스"],[601,"영천","1관","22:30","24:59",102,102,"19775","스파이더맨: 어크로스 더 유니버스"]],["909802","2관",102,[501,"영천","2관","21:35","23:42",98,102,"19864","귀공자"],[501,"영천","2관","21:35","23:42",98,102,"19864","귀공자"]],["909803","3관",102,[101,"영천","3관","20:30","23:14",83,102,"19962","인디아나 존스: 운명의 다이얼"],[101,"영천","3관","20:30","23:14",83,102,"19962","인디아나 존스: 운명의 다이얼"]],["909804","4관",102,[201,"영천","4관","22:20","25:04",101,102,"19962","인디아나 존스: 운명의 다이얼"],[201,"영천","4관","22:20","25:04",101,102,"19962","인디아나 존스: 운명의 다이얼"]],["909805","5관",102,[401,"영천","5관","20:00","21:55",86,102,"19803","범죄도시3"],[402,"영천","5관","22:05","24:00",102,102,"19803","범죄도시3"],[401,"영천","5관","20:00","21:55",86,102,"19803","범죄도시3"],[402,"영천","5관","22:05","24:00",102,102,"19803","범죄도시3"]],["909806","6관",102,[301,"영천","6관","21:25","24:09",99,102,"19962","인디아나 존스: 운명의 다이얼"],[301,"영천","6관","21:25","24:09",99,102,"19962","인디아나 존스: 운명의 다이얼"]]],["9097","포항",["909701","1관",91,[101,"포항","1관","20:40","22:39",65,91,"19438","엘리멘탈"],[102,"포항","1관","23:00","24:59",85,91,"19438","엘리멘탈"],[101,"포항","1관","20:40","22:39",65,91,"19438","엘리멘탈"],[102,"포항","1관","23:00","24:59",85,91,"19438","엘리멘탈"]],["909702","2관",72,[801,"포항","2관","20:20","22:25",62,72,"17726","여름날 우리"],[802,"포항","2관","22:40","24:45",71,72,"17726","여름날 우리"],[801,"포항","2관","20:20","22:25",62,72,"17726","여름날 우리"],[802,"포항","2관","22:40","24:45",71,72,"17726","여름날 우리"]],["909703","3관",82,[201,"포항","3관","21:40","23:39",75,82,"19438","엘리멘탈"],[201,"포항","3관","21:40","23:39",75,82,"19438","엘리멘탈"]],["909704","4관",89,[501,"포항","4관","20:00","21:55",65,89,"19803","범죄도시3"],[502,"포항","4관","22:10","24:05",87,89,"19803","범죄도시3"],[501,"포항","4관","20:00","21:55",65,89,"19803","범죄도시3"],[502,"포항","4관","22:10","24:05",87,89,"19803","범죄도시3"]],["909705","5관",71,[701,"포항","5관","23:30","25:37",69,71,"19864","귀공자"],[702,"포항","5관","21:40","23:20",68,71,"19869","라방"],[701,"포항","5관","23:30","25:37",69,71,"19864","귀공자"],[702,"포항","5관","21:40","23:20",68,71,"19869","라방"]],["909706","6관",98,[301,"포항","6관","22:30","25:14",97,98,"19962","인디아나 존스: 운명의 다이얼"],[301,"포항","6관","22:30","25:14",97,98,"19962","인디아나 존스: 운명의 다이얼"]],["909707","7관",93,[601,"포항","7관","20:50","22:45",86,93,"19803","범죄도시3"],[602,"포항","7관","23:10","25:05",92,93,"19803","범죄도시3"],[601,"포항","7관","20:50","22:45",86,93,"19803","범죄도시3"],[602,"포항","7관","23:10","25:05",92,93,"19803","범죄도시3"]],["909708","8관",116,[401,"포항","8관","21:00","23:44",96,116,"19962","인디아나 존스: 운명의 다이얼"],[401,"포항","8관","21:00","23:44",96,116,"19962","인디아나 존스: 운명의 다이얼"]]]],"20230629": [["9098","영천",["909801","1관",102,[101,"영천","1관","10:00","11:59",101,102,"19909","엘리멘탈"],[1001,"영천","1관","12:10","14:39",101,102,"19775","스파이더맨: 어크로스 더 유니버스"],[1002,"영천","1관","14:50","17:19",101,102,"19775","스파이더맨: 어크로스 더 유니버스"],[1003,"영천","1관","19:20","21:49",102,102,"19775","스파이더맨: 어크로스 더 유니버스"],[1301,"영천","1관","17:30","19:10",102,102,"19869","라방"],[1302,"영천","1관","22:00","23:40",102,102,"19869","라방"]],["909802","2관",102,[201,"영천","2관","17:05","19:04",98,102,"19438","엘리멘탈"],[901,"영천","2관","10:20","12:27",99,102,"19864","귀공자"],[902,"영천","2관","14:45","16:52",101,102,"19864","귀공자"],[903,"영천","2관","19:15","21:22",100,102,"19864","귀공자"],[904,"영천","2관","21:35","23:42",100,102,"19864","귀공자"],[1501,"영천","2관","12:40","14:35",101,102,"19875","애스터로이드 시티"]],["909803","3관",102,[401,"영천","3관","09:50","12:34",101,102,"19962","인디아나 존스: 운명의 다이얼"],[402,"영천","3관","14:40","17:24",101,102,"19962","인디아나 존스: 운명의 다이얼"],[403,"영천","3관","17:35","20:19",100,102,"19962","인디아나 존스: 운명의 다이얼"],[404,"영천","3관","20:30","23:14",100,102,"19962","인디아나 존스: 운명의 다이얼"],[1101,"영천","3관","12:45","14:27",101,102,"19832","파이어하트"]],["909804","4관",102,[501,"영천","4관","10:40","13:24",100,102,"19962","인디아나 존스: 운명의 다이얼"],[502,"영천","4관","13:35","16:19",100,102,"19962","인디아나 존스: 운명의 다이얼"],[503,"영천","4관","16:30","19:14",101,102,"19962","인디아나 존스: 운명의 다이얼"],[504,"영천","4관","19:25","22:09",98,102,"19962","인디아나 존스: 운명의 다이얼"],[505,"영천","4관","22:20","25:04",101,102,"19962","인디아나 존스: 운명의 다이얼"]],["909805","5관",102,[301,"영천","5관","12:00","13:59",102,102,"19909","엘리멘탈"],[701,"영천","5관","17:55","19:50",102,102,"19803","범죄도시3"],[702,"영천","5관","20:00","21:55",102,102,"19803","범죄도시3"],[703,"영천","5관","22:05","24:00",102,102,"19803","범죄도시3"],[1201,"영천","5관","16:00","17:42",101,102,"19832","파이어하트"],[1401,"영천","5관","10:10","11:50",100,102,"19869","라방"],[1402,"영천","5관","14:10","15:50",102,102,"19869","라방"]],["909806","6관",102,[601,"영천","6관","18:30","21:14",99,102,"19962","인디아나 존스: 운명의 다이얼"],[602,"영천","6관","21:25","24:09",101,102,"19962","인디아나 존스: 운명의 다이얼"],[801,"영천","6관","10:10","12:05",101,102,"19803","범죄도시3"],[802,"영천","6관","12:15","14:10",101,102,"19803","범죄도시3"],[803,"영천","6관","14:20","16:15",99,102,"19803","범죄도시3"],[804,"영천","6관","16:25","18:20",101,102,"19803","범죄도시3"]]],["9097","포항",["909701","1관",91,[101,"포항","1관","10:40","12:39",83,91,"19438","엘리멘탈"],[102,"포항","1관","13:10","15:09",85,91,"19438","엘리멘탈"],[103,"포항","1관","18:20","20:19",71,91,"19438","엘리멘탈"],[104,"포항","1관","20:40","22:39",87,91,"19438","엘리멘탈"],[105,"포항","1관","23:00","24:59",87,91,"19438","엘리멘탈"],[901,"포항","1관","15:30","17:59",87,91,"19775","스파이더맨: 어크로스 더 유니버스"]],["909702","2관",72,[1001,"포항","2관","13:45","15:27",71,72,"19832","파이어하트"],[1002,"포항","2관","15:40","17:22",69,72,"19832","파이어하트"],[1201,"포항","2관","11:30","13:35",70,72,"17726","여름날 우리"],[1202,"포항","2관","17:50","19:55",69,72,"17726","여름날 우리"],[1203,"포항","2관","20:20","22:25",68,72,"17726","여름날 우리"],[1204,"포항","2관","22:40","24:45",71,72,"17726","여름날 우리"]],["909703","3관",82,[201,"포항","3관","11:00","12:59",76,82,"19909","엘리멘탈"],[202,"포항","3관","13:50","15:49",78,82,"19438","엘리멘탈"],[203,"포항","3관","17:00","18:59",71,82,"19438","엘리멘탈"],[204,"포항","3관","19:20","21:19",78,82,"19438","엘리멘탈"],[205,"포항","3관","21:50","23:49",80,82,"19438","엘리멘탈"]],["909704","4관",89,[301,"포항","4관","14:40","16:39",86,89,"19438","엘리멘탈"],[601,"포항","4관","10:20","12:15",76,89,"19803","범죄도시3"],[602,"포항","4관","12:30","14:25",85,89,"19803","범죄도시3"],[603,"포항","4관","17:20","19:15",89,89,"19803","범죄도시3"],[604,"포항","4관","20:00","21:55",89,89,"19803","범죄도시3"],[605,"포항","4관","22:10","24:05",89,89,"19803","범죄도시3"]],["909705","5관",71,[801,"포항","5관","09:50","11:57",65,71,"19864","귀공자"],[802,"포항","5관","14:20","16:27",71,71,"19864","귀공자"],[803,"포항","5관","19:00","21:07",69,71,"19864","귀공자"],[804,"포항","5관","23:30","25:37",71,71,"19864","귀공자"],[1101,"포항","5관","12:20","14:00",68,71,"19869","라방"],[1102,"포항","5관","16:50","18:30",71,71,"19869","라방"],[1103,"포항","5관","21:30","23:10",71,71,"19869","라방"]],["909706","6관",98,[401,"포항","6관","16:00","17:59",96,98,"19438","엘리멘탈"],[402,"포항","6관","09:50","12:34",96,98,"19962","인디아나 존스: 운명의 다이얼"],[403,"포항","6관","12:50","15:34",98,98,"19962","인디아나 존스: 운명의 다이얼"],[404,"포항","6관","19:10","21:54",98,98,"19962","인디아나 존스: 운명의 다이얼"],[405,"포항","6관","22:20","25:04",98,98,"19962","인디아나 존스: 운명의 다이얼"]],["909707","7관",93,[701,"포항","7관","09:30","11:25",85,93,"19803","범죄도시3"],[702,"포항","7관","11:40","13:35",88,93,"19803","범죄도시3"],[703,"포항","7관","14:00","15:55",86,93,"19803","범죄도시3"],[704,"포항","7관","16:30","18:25",88,93,"19803","범죄도시3"],[705,"포항","7관","18:40","20:35",90,93,"19803","범죄도시3"],[706,"포항","7관","21:00","22:55",92,93,"19803","범죄도시3"],[707,"포항","7관","23:10","25:05",90,93,"19803","범죄도시3"]],["909708","8관",116,[501,"포항","8관","09:00","11:44",107,116,"19962","인디아나 존스: 운명의 다이얼"],[502,"포항","8관","12:00","14:44",111,116,"19962","인디아나 존스: 운명의 다이얼"],[503,"포항","8관","15:00","17:44",106,116,"19962","인디아나 존스: 운명의 다이얼"],[504,"포항","8관","18:00","20:44",109,116,"19962","인디아나 존스: 운명의 다이얼"],[505,"포항","8관","21:00","23:44",111,116,"19962","인디아나 존스: 운명의 다이얼"]]]]}')

            # self.logger.error(json.dumps(self.dicMovieData)) 
            # self.logger.error(json.dumps(self.dicCinemas)) 
            # self.logger.error(json.dumps(self.dicTickecting)) 

            data = {  # POST 데이터
                'moviedata': str(self.dicMovieData),        
                'cinemas': str(self.dicCinemas),
                
                'ticketingdata': str({}), # 이제 안씀
                'tickecting': str(self.dicTickecting)
            }
            response = requests.post(url, data=data)  # POST 요청 보내기
            print('[', response.text, ']')  # 응답 결과 출력

            self.logger.info('### LOTTE 서버 전송 종료 ###')

        except Exception as e:
            self.logger.error('LOTTE 전송 중 오류 발생!')
            self.logger.error(f'오류 내용! {e}')
            self.logger.error(f'{traceback.print_exc()}')
            raise e
        pass
    # ===================================================================================


# end of [class CrawlLotte(Crawl):]


# ###################################################################################
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

    logger_lotte = get_logger('lotte')

    crawlLotte = CrawlLotte(logger_lotte, dateRage)  # Lotte
    crawlLotte.crawling()
    crawlLotte.uplodding()

    clean_logger('lotte')

# ###################################################################################
