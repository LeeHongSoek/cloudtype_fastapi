import requests

# POST 요청을 보낼 PHP 스크립트의 URL
url = 'http://www.mtns7.co.kr/totalscore/upload_lotte.php'

# POST 데이터
data = {
    'moviedata': 'value1',
    'key2': 'value2',
}

# POST 요청 보내기
response = requests.post(url, data=data)

# 응답 결과 출력
print(response.text)
