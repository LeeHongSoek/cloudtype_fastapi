
# browsermob-proxy 서버 시작
#server_path = 'browsermob-proxy 실행 파일 경로' # browsermob-proxy 공식 저장소(https://github.com/lightbody/browsermob-proxy/releases)에서 사용 중인 운영 체제에 맞는 browsermob-proxy 바이너리를 다운로드합니다.

from selenium import webdriver
from browsermobproxy import Server
import time
from selenium.webdriver.chrome.options import Options


# browsermob-proxy 서버 시작
server_path = 'C://browsermob-proxy-2.1.4//bin//browsermob-proxy.bat'
server = Server(server_path)
server.start()



# 프록시 생성 및 WebDriver에 프록시 사용 설정
proxy = server.create_proxy()
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server={0}'.format(proxy.proxy))
chrome_options.add_argument('--ignore-certificate-errors')  # 인증서 오류 무시
chrome_options.add_argument('--ignore-ssl-errors')  # SSL 오류 무시
driver = webdriver.Chrome(options=chrome_options)

# 요청 캡처 활성화
proxy.new_har("lottecinema", options={'captureHeaders': True, 'captureContent': True})

# 웹사이트로 이동
driver.get("https://www.lottecinema.co.kr/NLCHS/Movie")

# 3초 대기
time.sleep(10)

# 캡처된 요청 가져오기
har = proxy.har
entries = har['log']['entries']

# 각 요청의 세부 정보 출력
for entry in entries:
    request = entry['request']
    print(request['url'])
    print(request['method'])
    print(request['headers'])
    
    if 'postData' in request:
        print(request['postData'])
    else:
        print("No post data available")

# WebDriver 종료 및 프록시 서버 중지
driver.quit()
server.stop()
