import os
import requests
import datetime as dt
from twilio.rest import Client


today = dt.datetime.now()
#today = str(dt.datetime(today.year, today.month, today.day, 16))
yesterday = dt.datetime(today.year, today.month, today.day-2, 16)
before_yesterday = dt.datetime(today.year, today.month, today.day-3, 16)

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
STOCK_API_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_PARAMS = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": STOCK,
    "interval": "60min",
    "datatype": "json",
    "apikey": STOCK_API_KEY,
}


stock_response = requests.get(url=STOCK_API_ENDPOINT, params=STOCK_PARAMS)
stock_response.raise_for_status()
stock_data = stock_response.json()
print(stock_data)

closing_price_yesterday = float(stock_data["Time Series (60min)"][str(yesterday)]["4. close"])
closing_price_before_yesterday = float(stock_data["Time Series (60min)"][str(before_yesterday)]["4. close"])


price_difference = abs(closing_price_yesterday - closing_price_before_yesterday)
percentage = round(price_difference/max(closing_price_yesterday, closing_price_before_yesterday), 2)


# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_PARAM = {
    "qInTitle": COMPANY_NAME,
    "apiKey": NEWS_API_KEY,
    "from": before_yesterday.isoformat(),
    "to": yesterday.isoformat(),
    "language": "en"
}


news_response = requests.get(url=NEWS_API_ENDPOINT, params=NEWS_PARAM)
news_response.raise_for_status()
news_data = news_response.json()

news = []
for x in range(3):
    news_dict = {
        "Headline": news_data["articles"][x]["title"],
        "Brief": news_data["articles"][x]["description"],
    }
    news.append(news_dict)


## STEP 3: Use https://www.twilio.com
# Send a separate message with the percentage change and each article's title and description to your phone number.

# Twilio
account_sid = os.environ.get("ACCOUNT_SID")
auth_token = os.environ.get("AUTH_TOKEN")


if percentage >= 5:
    if closing_price_before_yesterday < closing_price_yesterday:
        action = "🔺"
    else:
        action = "🔻"

    msg = ""
    client = Client(account_sid, auth_token)
    for article in news:
        msg = f"{STOCK}: {action}{percentage}%\nHeadline: {article['Headline']}\n Brief: {article['Brief']}\n\n"
        print(msg)
        message = client.messages \
            .create(
            body=msg,
            from_="+12407248817",
            to="+41 78 934 29 44"
        )
        print(message.status)
