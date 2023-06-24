import sys 
import json
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from selenium import webdriver
from browsermobproxy import Server # pip install browsermob-proxy
import time
from selenium.webdriver.chrome.options import Options
from Crawl_Supper import Crawl
from jsonpath_rw import parse  # pip install jsonpath-rw      https://pypi.python.org/pypi/jsonpath-rw
import requests
from urllib.parse import parse_qs, urlparse
from datetime import datetime
from Crawling_Logger import get_logger, clean_logger

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib3  # pip install urllib3


class CrawlLotte(Crawl):

    # ===================================================================================
    def __init__(self, is_prn_console, log_lotte, date_rage):

        self.dateRage = date_rage
        self.http = urllib3.PoolManager()

        self.logger = log_lotte  # 파이션 로그
        self.isPrnConsole = is_prn_console  # 출력여부

        self.dicMovieData = {}  # 영화데이터 정보
        self.dicCinemas = {}  # 극장 코드 정보
        self.dicMovies = {}  # 영화 코드 정보

        self.dicTicketingData = {}  # 티켓팅 정보
    # ===================================================================================



    # ===================================================================================
    def crawling(self):        

        # -----------------------------------------------------------------------------------
        #  영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. ###
        #     
        def _crawl_lotte_boxoffice(self):

            self.logger.info('')
            self.logger.info('### 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. ###')

            movie_count = 0

            # 요청 캡처 활성화
            proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})
            
            driver.get("https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1") # 웹사이트로 이동
            driver.implicitly_wait(3) # 3초 대기

            # 캡처된 요청 가져오기
            har = proxy.har
            entries = har['log']['entries']

            # 각 요청의 세부 정보 출력
            for entry in entries:
                request = entry['request']
                response = entry['response']
                
                if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx":
                                            
                    #print(request['url'])
                    #print(request['method'])    
                    
                    
                    #print('------------------------')
                    #print(request['headers'])

                    content = response['content']
                    text = content['text']    
                    #print('------------------------')
                    #print(f"MovieData.aspx json : {text}")           

                    if self.isPrnConsole:  # ################
                        self.logger.info('-------------------------------------')
                        self.logger.info('no, 코드, 영화명, 장르, 예매, 개봉일, 관람등급')
                        self.logger.info('-------------------------------------')

                    # JSON 파싱
                    json_obj = json.loads(text)

                    jsonpath_expr = parse('Movies.Items[*]')

                    for match in jsonpath_expr.find(json_obj):
                        representationmoviecode = str(match.value['RepresentationMovieCode'])
                        movienamekr = str(match.value['MovieNameKR']).strip()
                        moviegenrename = str(match.value['MovieGenreName'])
                        bookingyn = str(match.value['BookingYN'])
                        releasedate = str(match.value['ReleaseDate'])
                        releasedate = releasedate[0:4] + releasedate[5:7] + releasedate[8:10]
                        viewgradenameus = str(match.value['ViewGradeNameUS'])

                        if movienamekr == '' or movienamekr == 'AD': continue

                        self.dicMovieData[representationmoviecode] = [movienamekr, moviegenrename, bookingyn, releasedate, viewgradenameus, -1]  # 영화데이터 정보

                        if self.isPrnConsole:  # ################
                            movie_count += 1
                            self.logger.info(f'{movie_count} : {representationmoviecode},{movienamekr},{moviegenrename},{bookingyn},{releasedate},{viewgradenameus}')
                        #
                    #
                #
        # end of [def _crawl_lotte_boxoffice(self):]


        # -----------------------------------------------------------------------------------
        #  영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다.  ###
        #         

        def _crawl_lotte_cinema(self):
            
            self.logger.info('')
            self.logger.info('### 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. ###')

            def parse_links(tagLst):
                
                soup = BeautifulSoup(tagLst, 'html.parser')
                a_tags = soup.find_all('a')
                
                parsed_links = []
                
                for a_tag in a_tags:
                    link = a_tag['href']
                    parsed_url = urlparse(link)
                    params = parse_qs(parsed_url.query)
                    
                    url = link.split('?')[0]
                    query_params = {key: value[0] for key, value in params.items()}
                    text = a_tag.text.replace("\n", "").strip()
                    
                    parsed_link = {'url': url, 'query_params': query_params, 'text': text, 'link': link }                
                    parsed_links.append(parsed_link)
                    # print("URL:", parsed_link['url'],", Query Params:", parsed_link['query_params'],", Text:", parsed_link['text'], link:", parsed_link['link'])
                    
                return parsed_links
            
            # ----------------- end of [ def parse_links(html): ]

            driver.get('https://www.lottecinema.co.kr/NLCHS')
            driver.implicitly_wait(3)

            html = driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
            soup = BeautifulSoup(html, "html.parser")

            if (tag1 := soup.select_one("#nav > ul > li:nth-child(3) > div > ul")): # 메인 메뉴의 '영화관' 하위 메뉴 탐색
                
                tagLst = ''
                tags2 = tag1.select('li > a:not([href="#"])')
                for tag2 in tags2:  # print(tag2)
                    tagLst += tag2.prettify()
                
                parsed_links = parse_links(tagLst)

                if self.isPrnConsole:  # ################
                    self.logger.info('-------------------------------------')
                    self.logger.info(' 코드, 스페셜관, 정렬일련번호, 극장명')
                    self.logger.info('-------------------------------------')


                sortsequence = 0
                for parsed_link in parsed_links:
                    print(parsed_link)
                    if parsed_link['url']=='https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema': # 극장(스페셜괌)정보저장
                        sortsequence = sortsequence + 1
                        self.dicCinemas[parsed_link['query_params']['screendivcd']] = ['Y', sortsequence, parsed_link['text'], parsed_link['link']] 

                    if parsed_link['url'] == 'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail': # 극장(일반)정보저장
                        sortsequence = sortsequence + 1
                        self.dicCinemas[parsed_link['query_params']['cinemaID']] = ['N', sortsequence, parsed_link['text'], parsed_link['link']] 

                if self.isPrnConsole:  # ################            
                    for key, value in self.dicCinemas.items():
                        self.logger.info('{} : {},{},{},{}'.format(key, value[0], value[1], value[2], value[3]))

        # end of [def _crawl_lotte_cinema(self):]



        # -----------------------------------------------------------------------------------
        # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. ###
        #
        def _crawl_lotte_ticketingdata(self):

            self.logger.info('')
            self.logger.info('### 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. ###')

            dicTeather = {}

            '''
            for key, value in self.dicCinemas.items(): # 전체 극장을 순회한다.
                
                if value[0] == 'Y': # 스페셜 극장은 빠진다.
                    continue
                self.logger.info(f'{value[0]}/{value[2]} ({key}) : URL {value[3]}')
                
                url = value[3] # 웹사이트로 이동
                '''
            #url = 'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1004'
            #url = 'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1004'
            url = 'https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1013'
            driver.get(url)
            
            html = driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
            soup = BeautifulSoup(html, 'html.parser')

            time_table_xpath = '//*[@id="contents"]/div[1]/div[1]/h3'
            elements = driver.find_elements(By.XPATH, f'{time_table_xpath}')
            theatherNm = elements[0].text

            if (tag1 := soup.select_one("ul > li")): # 메인 메뉴의 '영화관' 하위 메뉴 탐색                        
                elements = driver.find_elements(By.XPATH, '//*[text()="확인"]') # 난데없는 팝업창이 나오면 '확인'을 누를다... 
                if len(elements) > 0:
                    element = elements[0]
                    element.click()
                    time.sleep(1)                           
            # 

            # 전체 상영일수를 구한다. 
            time_table_xpath = '//*[@id="timeTable"]/div[1]/div/ul/div[1]/div'
            elements = driver.find_elements(By.XPATH, f'{time_table_xpath}/div')
            count = len(elements)  
            
            nMin = 1000
            nMax = -1
            for i in range(1, (count+1)): # 전체 상영일 순환

                element = driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a') # 일자 선택 버튼
                if 'disabled' in element.get_attribute('class'):  # 무효한 상영일을 거른다.
                    continue
                else:
                    if i < nMin: 
                        nMin = i
                    if i > nMax: 
                        nMax = i

            for i in range(nMin, (nMax+1)): # 전체 상영일 순환

                element = driver.find_element(By.XPATH, f'//*[@id="timeTable"]/div[1]/div/ul/div[1]/div/div[{i}]/li/a') # 일자 선택 버튼
                if 'disabled' in element.get_attribute('class'):  # 무효한 상영일을 거른다.
                    break
                
                # 복수 실행을 위해 캡처된 요청 초기화
                proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})

                element.click() # 상영일 누르기..!!!
                time.sleep(1)

                # 캡처된 요청 가져오기
                har = proxy.har
                entries = har['log']['entries']

                # 각 요청의 세부 정보 출력
                for entry in entries:
                    request = entry['request']
                    response = entry['response']
        
                    if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":
                        postData = request['postData']

                        lines = postData['text'].split('\r\n')
                        json_obj = json.loads(lines[3])
                        jsonpath_expr = parse('playDate').find(json_obj)
                        playDate = jsonpath_expr[0].value if jsonpath_expr else None

                        text = response['content']['text']

                        # JSON 파싱
                        json_obj = json.loads(text)

                        jsonpath_expr = parse('PlayDates.ItemCount').find(json_obj)
                        ItemCount = jsonpath_expr[0].value if jsonpath_expr else None

                        jsonpath_expr = parse('PlayDates.Items').find(json_obj)
                        if len(jsonpath_expr) == 1:
                            if self.isPrnConsole:  # ################
                                self.logger.info('-------------------------------------')
                                self.logger.info('상영일 ({ItemCount})')
                                self.logger.info('-------------------------------------')

                            for PlayDate in jsonpath_expr[0].value:
                                PlayDate = str(PlayDate['PlayDate'])

                                if self.isPrnConsole:  # ################
                                    self.logger.info(PlayDate)
                        #            

                        jsonpath_expr = parse('PlaySeqs.Items').find(json_obj)
                        if len(jsonpath_expr) == 1:
                            
                            ticket_count = 0

                            # dicScreen를 먼저구하기 위해 2번 돈다.
                            dicScreen = {}

                            for PlayDate in jsonpath_expr[0].value:
                                screenid = str(PlayDate['ScreenID'])  # 상영관 코드
                                screennamekr = PlayDate['ScreenNameKR']  # 상영관명
                                totalseatcount = PlayDate['TotalSeatCount']  # 총좌석수

                                cinemaid = str(PlayDate['CinemaID'])  # 극장코드 (월드타워)
                                screendivnamekr = PlayDate['ScreenDivisionNameKR']  # 부상영관명 (씨네패밀리)
                                screendivcode = str(PlayDate['ScreenDivisionCode'])  # 부상영관코드 (960)

                                if cinemaid == "1016" and screendivcode == "960":  # 월드타워 점 씨네패밀리 관 인경우
                                    screenid = screenid+"*"
                                    screennamekr = screennamekr + " " + screendivnamekr

                                dicScreen[screenid] = [screennamekr, totalseatcount]
                                
                            # end of [for PlayDate in jsonpath_expr[0].value:]

                            if self.isPrnConsole:  # ################
                                self.logger.info('-------------------------------------')
                                self.logger.info('관(코드), 좌석수')
                                self.logger.info('-------------------------------------')
                            for key, value in dicScreen.items():
                                if self.isPrnConsole:  # ################
                                    self.logger.info(f'{value[0]}({key}), {value[1]}석')

                            if self.isPrnConsole:  # ################
                                self.logger.info('-------------------------------------')
                                self.logger.info('극장명(일자), no, 티켓코드, 상영관그룹명, 상영관명, 영화명, 영화구분, 개봉일, 시작시간~끝시간, 예약좌석수/총좌석수')
                                self.logger.info('-------------------------------------')
                            
                            screenid_old = None
                            screenNo = 0
                            degreeNo = 0
                            for PlayDate in jsonpath_expr[0].value:
                                cinemanamekr = PlayDate['CinemaNameKR']  # 극장명
                                sequencenogroupnamekr = PlayDate['SequenceNoGroupNameKR']  # 상영관그룹명
                                screenid = str(PlayDate['ScreenID'])  # 상영관 코드
                                screennamekr = PlayDate['ScreenNameKR']  # 상영관명
                                moviecode = PlayDate['MovieCode']  # 영화코드 [영화명 + 필름종류 + 더빙/자막]
                                bookingseatcount = PlayDate['BookingSeatCount']  # 예약좌석수
                                totalseatcount = PlayDate['TotalSeatCount']  # 총좌석수
                                playdate_ = PlayDate['PlayDt']  # 상영일자
                                playdt = playdate_[0:4] + playdate_[5:7] + playdate_[8:10]  # 상영일자(조정)
                                starttime = PlayDate['StartTime']  # 상영시간(시작)
                                endtime = PlayDate['EndTime']  # 상영시간(끝)

                                cinemaid = str(PlayDate['CinemaID'])  # 극장코드 (월드타워)
                                screendivnamekr = PlayDate['ScreenDivisionNameKR']  # 부상영관명 (씨네패밀리)
                                screendivcode = str(PlayDate['ScreenDivisionCode'])  # 부상영관코드 (960)

                                if cinemaid == "1016" and screendivcode == "960":  # 월드타워 점 씨네패밀리 관 인경우
                                    screenid = screenid + "*"
                                    screennamekr = screennamekr + " " + screendivnamekr
                                
                                #print(self.dicMovies[moviecode][1]+':'+self.dicMovies[moviecode][0])

                                if screenid_old != screenid:

                                    if screenid_old is not None:
                                        dicScreen[screenid_old].append(dicTime)
                                    #

                                    screenNo += 1
                                    degreeNo = 0
                                    dicTime = {}
                                    screenid_old = screenid
                                #

                                degreeNo += 1
                                #dicTime[(screenNo * 100) + degreeNo] = [starttime, endtime, bookingseatcount, moviecode, self.dicMovies[moviecode][1], self.dicMovies[moviecode][2]]
                                dicTime[(screenNo * 100) + degreeNo] = [starttime, endtime, bookingseatcount, moviecode]
                                

                                if self.isPrnConsole:  # ################
                                    ticket_count += 1
                                    #self.logger.info('{}({}) {},{},{},{},{},{},{},{},{},{}~{},({}/{})'.format(theatherNm, today, (screenNo * 100) + degreeNo, dicCinema, theatherNmsequencenogroupnamekr, screennamekr, moviecode, self.dicMovies[moviecode][0], self.dicMovies[moviecode][1], self.dicMovies[moviecode][2], playdt, starttime, endtime, bookingseatcount, totalseatcount))
                                    self.logger.info('{}({}) {},{},{},{},{},{}~{},({}/{})'.format(theatherNm, playdate_, (screenNo * 100) + degreeNo,  sequencenogroupnamekr, screennamekr, moviecode,  playdt, starttime, endtime, bookingseatcount, totalseatcount))

                            # end of [for PlayDate in jsonpath_expr[0].value:]

                            if screenid_old is not None:
                                dicScreen[screenid].append(dicTime)

                            dicTeather['1013'] = [dicScreen]

                        # end of [ if len(jsonpath_expr = parse('PlaySeqs.Items').find(json_obj)) == 1:]
                    # end of [if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":]

                # end of [for entry in entries:] 

                self.dicTicketingData[playDate[0:4] + playDate[5:7] + playDate[8:10]] = [dicTeather]
            # end of [for i in range(1, (count+1)): # 전체 상영일 순환]
            '''
            # end of [for key, value in self.dicCinemas.items(): # 전체 극장을 순회한다.]
            '''            
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
            driver = webdriver.Chrome(options=chrome_options)

            # ------------------------------
            #_crawl_lotte_boxoffice(self)      # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
            #_crawl_lotte_cinema(self)         # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
            _crawl_lotte_ticketingdata(self)  # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData1)
            # ------------------------------
            
            driver.quit()
            server.stop()
            
        except Exception as e:
            self.logger.error('LOTTE 크롤링 중 오류발생!')
            raise e
    # ===================================================================================

    # ===================================================================================
    def uplodding(self):
        try:
            self.logger.info('')
            self.logger.info('### LOTTE 서버 전송 시작 ###')

            for key in self.dicCinemas.keys(): # dicCinemas의 모든 키들을 얻음
                self.dicCinemas[key] = self.dicCinemas[key][:-1] # 마지막 'link'는 삭제

            fields = {
                "moviedata": str(self.dicMovieData),
                "cinemas": str(self.dicCinemas),
                "ticketingdata": str(self.dicTicketingData)
            }
            url = 'http://www.mtns7.co.kr/totalscore/upload_lotte.php'

            r = self.http.request('POST', url, fields)
            data = r.data.decode('utf-8')

            print('[', data, ']')

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

    crawlLotte = CrawlLotte(True, logger_lotte, dateRage)  # Lotte
    crawlLotte.crawling()
    crawlLotte.uplodding()

    clean_logger('lotte')

# ###################################################################################


