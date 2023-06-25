import sys
import json
import time
import urllib3  # pip install urllib3
import requests

from bs4 import BeautifulSoup  # pip install beautifulsoup4
from browsermobproxy import Server  # pip install browsermob-proxy
from jsonpath_rw import parse  # pip install jsonpath-rw      https://pypi.python.org/pypi/jsonpath-rw
from urllib.parse import parse_qs, urlparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait

from Crawl_Supper import Crawl
from Crawling_Logger import get_logger, clean_logger


class CrawlLotte(Crawl):

    # ===================================================================================
    def __init__(self, log_lotte, date_rage):

        self.dateRage = date_rage
        self.http = urllib3.PoolManager()

        self.logger = log_lotte  # 파이션 로그

        self.dicMovieData = {}  # 영화데이터 정보
        self.dicCinemas = {}  # 극장 코드 정보
        self.dicMovies = {}  # 영화 코드 정보

        self.dicTicketingData = {}  # 티켓팅 정보

    # ===================================================================================

    # ===================================================================================
    def crawling(self):

        # -----------------------------------------------------------------------------------
        #  영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
        #
        def _crawl_lotte_boxoffice(chm_driver):

            self.logger.info('=======================================================================================================================')
            self.logger.info('영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)')
            self.logger.info('-----------------------------------------------------------------------------------------------------------------------')

            movie_count = 0

            proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 요청 캡처 활성화

            chm_driver.get("https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1")  # 웹사이트로 이동
            chm_driver.implicitly_wait(3)  # 3초 대기

            for entry in proxy.har['log']['entries']:  # 각 캡처된 요청의 세부 정보 출력

                request = entry['request']
                response = entry['response']

                if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx":

                    self.logger.info('-------------------------------------------------------------------------------')
                    self.logger.info('no, 코드, 영화명, 장르, 예매, 개봉일, 관람등급')
                    self.logger.info('-------------------------------------------------------------------------------')

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

                        movie_count += 1
                        self.logger.info(f'{movie_count} : {representationmoviecode},{movienamekr},{moviegenrename},{bookingyn},{releasedate},{viewgradenameus}')
                    #

                # end of [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx": ]
            # end of [for entry in proxy.har['log']['entries']:  # 각 캡처된 요청의 세부 정보 출력 ]

        # end of [def _crawl_lotte_boxoffice(self): ]

        # -----------------------------------------------------------------------------------
        #  영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
        #
        def _crawl_lotte_cinema(chm_driver):

            self.logger.info('=========================================================================================')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)')
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
            chm_driver.implicitly_wait(3)

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
                    if parsed_link['url'] == 'https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema':  # 극장(스페셜괌)정보저장
                        sortsequence = sortsequence + 1
                        self.dicCinemas[parsed_link['query_params']['screendivcd']] = ['Y', sortsequence, parsed_link['text'], parsed_link['link'], '']

                    if parsed_link['url'] == 'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail':  # 극장(일반)정보저장

                        if parsed_link['query_params']['cinemaID'] != '1017':  # --------------------------------------------------------------- 디버깅용
                            continue
                        sortsequence = sortsequence + 1
                        self.dicCinemas[parsed_link['query_params']['cinemaID']] = ['N', sortsequence, parsed_link['text'], parsed_link['link'], '']

                self.logger.info('-------------------------------------')
                self.logger.info(' 코드, 스페셜관, 정렬일련번호, 극장명')
                self.logger.info('-------------------------------------')

                for key, value in self.dicCinemas.items():
                    self.logger.info(f'{key} : {value[0]},{value[1]},{value[2]},{value[3]}')

        # end of [def _crawl_lotte_cinema(self):]

        # -----------------------------------------------------------------------------------
        # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
        #
        def _crawl_lotte_ticketingdata(chm_driverdriver):

            self.logger.info('==========================================================================================================================')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)')
            self.logger.info('--------------------------------------------------------------------------------------------------------------------------')

            def __read_cinemas():
                _dicTeather = {}
                movie_count = 0

                self.logger.info(f'{cn_value[0]}/{cn_value[2]} ({cn_key}) : URL {cn_value[3]}')

                url = cn_value[3]  # 웹사이트로 이동

                chm_driverdriver.get(url)

                html = chm_driverdriver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
                soup = BeautifulSoup(html, 'html.parser')

                theather_nm = chm_driverdriver.find_elements(By.XPATH, '//*[@id="contents"]/div[1]/div[1]/h3')[0].text

                if soup.select_one("ul > li"):  # 메인 메뉴의 '영화관' 하위 메뉴 탐색
                    button = chm_driverdriver.find_elements(By.XPATH, '//*[text()="확인"]')  # 난데없는 팝업창이 나오면 '확인'을 누를다...
                    if len(button) > 0:  # 버튼이 발견되면...
                        element = button[0]
                        element.click()
                        time.sleep(1)
                    #
                #

                button = chm_driverdriver.find_elements(By.XPATH, '//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div')  # 전체 상영일들을 구한다.

                arr_ablity_day = []

                for i in range(1, (len(button) + 1)):  # 전체 상영일 순환

                    element = chm_driverdriver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a')  # 일자 선택 버튼
                    parent_div = element.find_element(By.XPATH, '..').find_element(By.XPATH, '..')
                    parent_div_class = parent_div.get_attribute('class')

                    if 'disabled' in element.get_attribute('class'):
                        arr_ablity_day.append('F')  # 무효한 상영일
                    else:
                        arr_ablity_day.append('T')  # 유효한 상영일
                # end of [for i in range(1, (count+1)):  # 전체 상영일 순환 ]

                i = 0
                for ablityDay in arr_ablity_day:  # 유효한 상영일만 순환

                    i = i + 1

                    if ablityDay == 'F' or i > 14:  # 다음 페이지 문제로 인해 무조건 14 일자 까지만..
                        continue

                    proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})  # 복수 실행을 위해 캡처된 요청 초기화

                    div_act = chm_driverdriver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}][contains(@class, "active")]')
                    if not div_act:
                        chm_driverdriver.find_element(By.XPATH, '//*[@id="timeTable"]/div[1]/div/ul/div[2]/button[2]').click()  # 다음페이지 누르기..!!!
                        time.sleep(1)

                    chm_driverdriver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a').click()  # 상영일 누르기..!!!
                    time.sleep(1)

                    play_date = ''

                    for entry in proxy.har['log']['entries']:  # 캡처된 각 요청의 세부 정보 출력
                        request = entry['request']
                        response = entry['response']

                        if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":

                            json_obj = json.loads(request['postData']['text'].split('\r\n')[3])

                            jsonpath_expr = parse('playDate').find(json_obj)
                            play_date = jsonpath_expr[0].value if jsonpath_expr else None

                            # JSON 파싱
                            json_obj = json.loads(response['content']['text'])  ###########################

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

                                ticket_count = 0

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
                                for si_key, si_value in dic_screen.items():
                                    self.logger.info(f'{si_value[0]}({si_key}), {si_value[1]}석')

                                self.logger.info('--------------------------------------------------------------------------------')
                                self.logger.info(f'[{theather_nm}] 일자, 상영관, 시작시간~끝시간, 예약좌석수/총좌석수, 영화, 개봉일')
                                self.logger.info('--------------------------------------------------------------------------------')

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

                                        if screenid_old is not None:
                                            dic_screen[screenid_old].append(dicTime)

                                        screen_no += 1
                                        degree_no = 0
                                        dicTime = {}
                                        screenid_old = screenid
                                    #

                                    degree_no += 1
                                    dicTime[(screen_no * 100) + degree_no] = [starttime, endtime, bookingseatcount, moviecode, self.dicMovies[moviecode][1], self.dicMovies[moviecode][2]]

                                    ticket_count += 1

                                # end of [for PlayDate in jsonpath_expr[0].value:]

                                if screenid_old is not None:
                                    dic_screen[screenid].append(dicTime)

                                _dicTeather[cn_key] = [dic_screen]

                            # end of [ if len(jsonpath_expr = parse('PlaySeqs.Items').find(json_obj)) == 1:]
                        # end of [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":]
                    # end of [for entry in proxy.har['log']['entries']:  # 캡처된 각 요청의 세부 정보 출력]

                    self.dicTicketingData[play_date[0:4] + play_date[5:7] + play_date[8:10]] = [_dicTeather]

                    # break  # ------------------------------------- 디버깅용

                # end of [for i in range(nMin, (nMax+1)):  # 유효한 상영일만 순환  ]
            #

            for cn_key, cn_value in self.dicCinemas.items():  # 전체 극장을 순회한다.

                if cn_value[0] == 'Y':  # 스페셜 극장은 빠진다.
                    continue

                __read_cinemas()

            # end of [for key, value in self.dicCinemas.items():  # 전체 극장을 순회한다.]

        # end of [def _crawl_lotte_ticketingdata(self):]

        ############################################

        try:
            server_path = 'C://Crawlling2//browsermob-proxy-2.1.4//bin//browsermob-proxy.bat'
            server = Server(server_path)
            server.start()

            proxy = server.create_proxy()
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
            chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
            chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
            chrome_driver = webdriver.Chrome(options=chrome_options)

            # ------------------------------
            _crawl_lotte_boxoffice(chrome_driver)  # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
            _crawl_lotte_cinema(chrome_driver)  # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
            _crawl_lotte_ticketingdata(chrome_driver)  # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
            # ------------------------------

            chrome_driver.quit()
            server.stop()

        except Exception as e:
            self.logger.error('LOTTE 크롤링 중 오류발생!')
            raise e

    # ===================================================================================

    # ===================================================================================
    def uplodding(self):
        try:
            self.logger.info('')
            self.logger.info('')

            self.logger.info('### LOTTE 서버 전송 시작 ###')

            for key in self.dicCinemas.keys():  # dicCinemas의 모든 키들을 얻음
                self.dicCinemas[key] = self.dicCinemas[key][:-1]  # 마지막 'link'는 삭제

            url = 'http://www.mtns7.co.kr/totalscore/upload_lotte.php'  # POST 요청을 보낼 PHP 스크립트의 URL
            data = {  # POST 데이터
                'moviedata': str(self.dicMovieData),
                'cinemas': str(self.dicCinemas),
                'ticketingdata': str(self.dicTicketingData)
            }
            response = requests.post(url, data=data)  # POST 요청 보내기
            print('[', response.text, ']')  # 응답 결과 출력

            self.logger.info('### LOTTE 서버 전송 종료 ###')

        except Exception as e:
            self.logger.error('LOTTE 전송 중 오류 발생!')
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
