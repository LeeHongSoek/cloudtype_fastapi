import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_sp500_tickers():
    url = "https://www.slickcharts.com/sp500"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table')
    tickers = []
    for row in table.find_all('tr')[1:]:
        ticker = row.find_all('td')[2].text.strip()

        dot_index = ticker.find(".")
        if dot_index != -1:
            ticker = ticker[:dot_index] + ticker[dot_index+1:].lower()
        else:    
            tickers.append(ticker)
    return tickers

def get_closing_price(ticker, start_date_str):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = start_date + timedelta(days=1)
    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())
    params = {
        "period1": start_timestamp,
        "period2": end_timestamp
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    timestamps = data["chart"]["result"][0]["timestamp"]
    closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    target_close = closes[0]
    return target_close

def main():
    start_date_str = "2023-06-03"
    tickers = get_sp500_tickers()
    for ticker in tickers:
        closing_price = get_closing_price(ticker, start_date_str)
        print(f"The closing price of {ticker} on {start_date_str} is: {closing_price}")

main()
