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

class CrawlLotte(Crawl):

    # -----------------------------------------------------------------------------------
    def __init__(self, is_prn_console, log_lotte, date_rage):

        self.dateRage = date_rage

        self.logger = log_lotte  # 파이션 로그
        self.isPrnConsole = is_prn_console  # 출력여부

        self.dicMovieData = {}  # 영화데이터 정보
        self.dicCinemas = {}  # 극장 코드 정보
        self.dicMovies = {}  # 영화 코드 정보

        self.dicTicketingData = {}  # 티켓팅 정보
    # -----------------------------------------------------------------------------------

    def crawling(self):
        try:
            #self.__crawl_lotte_boxoffice()  # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
            #self.__crawl_lotte_cinema()  # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
            self.__crawl_lotte_ticketingdata()  # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData1)
            
            
        except Exception as e:
            self.logger.error('LOTTE 크롤링 중 오류발생!')
            raise e

    #

    # ---------------------------------------------------------------------------------------------------------------------
    # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
    #
    def __crawl_lotte_ticketingdata(self):

        self.logger.info('')
        self.logger.info('### 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. ###')

        # https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1004

        # browsermob-proxy 서버 시작
        server_path = 'C://Crawlling2//browsermob-proxy-2.1.4//bin//browsermob-proxy.bat'
        server = Server(server_path)
        server.start()

        # 프록시 생성 및 WebDriver에 프록시 사용 설정
        proxy = server.create_proxy()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
        chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
        chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
        #chrome_options.add_argument('--no-proxy-server')  # 프록시 서버 비활성화 옵션
        driver = webdriver.Chrome(options=chrome_options)

        # 요청 캡처 활성화
        proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})
        
        '''
        for key, value in self.dicCinemas.items():
            if value[0] == 'N':
                self.logger.info(f'{value[0]}/{value[2]} ({key}) : URL {value[3]}')
                driver.get(value[3]) # 웹사이트로 이동
        '''        
        driver.get('https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1013')
        
        time.sleep(1) #driver.implicitly_wait(3) # 3초 대기

        html = driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
        soup = BeautifulSoup(html, 'html.parser')
        tags1 = soup.select('div > div > div > ul > div > div > div > li', class_='item')
        
        current_year = datetime.now().year
        month = ''
        day = ''

        for tag1 in tags1:  
            
            if (tag2 := tag1.select_one('a.date:not(.disabled)')) is not None:

                print('tag1 <~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                print(tag1)

                strong_tag_m = tag1.select_one('strong.month')
                strong_tag_d = tag1.select_one('strong:not([class])')

                if strong_tag_m is not None:
                    month = strong_tag_m.text.replace('월','').zfill(2)
                if strong_tag_d is not None:
                    day = strong_tag_d.text.zfill(2)

                if month == '01':
                    current_year += 1

                print(f'{current_year}-{month}-{day}')

                print('tag1 >~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                    
        # 캡처된 요청 가져오기
        har = proxy.har
        entries = har['log']['entries']

        # 각 요청의 세부 정보 출력
        for entry in entries:
            request = entry['request']
            response = entry['response']
            
            if request['url'] == "https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx":
                                        
                print(request['url'])                        
                #print(request['method'])    
                postData = request['postData']
                content = response['content']
                text = content['text']


                #print('headers < ************************')
                #print(((str(request['headers']).replace("\"", "`")).replace("'", "\"")).replace("`", "'"))
                #print('headers > ************************')                       
                
                print('postData < ************************')                        
                lines = postData['text'].split('\r\n')
                print(lines[3])
                json_obj = json.loads(lines[3])
                jsonpath_expr = parse('playDate').find(json_obj)
                if (playDate := jsonpath_expr[0].value if jsonpath_expr else None):
                    print(f'playDate = {playDate}')
                print('postData > ************************')

                
                #print(' Json < ************************')                        
                #print(text)
                #print(' Json > ************************')
                
                # JSON 파싱
                json_obj = json.loads(text)

                jsonpath_expr = parse('PlayDates.ItemCount').find(json_obj)
                if (ItemCount := jsonpath_expr[0].value if jsonpath_expr else None):
                    if self.isPrnConsole:  # ################
                        self.logger.info('-------------------------------------')
                        self.logger.info('상영일수')
                        self.logger.info('-------------------------------------')
                        self.logger.info(ItemCount)

                jsonpath_expr = parse('PlayDates.Items').find(json_obj)
                if len(jsonpath_expr) == 1:
                    if self.isPrnConsole:  # ################
                        self.logger.info('-------------------------------------')
                        self.logger.info('상영일')
                        self.logger.info('-------------------------------------')

                    for PlayDate in jsonpath_expr[0].value:
                        PlayDate = str(PlayDate['PlayDate'])

                        if self.isPrnConsole:  # ################
                            self.logger.info(PlayDate)

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

                        if self.isPrnConsole:  # ################
                            self.logger.info(f'{screenid} = {screennamekr},{totalseatcount}')

                    if self.isPrnConsole:  # ################
                        self.logger.info('-------------------------------------')
                        self.logger.info('일자, no, 티켓코드, 극장명, 상영관그룹명, 상영관명, 영화명, 영화구분, 개봉일, 시작시간, 끝시간, 예약좌석수, 총좌석수')
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
                        playdt = PlayDate['PlayDt']  # 상영일자
                        playdt = playdt[0:4] + playdt[5:7] + playdt[8:10]  # 상영일자(조정)
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
                        #dicTime[degreeNo] = [starttime, endtime, bookingseatcount, moviecode, self.dicMovies[moviecode][0], self.dicMovies[moviecode][1], self.dicMovies[moviecode][2]]
                        dicTime[degreeNo] = [starttime, endtime, bookingseatcount, moviecode]
                        

                        if self.isPrnConsole:  # ################
                            ticket_count += 1
                            #self.logger.info('{} : {},{},{},{},{},{},{},{},{},{},{}~{},{},{}'.format(today, (screenNo * 100) + degreeNo, dicCinema, cinemanamekr, sequencenogroupnamekr, screennamekr, moviecode, self.dicMovies[moviecode][0], self.dicMovies[moviecode][1], self.dicMovies[moviecode][2], playdt, starttime, endtime, bookingseatcount, totalseatcount))
                            self.logger.info('{},{},{},{},{},{},{}~{},{},{}'.format((screenNo * 100) + degreeNo,  cinemanamekr, sequencenogroupnamekr, screennamekr, moviecode,  playdt, starttime, endtime, bookingseatcount, totalseatcount))

                    if screenid_old is not None:
                        dicScreen[screenid].append(dicTime)

                    #self.dicTeather[self.dicCinema] = [dicScreen]

            #

        driver.quit()

    # -------------------------------------------------------------------------------------------------


    # ----------------------------------------------------------------------------------------------------------------------------
    # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
    #
    def __crawl_lotte_boxoffice(self):
        self.logger.info('')
        self.logger.info('### 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. ###')

        movie_count = 0

        # browsermob-proxy 서버 시작
        server_path = 'C://Crawlling2//browsermob-proxy-2.1.4//bin//browsermob-proxy.bat'
        server = Server(server_path)
        server.start()

        # 프록시 생성 및 WebDriver에 프록시 사용 설정
        proxy = server.create_proxy()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
        chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
        chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
        #chrome_options.add_argument('--no-proxy-server')  # 프록시 서버 비활성화 옵션
        driver = webdriver.Chrome(options=chrome_options)

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

        # WebDriver 종료 및 프록시 서버 중지
        driver.quit()
        server.stop()

    # -------------------------------------------------------------------------------------------------
        
    # -------------------------------------------------------------------------------------------------
    # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
    #
    def __crawl_lotte_cinema(self):
        
        self.logger.info('')
        self.logger.info('### 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. ###')

        def parse_links(html):
            
            soup = BeautifulSoup(html, 'html.parser')
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

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
        chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시

        driver = webdriver.Chrome(options=chrome_options)  

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

        driver.quit()

    # -------------------------------------------------------------------------------------------------


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
    #
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

    logger_lotte = get_logger('lotte')

    crawlLotte = CrawlLotte(True, logger_lotte, dateRage)  # Lotte
    crawlLotte.crawling()
    #crawlLotte.uplodding()

    clean_logger('lotte')
#


