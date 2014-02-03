#!/usr/bin/python

# Jason B. Hill (jason@jasonbhill.com)
#
# A simple example to demonstrate using Tweetwatch to collect data from
# Twitter's streaming API. This example uses the 2014 SuperBowl and the search
# terms "broncos" and "seahawks".

# See "superbowl_data" for sample output for this script


# Load tweetwatch
import tweetwatch.stream
import tweetwatch.meters

# set the API access token / enter your values to make it function
apiToken = {
    'consumerKey': 'xxxx',
    'consumerSecret': 'xxxx',
    'accessToken': 'xxxx',
    'accessTokenSecret': 'xxxx'}

userAgent = 'tweetwatch / version 0.1.2'

# create a tweets per minute meter; record 180 seconds at a time
tpm = tweetwatch.meters.TPM(180)

# define our data function
def dataFunction(data):
    # open a file for recording the data
    f = open('superbowl_data', 'a')

    # write the data to the file when it has non-trivial length
    # Note: We expect a ton of data here, so rate limited tweets come in as:
    # {"limit":{"track": 9994873}}
    # This means that we've missed 9994873 tweets since the connection was
    # originally established.
    if len(data) > 5:
        f.write(data)
        print data

    # close the data file
    f.close()

    # print current tpm meter info
    if len(data) > 5:
        tpm.record(1)
        print "\nCurrent tpm: %s\n" % tpm.get()

# define search terms
searchTerms = 'broncos, seahawks'

# configure the stream search
S = tweetwatch.stream.Stream(apiToken, searchTerms, dataFunction, user_agent=userAgent)

# run the search
S.configure()
S.start()
