#!/usr/bin/python

# This script takes a pair of input files:
#   tweet_file  :   Contains tweets returned from Twitter's streaming API, each
#                   line having the raw JSON entity. Rate limited responses
#                   (and other responses not representing a tweet) are ignored.
#   word_file   :   A list of words, one per line with no delimiters.
#
# It outputs three files:
#   tpm_totals  :   A minute-by-minute account of hits from word_file found in
#                   tweet_file. The only item counted here are hits, not which
#                   word is hit or which search term corresponds to the hit.
#   tpm_by_word :   A minute-by-minute account of hits from word_file found in
#                   tweet_file organized by word.
#   tpm_by_term :   A minute-by_minute account of hits from word_file found in
#                   tweet_file organized by which word of word_file is hit and
#                   while search term the hit corresponds to.

# Jason B. Hill (jason@jasonbhill.com)


input_file = '/media/usb0/superbowl/superbowlTweetData/superbowl_data_all'
word_file = '/media/usb0/superbowl/superbowlTweetData/badwords'
search_terms = ['broncos','seahawks']

try:
    import simplejson as json
except ImportError:
    import json


# function to turn snowflake into timestamp
def snowflake2time(s):
    return (((s >> 22) + 1288834974657) / 1000)


# get the minimum and maximum timestamp from snowflakes in the given file
min_time = 0
max_time = 0
with open(input_file) as f:
    for line in f:
        try:
            parsed_line = json.loads(line)
            if 'id' in parsed_line:
                s = snowflake2time(parsed_line['id'])
                # set min time
                if min_time == 0 or s < min_time:
                    min_time = s
                # set max time
                if s > max_time:
                    max_time = s
        except:
            pass





# make a list of words from word_file
words = []
with open(word_file) as f:
    for line in f:
        words.append(line.strip())


# open files and print file headers
f_totals = open('tpm_totals', 'a')
f_totals.write('minute, total hits\n')

f_word = open('tpm_by_word', 'a')
s = 'minute, '
for w in words:
    s += w + ', '
s += '\n'
f_word.write(s)

f_term = open('tpm_by_term', 'a')
s = 'minute, '
for w in words:
    for term in search_terms:
        s += w + " (" + term + "), "
s += '\n'
f_term.write(s)


f_term_only = open('tpm_term_only', 'a')
s = 'minute, '
for term in search_terms:
    # add each individually
    s += term + ', '
s += '\n'
f_term_only.write(s)



# form a dictionary for totals
tpm_totals = {}
for i in range(0, 1+(max_time-min_time)/60, 1):
    tpm_totals[i] = 0

# form a dictionary for tpm by word
tpm_by_word = {}
for i in range(0, 1+(max_time-min_time)/60, 1):
    # make a dictionary for each minute
    tpm_by_word[i] = {}
    for w in words:
        tpm_by_word[i][w] = 0

# form a dictionary for tpm by term and word
tpm_by_term = {}
for i in range(0, 1+(max_time-min_time)/60, 1):
    # make a dictionary for each minute
    tpm_by_term[i] = {}
    for w in words:
        tpm_by_term[i][w] = {}
        for term in search_terms:
            tpm_by_term[i][w][term] = 0

# form a dictionary for tpm by terms only
tpm_term_only = {}
for i in range(0, 1+(max_time-min_time)/60, 1):
    # make a dictionary for each minute
    tpm_term_only[i] = {}
    for term in search_terms:
        tpm_term_only[i][term] = 0

# iterate over the input file and categorize findings - this will take a bit
j = 0
with open(input_file) as f:
    for line in f:
        j += 1
        if j % 1000 == 0: print j
        tweet = json.loads(line)
        if 'id' in tweet:
            # get timestamp
            s = snowflake2time(tweet['id'])
            # get minute mark
            m = (s - min_time)/60
            tls = set(tweet['text'].lower().split())

            for w in words:
                if 'text' in tweet and w in tls:
                    # add any words to total count for this minute
                    tpm_totals[m] += 1

                    # add words to specific word counts
                    tpm_by_word[m][w] += 1

                    # add words to specific search word counts
                    for term in search_terms:
                        if term in tweet['text'].lower():
                            tpm_by_term[m][w][term] += 1
                            tpm_term_only[m][term] += 1

# print results
for i in range(0, 1+(max_time-min_time)/60, 1):
    # print word totals
    s = '%s, %s,\n' % (i, tpm_totals[i])
    f_totals.write(s)

    # print individual words
    s = '%s, ' % i
    for w in words:
        s += str(tpm_by_word[i][w]) + ', '
    s += '\n'
    f_word.write(s)

    # print term specific words
    s = '%s, ' % i
    for w in words:
        for term in search_terms:
            s += str(tpm_by_term[i][w][term]) + ', '
    s += '\n'
    f_term.write(s)

    # print term only counts
    s = '%s, ' % i
    for term in search_terms:
        s += str(tpm_term_only[i][term]) + ', '
    s += '\n'
    f_term_only.write(s)
