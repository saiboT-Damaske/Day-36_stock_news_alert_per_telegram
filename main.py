import requests
import datetime as dt

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_API_KEY = ""
NEWS_API_KEY = ""

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

TELEGRAM_BOT_TOKEN = ''
TELEGRAM_CHAT_ID = ''

TODAYS_DATE = dt.datetime.now().date()
YESTERDAYS_DATE = TODAYS_DATE - dt.timedelta(days=1)
DAY_BEFORE_YESTERDAYS_DATE = TODAYS_DATE - dt.timedelta(days=2)


## Helper function telegram messages

def telegram_bot_send_text(bot_message: str):
    bot_token = TELEGRAM_BOT_TOKEN
    bot_chat_id =  TELEGRAM_CHAT_ID
    send_text = 'https://api.telegram.org/bot' \
                + bot_token \
                + '/sendMessage?chat_id=' \
                + bot_chat_id + '&parse_mode=Markdown&text=' \
                + bot_message

    telegram_response = requests.get(send_text)

    return telegram_response.json()


## STEP 1: Use https://newsapi.org/docs/endpoints/everything
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
# HINT 1: Get the closing price for yesterday and the day before yesterday. Find the positive difference between
# the two prices. e.g. 40 - 20 = -20, but the positive difference is 20.
# HINT 2: Work out the value of 5% of yesterday's closing stock price.


stock_params = {
    "symbol": STOCK,
    "function": "TIME_SERIES_DAILY",
    "apikey": STOCK_API_KEY,
}
stock = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock.raise_for_status()
close_price_yesterday = float(stock.json()["Time Series (Daily)"][str(YESTERDAYS_DATE)]["4. close"])
close_price_day_before_yesterday = \
    float(stock.json()["Time Series (Daily)"][str(DAY_BEFORE_YESTERDAYS_DATE)]["4. close"])

change_price = abs(close_price_yesterday - close_price_day_before_yesterday)

# There are multiple ways of calculating this nice would be ((yesterday/before_yesterday)-1)*100)
# other options use the average as a dividend to get the percent
stock_change_percent = round(((change_price / close_price_day_before_yesterday) * 100), 2)

change_up_down = None
if close_price_yesterday > close_price_day_before_yesterday:
    change_up_down = "🔺"
else:
    change_up_down = "🔻"

# Rest of the code only executes if this is true.
if change_price > (close_price_day_before_yesterday * 0.05):
    print("get the news the change is big")

    ## STEP 2: Use https://newsapi.org/docs/endpoints/everything
    # Instead of printing ("Get News"), actually fetch the first 3 articles for the COMPANY_NAME.
    # HINT 1: Think about using the Python Slice Operator

    news_params = {
        "qInTitle": COMPANY_NAME,
        "apiKEY": NEWS_API_KEY,

    }
    news_stock = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_stock.raise_for_status()
    news_first_3_articles = news_stock.json()["articles"][:3]

    ## STEP 3: Use twilio.com/docs/sms/quickstart/python
    # Send a separate message with each article's title and description to your phone number.
    # HINT 1: Consider using a List Comprehension.

    alert_message = f"{STOCK} stock price change: {stock_change_percent}%{change_up_down}"
    alert_json = telegram_bot_send_text(alert_message)
    print(alert_json)

    message = [f"Headline: {article['title']}\n" \
               f"Publisher: {article['source']['name']}\n" \
               f"url: {article['url']}\n" \
               f"Description: {article['description']}" for article in news_first_3_articles]

    for article in message:
        print(article)
        message_json = telegram_bot_send_text(article)
        print(message_json)

    # Alternative way but also does not work if there is a url in the description
    # for i in range(0, 3):
    #     print(i)
    #     Headline = f"Headline: {news_first_3_articles[i]['title']}\n"
    #     Publisher = f"Publisher: {news_first_3_articles[i]['source']['name']}\n"
    #     url = f"url: {news_first_3_articles[i]['url']}\n"
    #     description = f"Description: {news_first_3_articles[i]['description']}\n"
    #
    #     message = f"{Headline}{Publisher}{url}{description}"
    #     message_json = telegram_bot_send_text(message)
    #     print(message_json)
    #     print(message)

