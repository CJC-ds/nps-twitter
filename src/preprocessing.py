from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import nltk.sentiment.vader as vd
import re

def read_data(tweet_id, file_format='csv'):
    """
    Concatenates the `tweet_id` to file_path string and retrieves
    the data from disk as a `pandas.DataFrame`.

    Args:
        tweet_id (string):
            The id of the tweet to look for on disk.
        file_format (string):
            File format to retrieve. Default \'.csv\'

    Returns:
        type: pandas.DataFrame

    Raises:
        Exception: ValueError, file format not recognized.
    """
    if file_format not in ['csv', 'pickle']:
        raise ValueError('File format not recognized.')
    if file_format=='pickle':
        data = pd.read_pickle('../data/raw/replies_to_'+tweet_id+'.pickle')
    else:
        data = pd.read_csv('../data/raw/replies_to_'+tweet_id+'.csv')
    return data

def remove_user_mention(dataframe):
    """
    All tweets are `in_reply_to` where the owner of the tweet
    is mentioned `@user` at the beginning of each tweet.
    This function removes all mentions.

    Args:
        dataframe (pandas.DataFrame): the dataframe which holds the twitter data
            in the `full_text` column.

    Returns:
        dataframe: the dataframe will have an updated full_text column
        with all mentions removed.

    Raises:
        Exception: full_text column not found in supplied pd.DataFrame.
    """
    if 'full_text' not in dataframe.columns.tolist():
        raise Exception('full_text column not found in dataframe.')

    dataframe['full_text'] = dataframe.full_text.apply(
        lambda x: re.sub('(@[A-Za-z0-9]+)', '', x)
    )
    dataframe['full_text'] = dataframe.full_text.apply(lambda x: x.lstrip())
    return dataframe

def remove_duplicate_tweets(dataframe):
    """
    In some cases users spam the same tweet at twitter threads.
    Removes duplicate tweets in the dataset.

    Args:
        dataframe (pandas.DataFrame):
            The dataframe which holds the twitter data.

    Returns:
        pandas.DataFrame: processed dataframe with duplicate rows removed.

    Raises:
        Exception: full_text column not found in supplied pd.DataFrame.
    """
    if 'full_text' not in dataframe.columns.tolist():
        raise Exception('full_text column not found in dataframe.')
    dataframe.drop_duplicates(subset='full_text', inplace=True)
    dataframe.reset_index(inplace=True)
    return dataframe

def remove_stop_words(dataframe, custom_stopwords=[]):
    """
    Stop words usually refer to the most common words in a language.
    e.g. 'to', 'from', 'a'.etc
    This function will filter these out from the dataset.

    Args:
        dataframe (pandas.DataFrame):
            The dataframe which holds the twitter data.

    Returns:
        pandas.DataFrame: processed dataframe with a new column `processed_text`.

    Raises:
        Exception: full_text column not found in dataframe.

    """
    if 'full_text' not in dataframe.columns.tolist():
        raise Exception('full_text column not found in dataframe.')
    additional = ['rt', 'rts', 'retweet']
    additional.extend(custom_stopwords)
    stop_words = set().union(stopwords.words('english'), additional)
    dataframe['processed_text'] = dataframe['full_text'].str.lower()\
        .str.replace('(@[a-z0-9]+)\w+',' ')\
        .str.replace('(http\S+)', ' ')\
        .str.replace('([^0-9a-z \t])',' ')\
        .str.replace(' +', ' ')\
        .apply(lambda x: [i for i in x.split() if not i in stop_words])
    return dataframe

def stem_words(dataframe):
    """
    In linguistics, a stem is part of a word that is common to all its
    inflected variants.
    This function converts all word tokens in the processed_text column
    of the twitter data (pandas.DataFrame) to its stemmed form.
    e.g. waiting, waited, waits --> wait.

    Args:
        dataframe (pandas.DataFrame):
            The dataframe that holds the twitter data.
            The dataframe must contain the processed_text column.

    Returns:
        pandas.DataFrame:
            A dataframe that holds the twitter data. Including a new
            column 'stemmed' holding stemmed word tokens of processed_text.

    Raises:
        Exception: processed_text column not found in dataframe.

    """
    if 'processed_text' not in dataframe.columns.tolist():
        raise Exception('processed_text column not found in dataframe.')
    ps = PorterStemmer()
    dataframe['stemmed'] = dataframe['processed_text']\
        .apply(lambda x: [ps.stem(i) for i in x if i != ''])
    return dataframe

def extract_sentiment(dataframe):
    """
    This function scores each word token in the tweet, combines
    the scores within a tweet to give an overall sentiment score.
    The scores for each tweet is appended as a new column 'sentiment_score'
    to the supplied dataframe and returned.

    Sentiment is extracted using the `Vader sentiment intensity
    analyzer`. A sentiment indicates the view or opinion
    expressed. This opinion can be positive or negative.
    It is represented as a floating point decimal, where 0
    indicates neutral sentiment, negative values for negative
    sentiments and positive for positive sentiments.

    Args:
        dataframe (pandas.DataFrame):
            The dataframe that holds the twitter data.
            The dataframe must contain the processed_text column.

    Returns:
        pd.DataFrame:
        A dataframe that holds the twitter data. Including a new
        column 'sentiment_score' holding the sum of compounded
        word tokens sentiment scores of processed_text.
    """
    sia = vd.SentimentIntensityAnalyzer()
    dataframe['sentiment_score'] = dataframe['processed_text']\
    .apply(
        lambda x: sum([
            sia.polarity_scores(i)['compound']
            for i in word_tokenize( ' '.join(x) )
        ])
    )
    return dataframe

def extract_sentiment_stemmed(dataframe):
    """
    Extracts the sentiment score from the stemmed token words
    in the `stemmed` column of the dataframe.

    Args:
        dataframe (pandas.DataFrame):
            a DataFrame that holds the twitter data.
            requires the `stemmed` column.

    Returns:
        pandas.DataFrame:
            a DataFrame that holds the twitter data and
            contains the 'sentiment_score_stemmed' column.

    Raises:
        Exception: unable to process sentiment_score_stemmed when
        `stemmed` column is not found.
    """
    if 'stemmed' not in dataframe.columns.tolist():
        raise Exception('Unable to process sentiment_score_stemmed\
        when `stemmed` column is not found.')
    sia = vd.SentimentIntensityAnalyzer()
    dataframe['sentiment_score_stemmed'] = dataframe['stemmed']\
    .apply(
        lambda x: sum([
            sia.polarity_scores(i)['compound']
            for i in word_tokenize( ' '.join(x) )
        ]))
    return dataframe

def categorize_sentiment(dataframe):
    """
    This function converts floating point decimal representations of
    the sentiment score and classifies them. The classifications are
    appended to the resulting dataframe as a column `sent_class`.

    Args:
        dataframe (pandas.DataFrame):
            a DataFrame that holds the twitter data.
            requires the `sentiment_score` and
            `sentiment_score_stemmed` columns.

    Returns:
        pandas.DataFrame:
            a DataFrame that holds the twitter data and
            contains the `sent_class` and `sent_class_stemmed`
            columns.

    Raises:
        Exception: Required columns sentiment_score and
         sentiment_score_stemmed not found in pandas.DataFrame.
    """
    if (('sentiment_score' not in dataframe.columns.tolist()) &
        ('sentiment_score_stemmed' not in dataframe.columns.tolist())):
        raise Exception('Required columns sentiment_score and\
         sentiment_score_stemmed not found in pandas.DataFrame.')
    def classify(col):
        sent_class = pd.cut(
            dataframe[col],
            [-3, -1.2, -0.05, 0.05, 1.2, 3],
            right=True,
            include_lowest=True,
            labels=[
                'strongly negative',
                'negative',
                'neutral',
                'positive',
                'strongly positive'
            ]
        )
        return sent_class
    dataframe['sent_class'] = classify('sentiment_score')
    dataframe['sent_class_stemmed'] = classify('sentiment_score_stemmed')
    return dataframe

def parse_twitter_date(dataframe):
    """
    The dates `created_at` retrieved from the Twitter API are
    difficult for pandas.DataFrame to recognize as proper dates.
    This function will parse the dates and change the `created_at`
    column from a dtype string/object into a datetime64.

    Args:
        dataframe (pandas.DataFrame):
            The dataframe that holds the twitter data.
            The column `created_at` is in its raw form (dtype object).

    Returns:
        pandas.DataFrame:
            An updated DataFrame with the `created_at` column
            properly displaying the date and assigned with the datetime64
            dtype.
    """
    from datetime import datetime
    def convert_time(time_string):
        new_datetime = datetime.strftime(
            datetime.strptime(
                time_string,
                '%a %b %d %H:%M:%S +0000 %Y'
            ),
            '%Y-%m-%d %H:%M:%S'
        )
        return new_datetime
    created_at = dataframe['created_at'].apply(lambda x: convert_time(x))
    created_at = pd.to_datetime(created_at)
    dataframe['created_at'] = created_at
    return dataframe

def main(*args):
    try:
        try:
            tweet_id = args[0]
        except:
            tweet_id = input('Initial tweet id: ')
        data = read_data(tweet_id)
        print('Found specified tweet document.\n')
    except:
        print('Specified tweet document id not found.\n')

    try:
        print('Removing mentions from tweets...')
        data = remove_user_mention(data)
        print('Successfully removed mentions from tweets.\n')
    except Exception as e:
        print(str(e) + '\n')

    try:
        print('Removing duplicate tweets...')
        data = remove_duplicate_tweets(data)
        print('Duplicate tweets removed successfully.\n')
    except Exception:
        print('Failed to remove duplicate tweets.\n')

    try:
        print('Parsing created_at time column...')
        data = parse_twitter_date(data)
        print('Date parsing succeeded.\n')
    except Exception:
        print('Failed to parse the created_at time column.\n')

    try:
        print('Removing stop words...')
        data = remove_stop_words(data)
        print('Stop words removed.')
        print('processed_text column added.\n')
    except Exception as e:
        print(e)
        print('Error in removing stop words.\n')

    try:
        print('Stemming words...')
        data = stem_words(data)
        print('Stemmed words.')
        print('stemmed column added.\n')
    except Exception as e:
        print(e)
        print('Error in stemming words.\n')

    try:
        print('Determining sentiment score...')
        data = extract_sentiment_stemmed(data)
        print('Sentiment scores assigned to stemmed words.')
        print('sentiment_score_stemmed column added.\n')
    except Exception as e:
        print(e)
        print('Error in calculating sentiment scores on stemmed words.\n')

    try:
        print('Determining stemmed sentiment scores...')
        data = extract_sentiment(data)
        print('Sentiment scores assigned.')
        print('sentiment_score column added.\n')
    except Exception as e:
        print(e)
        print('Error in calculating sentiment score\n')

    try:
        print('Categorizing sentiment scores...')
        data = categorize_sentiment(data)
        print('Categories assigned.')
        print('sent_class column added.')
        print('sent_class_stemmed column added.\n')
    except Exception as e:
        print('Error assigning sentiment categories.\n')

    try:
        print('Saving data file as '+str(tweet_id)+'.pickle')
        data.to_pickle('../data/processed/'+str(tweet_id)+'.pickle')
        print('File successfully saved as '+str(tweet_id)+'.pickle')
        print('Done.\n')
    except Exception as e:
        print('Failed to save data to disk.')
        print(e)

if __name__=='__main__':
    main()
