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


import time
import sys

def _currMinMark():
    """
    Returns the Unix timestamp of the second at the beginning of the current
    minute in GMT.
    """
    # get the current Unix timestamp
    t = int(time.time())

    # get the second of the current minute GMT
    s = time.gmtime().tm_sec

    # return the timestamp of the current minute interval marker
    return t - s

def _nextMinMark():
    """
    Returns the Unix timestamp of the second at the beginning of the next
    minute in GMT.
    """
    # get the current Unix timestamp
    t = int(time.time())

    # get the second of the current minute GMT
    s = time.gmtime().tm_sec

    # return the timestamp of the next minute interval marker
    return t + (60 - s)





###############################################################################
# Minute counter                                                              #
###############################################################################
class TPM:
    def __init__(self, maxLen):
        """
        Create a dict with keys=timestamp and values=tweetcount to track the
        number of tweets (tweetcount) that occur at 'timestamp'. This list will
        hold timestamp values from the current second and back maxLen seconds.
        """
        if not isinstance(maxLen, int):
            raise TypeError('tweetwatch.meters.TPM error: maxLen must be an integer')
        elif maxLen < 60:
            raise ValueError('tweetwatch.meters.TPM error: maxLen must be >= 60')
        else: self._maxLen = maxLen

        # initialize self._tweetsBySecond
        self._tweetsBySecond = {}
        t = int(time.time())
        for i in range(t, t-(maxLen+1), -1):
            self._tweetsBySecond[i] = 0

    def _extendBySecond(self, timestamp):
        """
        Appends the dict self._tweetsBySecond to include timestamp:0. If the
        dict has grown longer than self.maxLen, elements are popped from the
        dict until proper length is obtained.
        """
        if not timestamp in self._tweetsBySecond:
            self._tweetsBySecond[timestamp] = 0
        while len(self._tweetsBySecond) > self._maxLen:
            v = self._tweetsBySecond.pop(min(self._tweetsBySecond.keys()))

    def _extendToNow(self, timestamp=None):
        """
        Prepends the list self._tweetsBySecond to include [timestamp, 0]
        entries for all seconds between its first timestamp value and now. This
        prepares the list for recording tweet counts at any given second.

        If the optional timestamp is set, use this value instead of now.
        """
        # get the timestamp of the current time
        if timestamp:
            s = timestamp
        else:
            s = int(time.time())

        # get the timestamp of the most recent time in the dict
        m = max(self._tweetsBySecond, key=self._tweetsBySecond.get)

        # add the required entries to the dict 
        for i in range(m + 1, s + 1, 1):
            self._extendBySecond(i)

    def record(self, numTweets, timestamp=None):
        """
        Add numTweets to self._tweetsBySecond[timestamp]. If the specified key
        does not exist, add the appropriate indices. If timestamp is not
        specified, use the current timestamp.
        """
        # if timestamp isn't given, use current timestamp
        if not timestamp:
            timestamp = int(time.time())

        # error checking on timestamp and numTweets
        if not isinstance(timestamp, int):
            raise TypeError('tweetwatch.meters.TPM.record error: timestamp not an integer')
        if timestamp <= 0:
            raise ValueError('tweetwatch.meters.TPM.record error: timestamp not a positive integer')
        if not isinstance(numTweets, int):
            raise TypeError('tweetwatch.meters.TPM.record error: numTweets not an integer')
        if numTweets <= 0:
            raise ValueError('tweetwatch.meters.TPM.record error: numTweets not a positive integer')

        # if timestamp is an existing key, then add numTweets to the value
        if timestamp in self._tweetsBySecond:
            self._tweetsBySecond[timestamp] += numTweets

        # if timestamp is not an existing key, extend self._tweetsBySecond
        else:
            # make sure that the given timestamp is greater than existing keys
            if timestamp < max(self._tweetsBySecond, key=self._tweetsBySecond.get):
                raise ValueError('tweetwatch.meters.TPM.record error: timestamp less than previous timestamps')
            else:
                self._extendToNow(timestamp)
                self._tweetsBySecond[timestamp] += numTweets

    def get(self):
        """
        Returns the current tweet per minute measurement as an integer.
        """
        # set a timestamp for now
        t = int(time.time())

        # make sure the dict is up-to-date by second.
        self._extendToNow(t)

        # return a measurement of number of tweets over the last 60 seconds
        return sum([self._tweetsBySecond[i] for i in range(t,t-60,-1)])










