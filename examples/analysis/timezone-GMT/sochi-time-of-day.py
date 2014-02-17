#!/usr/bin/python

# sochi-time-of-day.py
# Jason B. Hill (jason@jasonbhill.com)

# analyzes json tweet data for timezone -vs- time-of-day correlations


import simplejson as json
import time


# Function to turn snowflake into a timestamp
def snowflake2time(s):
    return (((s >> 22) + 1288834974657) / 1000)


# Function to turn a timestamp into a minute in day
def time2minute(t):
    # get the hour in GMT
    h = time.gmtime(t).tm_hour
    # get the minute in GMT
    m = time.gmtime(t).tm_min
    # return minute of the day
    return 60*h + m


# A dictionary of timezones containing total tweet and tweet by minute data
# Each key is a timezone
# Each value is a dictionary:
#   'total'     : total number of tweets for this timezone
#   'minutes'   : a tweet by minute list
timezone_data = {}


# iterate over days and hours
for d in range(0,29,1): # february
    for h in range(0,24): # hours in day
        filename = 'sochi2014-2-' + str(d) + '-' + str(h) + '-tweets'
        try:

            with open(filename) as f:
                print "examining %s" % filename
                for tweet in f:

                    try:
                        # load json
                        tweetjson = json.loads(tweet)
                        # get timezone
                        timezone = tweetjson['user']['time_zone']
                        minute = time2minute(snowflake2time(tweetjson['id']))

                        # add information to dictionary
                        if timezone in timezone_data:
                            timezone_data[timezone]['total'] += 1
                            timezone_data[timezone]['minutes'][minute] += 1
                        else:
                            # create dictionary for this timezone
                            timezone_data[timezone] = {}
                            # set initial counter for this timezone
                            timezone_data[timezone]['total'] = 1
                            # create a list of minute values
                            timezone_data[timezone]['minutes'] = [0 for i in range(1440)]
                            timezone_data[timezone]['minutes'][minute] += 1

                    except:
                        pass

        except:
            pass


# print json.dumps(timezone_data, indent=4, sort_keys=True)
for key in timezone_data:
    print "%s: %s" % (key, timezone_data[key]['minutes'])
