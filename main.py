# AWS Script
from datetime import datetime, time
import json
import pytz
import re

import firebase_admin
from firebase_admin import credentials, firestore, db
from iexfinance.stocks import Stock
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import twitter

# Load API Keys
with open("myKeys.json", 'r') as f:
    data = json.load(f)
# Load Regex Pattern:Replacement
with open(r"replacement_dict.json") as d:
    replacement_dict = json.load(d)
with open(r"tickers.json") as d:
    tickers = json.load(d)
# Load Previous Input
with open(r'previous_input.json', 'r') as d:
    previous_collection = json.load(d)
twitter_keys = data['keys']['twitter']
iex = data['keys']['iex']


def oauth_login():
    """Authenticate Twitter API keys

    :return: Authenticated Twitter API
    """
    consumer_key = twitter_keys['CONSUMER_KEY']
    consumer_secret = twitter_keys['CONSUMER_SECRET']
    oauth_token = twitter_keys['OAUTH_TOKEN']
    oauth_token_secret = twitter_keys['OAUTH_TOKEN_SECRET']
    auth = twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                               consumer_key, consumer_secret)
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api


def twitter_search(twitter_api, q, max_results=300):
    """Query twitter api

    :param twitter_api: Authenticated Twitter API
    :param q: Query Parameter
    :param max_results: Max results to return
    :return: Tweets
    """
    last_id = tickers['since_id'][q[1:]]
    search_results = twitter_api.search.tweets(q=q, count=100, since_id=last_id, **kw)
    
    statuses = search_results['statuses']
    max_results = min(1000, max_results)
    # Workaround to exceed the Twitter API limits
    for _ in range(10):  # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError as e:
            # End of results
            break
        kwargs = dict([kv.split('=')
                       for kv in next_results[1:].split("&")])
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        if len(statuses) > max_results: 
            break
    return statuses


def SimulSub(string_):
    """Single pass regex substitution method based off of dictionary
    
    :param string_: Sentence to search for matches
    :type string_: Str
    :returns: String with substitutions
    """
    if len(replacement_dict) == 0:
        return string_
    string_ = re.sub("([$][A-Za-z]*[\S]*)", "<TICKER>", string_)
    string_ = re.sub("(@[A-Za-z][\S]*)", "<USER>", string_)

    def repl_(regex_):
        match_ = regex_.group()
        for x in (sorted(replacement_dict.keys(), key=lambda x: len(x))):
            if re.search(x, match_) is not None:
                return replacement_dict[x]
        return match_
    pattern = ''
    for i in sorted(replacement_dict.keys(), key=lambda x: len(x)):
        pattern += (i + r'|')
    pattern = pattern[0:-1]
    string = re.sub(pattern, repl_, string_)
    return re.sub(" +", " ", string)


def get_polarity_score(tweets_lst):
    """Get polarity score of tweets
    
    :param tweets_lst: tweets for a query
    :returns polarity_arr: Array of polarity
    :returns negative: most negative tweet and score
    :returns positive: most positive tweet and score
    :returns recent: most recent tweet and score
    :rtype: tuple
    """
    # Initialize Sentiment Analyzer
    analyzer = SentimentIntensityAnalyzer()
    polarity_arr = np.zeros(len(tweets_lst))
    for i, text in enumerate(tweets_lst):
        # Clean text of tweet
        tweet = SimulSub(text['text'])
        # Measure the polarity of the tweet
        polarity = analyzer.polarity_scores(tweet)    
        # Store the normalized, weighted composite score
        polarity_arr[i] = polarity['compound']
    most_positive = np.argmax(polarity_arr)
    most_negative = np.argmin(polarity_arr)
    negative = (np.round(polarity_arr[most_negative], decimals=2), tweets_lst[most_negative]['text'])
    positive = (np.round(polarity_arr[most_positive], decimals=2), tweets_lst[most_positive]['text'])
    recent = (np.round(polarity_arr[0], decimals=2), tweets_lst[0]['text'])
    return polarity_arr, negative, positive, recent


def append_results(arr, ticker, negative, positive, recent):
    """Calculate polarity measures
    
    :param arr: List of polarities
    :type arr: np.array()
    :param ticker: ticker
    :type ticker: string
    :param negative: negative tweet, score
    :type negative: tuple
    :param positive: positive tweet, score
    :type positive: tuple
    :param recent: recent tweet, score
    :type recent: tuple
    :returns: polarity dictionary
    :rtype: dictionary
    """ 
    polarity_dict = {
        "Average_Sentiment_Score": np.round(np.average(arr), decimals=2),
        "id": ticker,
        'Most_Negative_Tweet': {
            'Tweet': negative[1],
            'Sentiment_Score': negative[0]
            }
        ,
        'Most_Positive_Tweet': {
            'Tweet': positive[1],
            'Sentiment_Score': positive[0]
            },
        'Most_Recent_Tweet': {
            'Tweet': recent[1],
            'Sentiment_Score': recent[0]
            }
        }
    return polarity_dict


def get_logo(stock):
    """Get logo of stock
    
    :param stock: stock object
    :type stock: iex.finance.stock()
    :returns: logo url dictionary
    :rtype: dictionary
    """
    return stock.get_logo()


def check_time():
    """Check if time is within market hours
    
    :returns: True if within market else False
    :rtype: boolen
    """
    tz_NY = pytz.timezone('America/New_York')
    current = datetime.now(tz_NY)
    date = datetime.today()
    open_time = datetime(date.year, date.month, date.day, 9, 30, 0, tzinfo=tz_NY)
    close_time = datetime(date.year, date.month, date.day, 4, 0, 0, tzinfo=tz_NY)
    if open_time < current < close_time:
        return True
    else:
        return False
    
    
def get_iex_data(ticker, cmp_id):
    """Get IEX data
    
    :param ticker: ticker to create Stock()
    :type ticker: string
    :param cmp_id: key used in collection
    :type cmp_id: string
    :returns: price change and logo
    :rtype: tuple
    """
    # Create stock object for IEX
    stock = Stock(ticker, token=iex)
    logo = tickers['logo'][ticker]
    if not logo:
        logo = get_logo(stock)
        tickers['logo'][ticker] = logo
    if not check_time():
        return previous_collection[cmp_id]['price'], logo
    iex_stock = stock.get_quote(displayPercent=True)
    # Get latest price
    price = str(iex_stock['latestPrice'])
    # Get percent change
    change = iex_stock['changePercent']
    price_chg = f"{price} ({change:.2f}%)"
    return price_chg, logo


def main():
    # Initialize Twitter API
    twitter_api = oauth_login()
    # Gather data input into dictionary
    db_collection = {}
    # Create date format
    date_fmt = '%m/%d/%Y %H:%M'
    # Convert to NYC timezone
    tz_NY = pytz.timezone('America/New_York') 
    for q in tickers['queries']:
        ticker = q[1:]
        key = re.sub('[,.]*', '', tickers['tickers'][ticker])
        print(f"Searching twitter for {q}")
        # Get search results
        response = twitter_search(twitter_api, q)
        if not response:
            db_collection[key] = previous_collection[key]
            continue
        sentiment_lst = [t for t in response]
        # Get polarity scores for tweets
        arr, negative, positive, recent = get_polarity_score(sentiment_lst)
        # Append polarity results
        db_collection[key] = append_results(arr, ticker, negative, positive, recent)
        # Get IEX data
        price, logo = get_iex_data(ticker, key)
        db_collection[key]['logo'] = logo
        db_collection[key]['price'] = price
        db_collection[key]['last_updated'] = datetime.now(tz_NY).strftime(date_fmt)
        tickers['since_id'][ticker] = response[0]['id']
        previous_collection[key] = db_collection[key]
        
    if not firebase_admin._apps:
        # Fetch the service account key JSON file contents
        # download service account key link
        # https://console.firebase.google.com/u/0/project/_/settings/serviceaccounts
        # change path to service account key
        cred = credentials.Certificate('stocksent-1bbf9-firebase-adminsdk-qf3lb-5c5aeae8a3.json')

        # Initialize the app with a service account, granting admin privileges
        firebase_admin.initialize_app(cred, {
              # replace the database url 
              'databaseURL': 'https://stocksent-1bbf9.firebaseio.com/',
              'databaseAuthVariableOverride': None
          })
    
    # Get a database reference to our page
    ref = db.reference('')
    # Connect to collection
    users_ref = ref.child('tickers')
    # Input data
    users_ref.set(db_collection)
    
    # Save updated information
    with open('tickers.json', 'w') as f:
        json.dump(tickers, f)
    with open('previous_input.json', 'w') as f:
        json.dump(previous_collection, f)


if __name__ == '__main__':
    main()
