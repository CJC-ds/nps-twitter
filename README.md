# nps-twitter
Net promoter score mined from twitter thread engagement.

## Project background
As organizations become increasingly reliant on Social Media platforms for customer engagement; customers have been given a voice to either complain or praise the efforts of these organizations.

Platforms such as **Twitter** have become increasingly rich in data as customers voluntarily voice their opinions and critique the behaviour and decisions that certain organizations decide to make.

Larger organizations with millions of followers will be bombarded with tweets at rates which are humanly impossible to read.
Therefore the full scope of how customers feel about their new announcement and/or decisions cannot be easily understood through human reading alone.

Feedback is important but it is only valuable when it is noticed, internalized and addressed.

## Aim

This project aims to retrieve and analyze tweets made to specific twitter threads, and the overall sentiment for the threads will be analyzed along with the most prevalent words associated with the positive and negative sentiments.

## Use case example

### @FallGuysGame
[**@FallGuysGame**](https://twitter.com/FallGuysGame) is a new videogame with a social media following of 1.4 Million users. Each of their tweets have no less than 1k likes. The number of comments made to each twitter thread ranges from 137 to 3.7k.

Previously, the team at **@FallGuysGame** have made an announcement about removing steam family share feature for their game, in efforts to combat cheaters exploiting the system to avoid bans.
The decision was met with mixed opinions.
People that play **Fall Guys** on steam family share were disappointed and outraged, while those that didn't, praised the team's efforts for combating game cheaters.

## Getting started.

### Setting credentials
In order to use the code for `get_replies.py`, you are first required to setup a Twitter [developer account](https://developer.twitter.com/en).

Then create a `credentials.ini` file with the format below.
Insert your own api keys. Then add `credentials.ini` file into the `src` folder.

```
[API]
key=YOUR_API_KEY
secret=YOUR_API_SECRET
[Access]
token=YOUR_ACCESS_TOKEN
secret=YOUR_ACCESS_SECRET
[Bearer]
token=YOUR_BEARER_TOKEN
```
### Getting the data

Run `get_replies.py` and input the twitter username without the '@' symbol. Along with the thread you wish to analyze.

#### Flag options

Recently implemented (24-09-2020) the passing of a flag option to retrieve
more tweet replies.

* **file_format `-f`**:

    Specify the output file format. Default `csv`.
    Other option `pickle`.

* **search_depth `-s`**:

    Specify the number of tweets to search through. Default `1000`,
    Note that not all tweets that are searched will be `in_reply_to`
    specified tweet. If `-s` is greater than 1000; please set `-w` to `on`.
    Free tier twitter API limits at 1000 per 15 mins.

* **wait_on_rate_limit `-w`**:

    Wait to retrieve more tweets once API limitations are exceeded.
    Can be either `on` or `off`. Default `off`.

*e.g.* `https://twitter.com/FallGuysGame/status/1308794965909295104 -f pickle -s 2000 -w on`

#### Data is saved to disk

The saved data retrieved from the Twitter API can be accessed as a csv (default)
file located at `../data/raw/replies_to_<twitter_id>.csv`

### Process the data

Run `preprocessing.py` and input the twitter thread id. It will check the csv files from the previous step, create additional columns for `processed_text` (Stop words are removed, words tokenized), `stemmed` (words are reduced to their root word, e.g. *likeable* become *like*), `sentiment_score` (performed on `processed_text` a signed float value which determines the overall sentiment of the tweet, where negative values have negative sentiment, and positive values have positive sentiment), `sentiment_score_stemmed` (similar to `sentiment_score`, but performed on stemmed words).

The result will be a `pickle` file (serialized python native data storage). The decision to create a `pickle` instead of csv, is that the datatypes of the original dataset is also stored, and will speed up reading time during the analysis step.

## Analysis

**In development**

## Known issues

Currently, the free-tier of twitter API does not support the tracking of replies to specific tweets.
The work around is to point the cursor object at the specified tweet (we wish to observe), and iterate over all tweets to `@user` and only keep the tweets `in_reply_to` specified tweet.

This method is not ideal (limitations):

* Limits on the official free-tier Twitter API only allows us to iterate through 1000 tweets every 15 mins.

* The majority of tweets to specified Twitter `@user` may not necessarily fall within the limits of 1000 cursor iterations. As some tweets to `@user` may be `in_reply_to` another tweet made by `@user`, but only shortly after the tweet of interest being made.

**Not all tweets to specified tweet may be retrieved if a large amount of tweets directed to `@user` straight after the tweet of interest is made.**

### Solution

Enabled a feature to sleep/wait approximately 15 minutes when API limits are reached. The `get_replies.py` will continue to search until the specified `search_depth` is met.
The `search_depth` can be assigned using the flag options (see flag options).
