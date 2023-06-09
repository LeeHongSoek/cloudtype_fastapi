import requests
from datetime import datetime, timedelta

def get_closing_price(ticker, start_date_str):
    # API 엔드포인트 URL
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

    # 시작일과 종료일 설정 (년-월-일 형식)
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = start_date + timedelta(days=1)

    # 시작일과 종료일을 Unix 시간(timestamp)으로 변환
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    # 매개변수 설정
    params = {
        "period1": start_timestamp,
        "period2": end_timestamp
    }

    # API 요청을 보내고 응답 받기
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, params=params)

    # JSON 응답 파싱
    data = response.json()

    # 종가 데이터 추출
    timestamps = data["chart"]["result"][0]["timestamp"]
    closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]

    # 입력한 날짜의 종가 데이터 리턴
    target_close = closes[0]
    return target_close

def main():
    ticker = "GOOGL"
    start_date_str = "2023-06-03"

    closing_price = get_closing_price(ticker, start_date_str)
    print(f"The closing price of {ticker} on {start_date_str} is: {closing_price}")

main()
