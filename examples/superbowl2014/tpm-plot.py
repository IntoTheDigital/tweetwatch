#!/usr/bin/python

# plot 'tweets per minute' data from raw data as in superbowl example

# Jason B. Hill (jason@jasonbhill.com)

try:
    import simplejson as json
except ImportError:
    import json


# function to turn snowflake into timestamp
def snowflake2time(s):
    return (((s >> 22) + 1288834974657) / 1000)

# get the minimum and maximum timestamp from snowflakes in superbowl_data
times = set([])
with open('superbowl_data') as f:
    for line in f:
        try:
            parsed_line = json.loads(line)
            if 'id' in parsed_line:
                s = snowflake2time(parsed_line['id'])
                if not s in times:
                    times.add(s)
        except:
            pass

# set min/max time
min_time = min(times)
max_time = max(times)

# "last" is only used a place holder when computing contributions from rate
# limited tweets
last = min_time

# the current number of rate limited tweets
track = 0

# remove times (not needed after this point)
del(times)

# form dictionary of minute-by-minute TPM values
tpm = {}
for i in range(min_time, max_time, 60):
     tpm[i] = 0

# for each entry, record a value in the corresponding minute
with open('superbowl_data4') as f:
    for line in f:
        try:
            parsed_line = json.loads(line)
            if 'id' in parsed_line:
                s = snowflake2time(parsed_line['id'])
                m = (s - min_time) / 60
                last = min_time + m*60
                tpm[last] += 1
            elif 'limit' in parsed_line:
                n = parsed_line['limit']['track']
                if n > track:
                    tpm[last] += n - track
                    track = n
                else:
                    tpm[last] += n
                    track = n
        except:
            pass

# print output in 60 second intervals
for i in range(min_time, max_time, 60):
    print "%s: %s" % (i, tpm[i])
