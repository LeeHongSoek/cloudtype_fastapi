
# browsermob-proxy 서버 시작
#server_path = 'browsermob-proxy 실행 파일 경로' # browsermob-proxy 공식 저장소(https://github.com/lightbody/browsermob-proxy/releases)에서 사용 중인 운영 체제에 맞는 browsermob-proxy 바이너리를 다운로드합니다.

import json
from selenium import webdriver
from browsermobproxy import Server # pip install browsermob-proxy
import time
from selenium.webdriver.chrome.options import Options
import requests


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
#driver.get("https://www.lottecinema.co.kr/NLCHS/Movie/List?flag=1")

response = requests.get("https://www.lottecinema.co.kr/NLCHS")
        
if response.status_code == 200:
    # 파일 저장
    with open('C://Crawlling2//aa1.txt', 'a', encoding='utf-8') as file:
        file.write(f'url ========= {"https://www.lottecinema.co.kr/NLCHS"}')
        file.write('\n\n')
        file.write(response.text)
        file.write('\n\n')
        file.write('\n\n')
        file.write('\n\n')
        file.write('\n\n')


driver.get("https://www.lottecinema.co.kr/NLCHS")

# 3초 대기
time.sleep(10)

# 캡처된 요청 가져오기
har = proxy.har
entries = har['log']['entries']

# 각 요청의 세부 정보 출력
for entry in entries:
    request = entry['request']
    #print(request['url'])
    #print(request['method'])
    #print(request['headers'])
    
    '''
    if 'postData' in request:
        print(request['postData'])
    else:
        print("No post data available")
    '''

    url = request['url']
            
    if url.endswith('.js'):
        response = requests.get(url)
        
        if response.status_code == 200:
            # 파일 저장
            with open('C://Crawlling2//aa2.txt', 'a', encoding='utf-8') as file:
                file.write(f'url ========= {url}')
                file.write('\n\n')
                file.write(response.text)
                file.write('\n\n')
                file.write('\n\n')
                file.write('\n\n')
                file.write('\n\n')
    
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
        
        # 파싱한 데이터 활용
        # 예를 들어, 파싱한 데이터에서 특정 필드 값을 출력해보겠습니다.
        print('------------------------')
        print(data)
        print()

        print('------------------------')
        movies = data["Movies"]["Items"]
        for movie in movies:
            movie_name = movie["MovieNameKR"]
            print(movie_name)

# WebDriver 종료 및 프록시 서버 중지
driver.quit()
server.stop()
