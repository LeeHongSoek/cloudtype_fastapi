import sys 
import json
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

'''

from urllib.parse import urlparse, parse_qs

url = "https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1013"

parsed_url = urlparse(url)

# URL의 구성 요소를 가져옵니다.
scheme = parsed_url.scheme
netloc = parsed_url.netloc
path = parsed_url.path
query = parsed_url.query

# 쿼리 문자열을 파싱하여 딕셔너리 형태로 가져옵니다.
query_params = parse_qs(query)

# 파싱된 결과를 출력합니다.
print("Scheme:", scheme)
print("Netloc:", netloc)
print("Path:", path)
print("Query Params:", query_params)


Scheme: https
Netloc: www.lottecinema.co.kr
Path: /NLCHS/Cinema/Detail
Query Params: {'divisionCode': ['1'], 'detailDivisionCode': ['1'], 'cinemaID': ['1013']}



'''
# -------------------------------------------------------------------------------------------------
# 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
#
def __crawl_lotte_cinema(self):

    self.logger.info('')
    self.logger.info('### 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. ###')

    '''
    https://lottecinema.co.kr/LCWS/Cinema/CinemaData.aspx

    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialIndex 홈
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=300 스페셜관(샤롯데)        
    https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?       divisionCode=2&detailDivisionCode=0300&cinemaID=1016 월드타워
    https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?       divisionCode=2&detailDivisionCode=0300&cinemaID=3048

    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=940 수퍼플렉스
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=980 수퍼 S
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=930 수퍼 4D
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=988 컬러리움
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=986 씨네컴포트 
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=960 씨네패밀리 
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=200 씨네커플
    https://www.lottecinema.co.kr/NLCHS/Cinema/SpecialCinema?divisionCode=2&screendivcd=950 씨네비즈


    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "300") gaTit = "스페셜관_샤롯데";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "941") gaTit = "스페셜관_수퍼플렉스G";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "980") gaTit = "스페셜관_수퍼S";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "940") gaTit = "스페셜관_수퍼플렉스";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "930") gaTit = "스페셜관_수퍼 4D";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "950") gaTit = "스페셜관_씨네비즈";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "200") gaTit = "스페셜관_씨네커플";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "960") gaTit = "스페셜관_씨네패밀리";
    if (getParam.SpecialCinema == "2" && getParam.screendivcd == "986") gaTit = "스페셜관_씨네컴포트";
    return gaTit;
}
else return headTitle;        


    https://www.lottecinema.co.kr/NLCHS/Cinema/Detail?divisionCode=1&detailDivisionCode=1&cinemaID=1013 가산디지털

    '''

    cinema_count = 0

    if self.isPrnConsole:  # ################
        self.logger.info('-------------------------------------')
        self.logger.info('no, 코드, 스페셜관, 정렬일련번호, 극장명')
        self.logger.info('-------------------------------------')

    specialcinemas = ["0300",  # 스페셜관(샤롯데) 지정
                        "0941",  # 스페셜관(수퍼플렉스 G) 지정
                        "0940",  # 스페셜관(수퍼플렉스) 지정
                        "0930",  # 스페셜관(수퍼 4D) 지정
                        "0910",  # 스페셜관(수퍼바이브) 지정
                        "0960",  # 스페셜관(씨네패밀리) 지정
                        "0200",  # 스페셜관(씨네커플) 지정
                        "0950"   # 스페셜관(씨네비즈) 지정
                        ]
    for specialcinema in specialcinemas:
        # print(specialcinema)

        fields = {"paramList":
                    '{"MethodName":"SpecialCinemaList",'
                    '"channelType":"HO",'
                    '"osType":"' + self.ostype + '",'
                    '"osVersion":"' + self.osversion + '",'
                    '"DetailDivisionCode":"' + specialcinema + '",'
                    '"Latitude":"37.5675451", "Longitude":"126.9773356"'
                    '}'
                    }
        url = 'http://www.lottecinema.co.kr/LCWS/Cinema/CinemaData.aspx?nocashe=' + str(random.random())
        r = self.http.request('POST', url, fields)
        time.sleep(self.delayTime)

        data = r.data.decode('utf-8')
        # print(data)

        json_obj = json.loads(data)

        jsonpath_expr = parse('Cinemas.Items[*]')

        i = 0
        for match in jsonpath_expr.find(json_obj):
            cinemaid = str(match.value['CinemaID'])
            cinemanamekr = match.value['CinemaNameKR']
            sortsequence = match.value['SortSequence']

            i = i + 1

            self.dicCinemas[cinemaid] = ['Y', sortsequence, cinemanamekr]  # 극장(스페셜괌)정보저장

            if self.isPrnConsole:  # ################
                cinema_count += 1
                self.logger.info('{} : {},{},{},{}'.format(cinema_count, cinemaid, 'Y', sortsequence, cinemanamekr))
            #
        # for match in jsonpath_expr.find( json_obj ):
    # for specialcinema in specialcinemas:

    detaildivisioncodes = ["1",   # 서울
                            "2",   # 경기/인천
                            "3",   # 충청/대전
                            "4",   # 전라/광주
                            "5",   # 경북/대구
                            "101", # 경남/부산/울산
                            "6",   # 강원
                            "7"    # 제주
                            ]
    for detaildivisioncode in detaildivisioncodes:

        fields = {"paramList":
                    '{"MethodName":"GetCinemaByArea",'
                    '"channelType":"HO",'
                    '"osType":"' + self.ostype + '",'
                    '"osVersion":"' + self.osversion + '",'
                    '"multiLanguageID":"KR",'
                    '"divisionCode":"1","detailDivisionCode":"' + detaildivisioncode + '"'                                                                                                                                                   '}'
                    }
        url = 'http://www.lottecinema.co.kr/LCWS/Cinema/CinemaData.aspx?nocashe=' + str(random.random())
        r = self.http.request('POST', url, fields)
        time.sleep(self.delayTime)

        data = r.data.decode('utf-8')

        json_obj = json.loads(data)

        jsonpath_expr = parse('Cinemas.Items[*]')

        i = 0
        for match in jsonpath_expr.find(json_obj):
            cinemaid = str(match.value['CinemaID'])
            cinemaname = match.value['CinemaName']
            sortsequence = match.value['SortSequence']

            i = i + 1

            self.dicCinemas[cinemaid] = ['N', sortsequence, cinemaname]  # 극장 정보저장

            if self.isPrnConsole:  # ################
                cinema_count += 1
                self.logger.info('{} : {},{},{},{}'.format(cinema_count, cinemaid, 'N', sortsequence, cinemanamekr))
            #
        #
    #
#
#
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
#
#
# -------------------------------------------------------------------------------------------------
    

def crawling(self):
    try:
        self.__crawl_lotte_cinema()  # 영화관 (https://www.lottecinema.co.kr/NLCHS/) 에서 극장데이터를 가지고 온다. (dicCinemas)
        self.__crawl_lotte_boxoffice()  # 영화 / 현재 상영작(https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1) 에서 영화데이터를 가지고 온다. (dicMovieData)
        #self.__crawl_lotte_ticketingdata()  # 영화관 (http://www.lottecinema.co.kr/LCWS/Ticketing/TicketingData.aspx) 에서 극장데이터를 가지고 온다. (dicTicketingData1)
        
    except Exception as e:
        self.logger.error('LOTTE 크롤링 중 오류발생!')
        raise e

#

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


