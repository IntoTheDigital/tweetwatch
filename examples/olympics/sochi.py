#!/usr/bin/python
# -*- coding: utf-8 -*-


import tweetwatch.stream
import tweetwatch.meters
import time
import simplejson as json

apiToken = {
    'consumerKey': 'your API key',
    'consumerSecret': 'your API key',
    'accessToken': 'your API key',
    'accessTokenSecret': 'your API key'}

userAgent = 'hilljb / version 0.1.2'

# create a tpm meter; record 180 seconds at a time
tpm = tweetwatch.meters.TPM(180)
# timer to display/record tpm info
tpm_watch = time.time() 

# define our data function
def dataFunction(data):
    # get current gmtime for formatting of filenames
    t = time.gmtime()

    # form filenames (sochi-year-m-d-h-desc)
    # --------------------------------------
    # tweet_file    (sochi-2014-2-7-20-tweets)
    # error_file    (sochi-2014-2-7-20-errors)
    # tpm_file      (sochi-2014-2-7-20-tpm)
    # rate_file     (sochi-2014-2-7-20-rate-limit)
    date_string = 'sochi' + str(t.tm_year) + '-' + str(t.tm_mon)
    date_string += '-' + str(t.tm_mday) + '-' + str(t.tm_hour) + '-'

    # if data is non-empty, send to output
    if len(data) > 5:

        # --- case 0: data isn't json
        json_data = {}
        try:
            json_data = json.loads(data)
        except:
            # the data wasn't parsable json
            filename = date_string + 'errors'
            f = open(filename, 'a')
            s = '-------------------------------------------------------------\n'
            s += str(int(time.time())) + '\n'
            s += data
            s += '\n'
            s += '-------------------------------------------------------------\n'
            f.write(s)
            f.close()

        # --- case 1: data is a tweet response
        if 'text' in json_data:
            filename = date_string + 'tweets'
            f = open(filename, 'a')
            f.write(data)
            f.close()

            # include this tweet in tpm counter
            tpm.record(1)

        # --- case 2: other errors
        if 'tweetwatch_error' in json_data:
            filename = date_string + 'errors'
            f = open(filename, 'a')
            s = '-------------------------------------------------------------\n'
            s += str(int(time.time())) + '\n'
            s += data
            s += '\n'
            s += '-------------------------------------------------------------\n'
            f.write(s)
            f.close()

        # --- case 3: rate limit response
        if 'limit' in json_data:
            filename = date_string + 'rate-limit'
            f = open(filename, 'a')
            # form timestamp and rate limit string
            s = str(int(time.time()))
            s += ': '
            s += str(json_data['limit']['track']) + '\n'
            f.write(s)
            f.close()

            # include in tpm counter
            tpm.record(json_data['limit']['track'])
    # end if len(data) > 5

    global tpm_watch
    if time.time() - tpm_watch > 30:
        # record/display tpm info roughly every 30 seconds
        print "current tpm: %s" % tpm.get()
        filename = date_string + 'tpm'
        f = open(filename, 'a')
        s = str(int(time.time()))
        s += ': ' + str(tpm.get()) + '\n'
        f.write(s)
        f.close()
        # reset tpm timer
        tpm_watch = time.time()



searchTerms = 'sochi, olympics, olímpics, olimpics, olympiáda, olympiada, olimpijske, olympische, олимпиада, алімпійскія, olümpiamängud, olympialaiset, olympiques, olympiade, ολυμπιακοί, olimpia, Ólympíuleikar, olympia, olímpicos'

searchTerms = 'sochi, teamusa'
searchTerms += ', olympics' # english, danish, filipino, romanian, swedish
searchTerms += ', olympi' # dutch (olympische), finnish (olympialaiset)
                          # french (olympiques), czech (olympiáda), german (olympiade)
searchTerms += ', ολυμπιακοί' # greek
searchTerms += ', オリンピック' # japanese
searchTerms += ', olimpia' # italian, hungarian (italian is olimpiada)
searchTerms += ', олимпийские' # russian
searchTerms += ', Олімпійські' # ukrainian


S = tweetwatch.stream.Stream(apiToken, searchTerms, dataFunction, user_agent=userAgent)

S.configure()
S.start()
