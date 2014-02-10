#!/usr/bin/python
# -*- coding: utf-8 -*-

#   This program is free software: you can redistribute it and/or modify it
#   under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or (at your
#   option) any later version.
#
#   This program is distributed in the hope that it will be useful, but WITHOUT
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
#   License for more details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Jason B. Hill (jason@jasonbhill.com)'
__copyright__ = 'Copyright (c) 2014'
__version__ = '0.1.2'

#   Thanks to Room 214 (www.room214.com) in Boulder, CO for involving me with
#   this project. 

import sys
import time

try: import pycurl
except ImportError:
    print >> sys.stderr, "tweetwatch.stream fatal error: 'import pycurl' failed."
    sys.exit(0)

try: import urllib
except ImportError:
    print >> sys.stderr, "tweetwatch.stream fatal error: 'import urllib' failed."
    sys.exit(0)

try: import oauth2 as oauth
except ImportError:
    print >> sys.stderr, "tweetwatch.stream fatal error: 'import oauth2' failed."
    print >> sys.stderr, "See: https://github.com/simplegeo/python-oauth2"
    sys.exit(0)

try: import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        print >> sys.stderr, "tweetwatch.stream fatal error: 'import json' failed."
        sys.exit(0)



###############################################################################
# Stream class                                                                #
# --------------------------------------------------------------------------- #
# Uses the pycurl module to connect to Twitter's streaming API                #
###############################################################################
class Stream:
    def __init__(self, apiToken, searchTerms, dataFunction,
            api_url='https://stream.twitter.com/1.1/statuses/filter.json', curl_encoding='gzip',
            filter_level='none', follow=None, language=None, locations=None, stall_warnings='true',
            timeout=300, user_agent=None):
        """
        Setup a persistant HTTP connection to Twitter's streaming API.

        REQUIRED INPUT:

        apiToken (dictionary) - The keys/values here correspond directly to a
            Twitter OAuth API token (see dev.twitter.com). The expected keys
            are as follows: 'consumerKey', 'consumerSecret', 'accessToken', and
            'accessTokenSecret'. The values are the corresponding strings. Note
            that Twitter's OAuth procedure is a bit strange here. Normally,
            the application that wants OAuth resources (in this case, Twitter
            content) would have only a consumer key and consumer secret. The
            application then makes a handshake with the server and exchanges
            its consumer key and secret for an access token/token secret. That
            token usually has a limited life, and then expires, at which point
            the application must authenticate for new tokens. Twitter's tokens
            don't expire, and so no handshake is needed and they give you the
            access token/token secret along with your consumer key and secret.

            ***EXAMPLE***

            apiToken = { # example only; not a real set of keys
                'consumerKey': 'aShhfdHHjjkfdsHHdkdkjfd',
                'consumerSecret': 'jkjUTEVS8843KkjhfdkfdSKHD93493jjsdkasfdks',
                'accessToken': '1285309457-8cdsfdlKKKfdslfdkkkskljlkjsfdXCKKF',
                'accessTokenSecret': 'KK8484jkjhfdKJHSKJ45kAKSAKagdfgfd''
            }

        searchTerms (string) - A comma-separated string of search terms. Each
            term must be limited to 60 bytes. Twitter's documentation states
            that "exact matching of phrases is not supported," although \'this
            string\' in quotes appears to work perfectly fine. UTF-8 characters
            will match exactly, even when an equivalent ASCII character exists,
            and so 'touché' will return different results than 'touche'. URL
            names are canonicalized on Twitter (e.g., "www.example.com" becomes
            "example.com"), so omit the "www" when searching for instances of a
            given URL. Terms are only searched for in the text of tweets, and
            hashtags are part of the text. So, using the term 'hashtag' will
            match tweets containing 'hashtag' and '#hashtag', which the term
            '#hashtag' will only match tweets hashtagged with '#hashtag'.

            ***EXAMPLE***

            searchTerms = 'item1, \'iterm with space\', #iterm3'

        dataFunction (function) - A Python function to route the JSON responses
            of the API appropriately.

        OPTIONAL INPUT:

        api_url (string) - A string representing the connection point for
            Twitter's streaming API. The default value is
            'https://stream.twitter.com/1.1/statuses/filter.json'.

        curl_encoding (string) - Must be one of 'identity' (does nothing),
            'deflate' (asks the server to compress its response using the zlib
            algorithm), or 'gzip' (asks the server to use gzip). The default
            value is 'gzip'.

        filter_level (string) - Must be one of 'none' (no filtering), 'low', or
            'medium'. The latter two options will provide only a sample of the
            tweets matching your search criteria, which is useful when rate
            limiting is expected or when only a sample set is needed. The
            default value is 'none'.

        follow (string) - A comma-separated string of user ID's you wish to
            include. Tweets from users other than those listed will be ignored
            and not returned in your search. The default is None.

            ***EXAMPLE***

            follow = '@user1, @user2, @user3'

        language (string) - A comma-separated string of BCP-47 language codes,
            limiting returned tweets to specific languages. For instance, using
            the string 'es, en' will limit tweets to English, Spanish, and
            Castilian. The default is to include tweets in all languages. The
            default value is None, returning all tweets matching your search
            criteria, regardless of language.

            ***EXAMPLE***

            language = 'es, en'

        locations (string) - A comma-separated string of longitude, latitude
            pairs specifying a set of bounding boxes to filter Tweets by. For
            instance, using '-122.75,36.8,-121.75,37.8' will only yield tweets
            from San Francisco. San Francisco or New York City can be given by
            using '-122.75,36.8,-121.75,37.8,-74,40,-73,41'. The default value
            is None, returning all tweets matching your search criteria,
            regardless of location.

            ***EXAMPLE***

            locations = '-122.75,36.8,-121.75,37.8,-74,40,-73,41'

        stall_warnings (string) - The only accepted value is 'true'. Setting
            to 'true' will cause periodic messages to be delivered if the client
            is in danger of being disconnected due to the network connection
            being too slow to maintain pace with responses.. These messages are
            only sent when the client is falling behind, and will occur at a
            maximum rate of about once every 5 minutes. This parameter is most
            appropriate for clients with high-bandwidth connections, such as the
            firehose. The default value is 'true'. If you wish to turn this
            option off explicitly, use stall_warnings = None.

        timeout (int) - A positive integer telling the connection to reset if
            less than 1 byte is received from Twitter within the specific time
            in seconds. If no tweets match your search criteria within 20 to 30
            seconds, Twitter will typically respond with a simple ping, which
            will maintain the connection. If no response or ping is received in
            'timeout' seconds, the connection will be closed and reset. The
            default value is 300 seconds (5 minutes).

            ***EXAMPLE***

            timeout = 200

        userAgent (string) : A string denoting the website or service using the
            streaming API data. This is for identication purposes. On some
            shared server systems, such as Amazon EC2, Twitter has limited API
            connections based on info provided in the user agent field, as too
            many were using those services for spam purposes. Twitter also
            gives no guidance on how to use this field; just make sure it makes
            your service, purpose, and identity clear. The default is None.

            ***EXAMPLE***

            userAgent = 'mywebsite.com / version: 1.1.3'
        """
        # the connection hasn't been configured or started yet
        self.connection = None

        # check and load the consumer key portion of the API key
        if not apiToken['consumerKey']:
            raise KeyError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                           "key 'consumerKey' not in dict 'apiToken'")
        elif not isinstance(apiToken['consumerKey'], str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "key value for 'consumerKey' not a string in dict 'apiToken'")
        else:
            self.consumerKey = apiToken['consumerKey']

        # check and load the consumer secret portion of the API key
        if not apiToken['consumerSecret']:
            raise KeyError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                           "key 'consumerSecret' not in dict 'apiToken'")
        elif not isinstance(apiToken['consumerSecret'], str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "key value for 'consumerSecret' not a string in dict 'apiToken'")
        else:
            self.consumerSecret = apiToken['consumerSecret']

        # check and load the access token portion of the API key
        if not apiToken['accessToken']:
            raise KeyError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                           "key 'accessToken' not in dict 'apiToken'")
        elif not isinstance(apiToken['accessToken'], str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "key value for 'accessToken' not a string in dict 'apiToken'")
        else:
            self.accessToken = apiToken['accessToken']

        # check and load the access token secret portion of the API key
        if not apiToken['accessTokenSecret']:
            raise KeyError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                           "key 'accessTokenSecret' not in dict 'apiToken'")
        elif not isinstance(apiToken['accessTokenSecret'], str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "key value for 'accessTokenSecret' not a string in dict 'apiToken'")
        else:
            self.accessTokenSecret = apiToken['accessTokenSecret']

        # check and load search terms; not much error checking possible
        if not isinstance(searchTerms, str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'searchTerms' not a string (must be a comma-separated string)")
        else:
            self.searchTerms = searchTerms

        # api_url may be overridden; make sure it is a string
        if not isinstance(api_url, str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'api_url' not a string")
        else:
            self.api_url = api_url

        # curl encoding may only be one of three items
        if not curl_encoding in ['identity','deflate','gzip']:
            raise ValueError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'curl_encoding' must be 'identity', 'deflate', or 'gzip'")
        else:
            self.curl_encoding = curl_encoding

        # set data function, not much checking done here
        if dataFunction is None or not hasattr(dataFunction, '__call__'):
            raise ValueError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'dataFunction' must be a Python function")
        else:
            self.dataFunction = dataFunction

        # filter level may only be one of three items
        if not filter_level in ['none','low','medium']:
            raise ValueError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'filter_level' must be 'none', 'low', or 'medium'")
        else:
            self.filter_level = filter_level

        # 'follow' is optional; make sure it is a string; do no other checking
        if follow and not isinstance(follow, str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'follow' not a string (when used, must be a comma-separated string)")
        elif follow:
            self.follow = follow
        else:
            self.follow = None

        # 'language' is optional; make sure it is a string; do no other checking
        if language and not isinstance(language, str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'language' not a string (when used, must be a comma-separated string)")
        elif language:
            self.language = language
        else:
            self.language = None

        # 'locations' is optional; make sure it is a string; do no other checking
        if locations and not isinstance(locations, str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'locations' not a string (when used, must be a comma-separated string)")
        elif locations:
            self.locations = locations
        else:
            self.locations = None

        # 'stall_warnings' must be either 'true' or None
        if stall_warnings and not stall_warnings == 'true':
            raise ValueError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'stall_warnings' must be either None or 'true'")
        elif stall_warnings:
            self.stall_warnings = 'true'
        else:
            self.stall_warnings = None

        # 'timeout' is optional; must be a positive integer
        if timeout and not isinstance(timeout, int):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'timeout' must be an integer")
        elif timeout and not timeout > 0:
            raise ValueError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'timeout' must be a positive integer")
        else:
            self.timeout = timeout

        # 'user_agent' is optional; make sure it is a string; do no other checking
        if user_agent and not isinstance(user_agent, str):
            raise TypeError("error in input to tweetwatch.stream.Stream.__init__():\n" \
                            "'user_agent' not a string (when used, must be a comma-separated string)")
        elif user_agent:
            self.user_agent = user_agent
        else:
            self.user_agent = None

        # form apiOpts dictionary for urlencoding and passing in html header
        self.apiOpts = {}
        if self.stall_warnings:
            self.apiOpts['stall_warnings'] = self.stall_warnings
        self.apiOpts['filter_level'] = self.filter_level
        if self.language:
            self.apiOpts['language'] = self.language
        self.apiOpts['track'] = self.searchTerms
        if self.locations:
            self.apiOpts['locations'] = self.locations

        # set error timing data for reconnect backoff
        self.errtime = int(time.time())

    def close(self):
        """
        Closes the connection. Corresponds to libcurl's curl_easy_cleanup.
        """
        self.connection.close()

    def configure(self):
        """
        Configure's the connection. Corresponds to libcurl's curl_easy_setopt.
        """
        # if the connection already exists, close it before continuing
        if self.connection:
            self.close()

        # set up the connection
        self.connection = pycurl.Curl()

        # set the URL of the connection endpoint
        self.connection.setopt(pycurl.URL, self.api_url)

       # set the user agent information
        if self.user_agent:
            self.connection.setopt(pycurl.USERAGENT, self.user_agent)

        # set the encoding
        self.connection.setopt(pycurl.ENCODING, self.curl_encoding)

        # tell curl to use http post
        self.connection.setopt(pycurl.POST, 1)

        # tell curl than less than 1 byte per second for self.timeout
        # is reason to consider the connection too slow and abort
        self.connection.setopt(pycurl.LOW_SPEED_LIMIT, 1)
        self.connection.setopt(pycurl.LOW_SPEED_TIME, self.timeout)

        # url encode post fields (stored as dictionary)
        self.connection.setopt(pycurl.POSTFIELDS, urllib.urlencode(self.apiOpts))

        # set http header with host and oauth2 authorization
        self.connection.setopt(pycurl.HTTPHEADER, ['Host: stream.twitter.com',
                'Authorization: %s' % self.get_oauth_header()])

        # point to the function that receives data from the stream
        self.connection.setopt(pycurl.WRITEFUNCTION, self.dataFunction)

    def get_oauth_header(self):
        """
        Use oauth2 module to create and return oauth header.
        """
        params = {
            'oauth_version': '1.0',
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_timestamp': int(time.time())
        }
        req = oauth.Request(method='POST', parameters=params,
                url='%s?%s' % (self.api_url, urllib.urlencode(self.apiOpts)))
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(),
                oauth.Consumer(key=self.consumerKey, secret=self.consumerSecret),
                oauth.Token(key=self.accessToken, secret=self.accessTokenSecret))
        return req.to_header()['Authorization'].encode('utf-8')

    def start(self):
        """
        Listen to the streaming endpoint.
        """
        while True:
            self.configure()
            try:
                self.connection.perform()
            except:
                # this should only happen when a network error occurs
                if int(time.time()) - self.errtime < 10:
                    errdict = {
                        'tweetwatch_error': {
                            'timestamp': int(time.time()),
                            'is_fatal': False,
                            'type': 'network',
                            'action': 'multiple recent failures - waiting 10 seconds'
                        }
                    }
                    self.dataFunction(json.dumps(errdict)+'\n')
                    time.sleep(10)
                else:
                    errdict = {
                        'tweetwatch_error': {
                            'timestamp': int(time.time()),
                            'is_fatal': False,
                            'type': 'network',
                            'action': 'waiting 1 second'
                        }
                    }
                    self.dataFunction(json.dumps(errdict)+'\n')
                    time.sleep(1)

            self.errtime = int(time.time())

            # get HTTP status code
            sc = self.connection.getinfo(pycurl.HTTP_CODE)

            if sc == 400:
                errdict = {
                    'tweetwatch_error': {
                        'timestamp': int(time.time()),
                        'is_fatal': True,
                        'type': 'HTTP 400 - bad request',
                        'action': 'process terminated'
                    }
                }
                self.dataFunction(json.dumps(errdict)+'\n')
                print >> sys.stderr, str(errdict)
                self.close()
                sys.exit(0)

            elif sc == 401:
                errdict = {
                    'tweetwatch_error': {
                        'timestamp': int(time.time()),
                        'is_fatal': True,
                        'type': 'HTTP 401 - unauthorized',
                        'action': 'process terminated'
                    }
                }
                self.dataFunction(json.dumps(errdict)+'\n')
                print >> sys.stderr, str(errdict)
                self.close()
                sys.exit(0)

            elif sc == 403:
                errdict = {
                    'tweetwatch_error': {
                        'timestamp': int(time.time()),
                        'is_fatal': True,
                        'type': 'HTTP 403 - forbidden',
                        'action': 'process terminated'
                    }
                }
                self.dataFunction(json.dumps(errdict)+'\n')
                print >> sys.stderr, str(errdict)
                self.close()
                sys.exit(0)

            elif sc == 420:
                errdict = {
                    'tweetwatch_error': {
                        'timestamp': int(time.time()),
                        'is_fatal': True,
                        'type': 'HTTP 420 - http rate limit',
                        'action': 'waiting one minute'
                    }
                }
                self.dataFunction(json.dumps(errdict)+'\n')
                print >> sys.stderr, str(errdict)
                time.sleep(60)

