from datetime import datetime
import json
import pytz
import re

import firebase_admin
from firebase_admin import credentials, firestore, db
from iexfinance.stocks import Stock
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import twitter


with open("myKeys.json", 'r') as f:
    data = json.load(f)
twitter_keys = data['keys']['twitter']
iex = data['keys']['iex']

with open(r"replacement_dict.json") as d:
    replacement_dict = json.load(d)
with open(r"tickers.json") as d:
    tickers = json.load(d)
with open(r'previous_input.json', 'r') as d:
    previous_collection = json.load(d)

def oauth_login():
    # XXX: Go to  to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://developer.twitter.com/en/docs/basics/authentication/overview/oauth
    # for more information on Twitter's OAuth implementation.
    
    CONSUMER_KEY = twitter_keys['CONSUMER_KEY']
    CONSUMER_SECRET = twitter_keys['CONSUMER_SECRET']
    OAUTH_TOKEN = twitter_keys['OAUTH_TOKEN']
    OAUTH_TOKEN_SECRET = twitter_keys['OAUTH_TOKEN_SECRET']
    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

def twitter_search(twitter_api, q, max_results=300, **kw):

    # See https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets
    # and https://developer.twitter.com/en/docs/tweets/search/guides/standard-operators
    # for details on advanced search criteria that may be useful for 
    # keyword arguments
    
    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets
    last_id = tickers['since_id'][q[1:]]
    search_results = twitter_api.search.tweets(q=q, count=100, since_id=last_id, **kw)
    
    statuses = search_results['statuses']
    
    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://developer.twitter.com/en/docs/basics/rate-limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.
    
    # Enforce a reasonable limit
    max_results = min(1000, max_results)
    
    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError as e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') 
                        for kv in next_results[1:].split("&") ])
        
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
            if (re.search( x , match_ ) != None):
                return replacement_dict[x]
        return match_
    pattern = ''
    for i in sorted(replacement_dict.keys(), key=lambda x: len(x)):
        pattern += (i + r'|')
    pattern = pattern[0:-1]
    string = re.sub(pattern, repl_ , string_ )
    return re.sub(" +", " ", string)


def get_polarity_score(tweets_lst):
    """Get polarity score of tweets
    
    :param tweets_lst: tweets for a query
    :param type: list
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
    # Get logo
    return stock.get_logo()

def get_iex_data(ticker):
    """Get IEX data
    
    :param ticker: ticker to create Stock()
    :type ticker: string
    :returns: price change and logo
    :rtype: tuple
    """
    # Create stock object for IEX
    stock = Stock(ticker, token=iex)
    logo = tickers['logo'][ticker]
    if not logo:
        logo = get_logo(stock)
        tickers['logo'][ticker] = logo
    iex_stock = stock.get_quote(displayPercent=True)
    # Get latest price
    price = str(iex_stock['latestPrice'])
    # Get percent change
    change = iex_stock['changePercent']
    price_chg = f"{price} ({change:.2f}%)"
    return price_chg, logo


def main():
    # Conenct to twitter
    twitter_api = oauth_login()
    
    # Gather data input into dictionary
    db_collection = {}
    # Create date format
    date_fmt = '%m/%d/%Y %H:%M'
    # Convert to NYC timezone
    tz_NY = pytz.timezone('America/New_York') 
    for q in tickers['queries']:
        sentiment_lst = []
        ticker = q[1:]
        key = re.sub('[,.]*', '', tickers['tickers'][ticker])
        print(f"Searching twitter for {q}")
        # Get search results
        response = twitter_search(twitter_api, q)
        if not response:
            continue
        sentiment_lst = [t for t in response]
        # Get polarity scores for tweets
        arr, negative, positive, recent = get_polarity_score(sentiment_lst)
        # Append polarity results
        db_collection[key] = append_results(arr, ticker, negative, positive, recent)
        # Get IEX data
        price, logo = get_iex_data(ticker)
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
    
    # Get a database reference to our blog.
    ref = db.reference('')
    # Connect to collection
    users_ref = ref.child('tickers')
    # Input data
    users_ref.set(db_collection
    )
    
    # Save updated information
    with open('tickers.json', 'w') as f:
        json.dump(tickers, f)
    with open('previous_input.json', 'w') as f:
        json.dump(previous_collection, f)


if __name__ == '__main__':
    main()
