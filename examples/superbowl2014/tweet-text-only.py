#!/usr/bin/python

# tweet-text-only.py
# Jason B. Hill (jason@jasonbhill.com) 2014 

# This script takes a pair of input file:
#   tweet_file  :   Contains tweets returned from Twitter's streaming API, each
#                   line having the raw JSON entity. Rate limited responses
#                   (and other responses not representing a tweet) are ignored.
#
# It outputs one file:
#   tweet_texts :   A file containing only the text of the returned tweets.
#                   Each tweet's text occupies one line.


input_file = '/media/usb0/superbowl/superbowlTweetData/superbowl_data_all'
tweet_texts = '/media/usb0/superbowl/superbowlTweetData/superbowl_tweets_text_only_all'


try:
    import simplejson as json
except ImportError:
    import json


# open the file tweet_texts for writing
f_tweet_texts = open(tweet_texts, 'w')

# get each tweet from the input file and write to tweet_texts file
with open(input_file) as f:
    for line in f:
        try:
            parsed_line = json.loads(line)
            if 'text' in parsed_line:
                f_tweet_texts.write(parsed_line['text'])
        except:
            pass

f_tweet_texts.close()


