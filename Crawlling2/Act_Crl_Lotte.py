"""

"""
from Act_Crl_Supper import ActCrlSupper
from Act_Tol_Logger import get_logger, clear_logger

import platform
import os
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

        self.dicMovies = {}      # 영화 코드 정보
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
        # 영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)
        #
        def _crawlingLotte_ticketing(chm_driver):

            self.logger.info('==========================================================================================================================')
            self.logger.info('영화관 (https://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData)')
            self.logger.info('--------------------------------------------------------------------------------------------------------------------------')
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
