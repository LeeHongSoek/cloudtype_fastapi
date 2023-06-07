import requests # pip install requests
from bs4 import BeautifulSoup # pip install beautifulsoup4
import pandas as pd # pip install pandas


def get_stock_closing_prices(stock_code, start_date, end_date):
    url = f"https://finance.yahoo.com/quote/{stock_code}/history?p={stock_code}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"data-test": "historical-prices"})
    rows = table.tbody.find_all("tr")

    closing_prices = []

    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 7:
            date = cells[0].span.text
            if start_date <= date <= end_date:
                closing_price = cells[4].span.text
                closing_prices.append((date, closing_price))

    return closing_prices

# 사용 예시
stock_code = "AAPL"  # 종목 코드
start_date = "2023-01-01"  # 시작 날짜
end_date = "2023-06-01"  # 종료 날짜

closing_prices = get_stock_closing_prices(stock_code, start_date, end_date)

# DataFrame 생성
df = pd.DataFrame(closing_prices, columns=["Date", "Closing Price"])

# "Closing Price" 열을 수치형으로 변환
df["Closing Price"] = df["Closing Price"].astype(float)

# DataFrame 출력
print(df)
