# nps-twitter
Net promoter score mined from twitter thread engagement.

For twitter accounts with large followings, we can quantitatively measure how audience/customers feel about an announcement of a business decision or product.
It can be used to quickly address a PR disaster before it happens, or determine if the company is moving towards a direction that your customers believe in.

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

Previously, the team at **@FallGuysGame** have made an [announcement](https://twitter.com/FallGuysGame/status/1298194813247004672) about removing steam family share feature for their game, in efforts to combat cheaters exploiting the system to avoid bans.
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

* **search_depth `-sd`**:

    Specify the number of tweets to search through. Default `1000`,
    Note that not all tweets that are searched will be `in_reply_to`
    specified tweet. If `-s` is greater than 1000; please set `-w` to `on`.
    Free tier twitter API limits at 1000 per 15 mins.

* **wait_on_rate_limit `-w`**:

    Wait to retrieve more tweets once API limitations are exceeded.
    Can be either `on` or `off`. Default `off`.

* **big_query `-bq`**:

    Use to Google Big Query to store our tweets. Default `on`.
    Alternative option `off`.
    The data stored on BigQuery will automatically update the
    dashboard on Google Data Studios.

    OAuth GCP key required. Place and rename BigQuery key file as `gbq_key.json` in `src` folder.

    (Requires GCP - BigQuery and Data Studios)

*e.g.* `https://twitter.com/FallGuysGame/status/1308794965909295104 -f pickle -s 2000 -w on`

#### Embedded

Returns the specified tweet. As an html string for embedding into the Dash app.

#### Pipeline

The pipeline runs `get_replies.py` and `preprocessing.py` to produce a dashboard
that displays the nps stats for the tweet as a flask web app.

#### Data is saved to disk

The saved data retrieved from the Twitter API can be accessed as a csv (default)
file located at `../data/raw/replies_to_<twitter_id>.csv`

### Process the data

Run `preprocessing.py` and input the twitter thread id. It will check the csv files from the previous step, create additional columns for `processed_text` (Stop words are removed, words tokenized), `stemmed` (words are reduced to their root word, e.g. *likeable* become *like*), `sentiment_score` (performed on `processed_text` a signed float value which determines the overall sentiment of the tweet, where negative values have negative sentiment, and positive values have positive sentiment), `sentiment_score_stemmed` (similar to `sentiment_score`, but performed on stemmed words).

The `language` column originally only displays language codes such as `en`, `und`, `es` *.etc*. This is not easily recognised by those unfamiliar, and will be parsed to display the full language name.
The conversion dictionary is generated from scraping [this](https://www.sitepoint.com/iso-2-letter-language-codes/) table.

The result will be a `pickle` file (serialized python native data storage). The decision to create a `pickle` instead of csv, is that the datatypes of the original dataset is also stored, and will speed up reading time during the analysis step.

## Analysis

**Disclaimer: The notebook will be analyzing Twitter data, data may contain offensive language. This may be upsetting to some people. The project owner holds no responsibility for any damages it may cause to users (mentally and physically). Please view at your own discretion**

Please see the `notebook` folder for exploratory data analysis (EDA)
of the dataset (post processing).

`EDA.ipynb`:

Numbers 1-3 look at the three sample datasets.

`testing_plotly_layout.ipynb`:

Explores how to make graphs with `plotly` for integration into dash.

## Dashboards

* `app.py`:

Dash is a package developed by the people at `plotly`.
This script hosts locally a dashboard application which presents
visualizations of the twitter dataset generated by the pipeline.

* `google data studio`:

Uploading the datasets to Google Big Query, allows easy integration with google data studio. I have made an example [dashboard](https://datastudio.google.com/reporting/4354ab1f-d0b1-4a47-b37f-69d46ab639ab) that displays the sentiment distribution of replies to
tweets that I have tested on.

**Generating your own `ini` file for `gbq_table_path.ini`.**

```
[GBQ_PATH]
project_id=YOUR_PROJECT_ID
table_name=YOUR_DATASET_NAME.YOUR_TABLE_NAME
```

**Edit code without `gbq_table_path.ini` file**

  **Change from:**

  ```
  path_to_table_info = 'gbq_table_path.ini'
  CONFIG = configparser.ConfigParser()
  CONFIG.read(path_to_table_info)
  project_id = CONFIG['GBQ_PATH']['project_id']
  table_name = CONFIG['GBQ_PATH']['table_name']
  ```

  **to:**

  ```
  project_id = 'YOUR_PROJECT_ID'
  table_name = 'YOUR_DATASET_NAME.YOUR_TABLE_NAME'
  ```

## Additional files

* `tweepy_attributes.txt`:

    Contains the full list of attributes that can be
    extracted from the Twitter API.
    Use it as a reference to customize the `tweet_fields_of_interest`
    in `get_replies.py`.

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
