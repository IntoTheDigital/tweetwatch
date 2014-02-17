Tweets by Time of Day by Timezone
=================================

While recording tweets for the 2014 Sochi Winter Olympics, it became obvious that certain places in
the world were in-sync with the live events in Sochi while others were on tape delay. This script
analyzes tweets by timezone to build a graphical view of the time of day when people in that
timezone send tweets.

Of course, the Olympics are a multi-day event. The only thing we're considering here is time of day,
not the particular day when a tweet is composed. Thus, tweets from different days will get placed on
the same 24-hour clock.

Methodology
-----------

We have many files for the Olympic tweet data, and so we're going to have to iterate over those
files. About 10 days in to the games, we have about 24GB of JSON tweet data, plus a small amount of
rate-limit information, stored in hour-by-hour rotating files.

We'll maintain a list for each timezone, where the list will hold a minute-by-minute account of a
day. Whenever we encounter a tweet for that timezone, we'll compute the minute the tweet corresponds
to and add to the counter for that minute in that timezone. One could think of this as a
2-dimensional list indexed by timezone and minute.
