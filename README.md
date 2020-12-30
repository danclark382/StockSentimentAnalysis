
# StockSentimentAnalysis

# Introduction

This is the final project for INFO 440: Social Media Data Analysis. The goal of the project was to create a dashboard that allows a user to subscribe to certain stock tickers that can be queried utilizing the Twitter API. The dashboard consists of blocks where each block represents a ticker. Our dashboard parses the returned tweets from the query every hour and performs sentiment analysis utilizing the popular vader sentiment analyzer. The overall score for these tweets are compounded and uploaded to the dashboard as well as the most positive and the most negative tweet. In addition to the sentiment, the stock price updates in the dashboard during market hours. 


# Technologies
AWS EC2: AWS EC2 was utilized to automate the script running which was done via a CRON job. The frequency is set to run every hour on the thirty minute mark. 

Firebase DB: Firebase DB was utilized to store the data. It was a good choice due to the flexbility of running in the cloud, scalability, and the time-series nature of it. 

Python: All Scripts were created in python.

React: The dashboard was built using React.

# Illustrations
# Examples of us
# Project status 

INFO 440: Social Media Data Analysis
	Scrapes Twitter for tweets containing $Ticker
	Pulls in pricing data from IEX
	Gets Sentiment of Tweets
	Publishes results to Firebase DB
	Dashboard Written in React
	Published on AWS EC2 to run every 30 minutes via CRON
