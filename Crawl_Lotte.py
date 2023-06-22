import sys 
import json
from bs4 import BeautifulSoup  # pip install beautifulsoup4
from selenium import webdriver
from browsermobproxy import Server # pip install browsermob-proxy
import time
from selenium.webdriver.chrome.options import Options
from Crawl_Supper import Crawl
from jsonpath_rw import parse  # pip install jsonpath-rw      https://pypi.python.org/pypi/jsonpath-rw

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
            self.__crawl_lotte_cinema()  # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
            '''
            self.__crawl_lotte_boxoffice()  # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
            self.__crawl_lotte_ticketingdata()  # 영화관 (http://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData1)
            '''
            
            
        except Exception as e:
            self.logger.error('LOTTE 크롤링 중 오류발생!')
            raise e

    #


    # -------------------------------------------------------------------------------------------------
    # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
    #
    def __crawl_lotte_cinema(self):

        self.logger.info('')
        self.logger.info('### 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. ###')

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
        chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시

        driver = webdriver.Chrome(options=chrome_options)  
        driver.implicitly_wait(3)

        driver.get('https://www.lottecinema.co.kr/NLCHS')
        driver.implicitly_wait(3)

        html = driver.page_source.replace('\n', '')  # 패이지 소스를 읽어온다.....
        soup = BeautifulSoup(html, "html.parser")

        tags1 = soup.select("#nav > ul > li:nth-child(3) > div > ul")
        for tag1 in tags1:
            tags2 = tag1.select('li > a[href="#"]')
            for tag2 in tags2:
                print('======================================================up')
                print(tag2)
            tags2 = tag1.select('li > a:not([href="#"])')
            for tag2 in tags2:
                print('======================================================dn')
                print(tag2)


        driver.quit()


        '''
        driver.find_element_by_xpath('//*[@class="btn-more-fontbold"]').click()  # '더보기' 클릭
        driver.implicitly_wait(3)

        time.sleep(self.delayTime)  # 초 단위 지연...

        

        soup = BeautifulSoup(html, "html.parser")
        '''

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

        # 웹사이트로 이동
        driver.get("https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1")

        # 5초 대기
        time.sleep(5)

        # 캡처된 요청 가져오기
        har = proxy.har
        entries = har['log']['entries']

        # 각 요청의 세부 정보 출력
        for entry in entries:
            request = entry['request']
            
            if request['url'] == "https://www.lottecinema.co.kr/LCWS/Movie/MovieData.aspx":
                                        
                print(request['url'])
                print(request['method'])    
                response = entry['response']
                
                print('------------------------')
                print(request['headers'])

                content = response['content']
                text = content['text']
                
                # JSON 파싱
                data = json.loads(text)

                if self.isPrnConsole:  # ################
                    self.logger.info('-------------------------------------')
                    self.logger.info('no, 코드, 영화명, 장르, 예매, 개봉일, 관람등급')
                    self.logger.info('-------------------------------------')

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

        movie_count = 0

    # -------------------------------------------------------------------------------------------------
        


    def uplodding(self):
        try:
            self.logger.info('')
            self.logger.info('### LOTTE 서버 전송 시작 ###')

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


