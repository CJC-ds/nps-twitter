from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import nltk.sentiment.vader as vd
import re

def read_data(tweet_id):
    data = pd.read_csv('../data/raw/replies_to_'+tweet_id+'.csv')
    return data

def remove_user_mention(data_series):
    data_series['full_text'] = data_series.full_text.apply(
        lambda x: re.sub('(@[A-Za-z0-9]+)', '', x)
    )
    data_series['full_text'] = data_series['full_text'].apply(lambda x: x.lstrip())
    return data_series

def remove_duplicate_tweets(dataframe):
    dataframe.drop_duplicates(subset='full_text', inplace=True)
    dataframe.reset_index(inplace=True)
    return dataframe

def remove_stop_words(dataframe):
    additional = ['rt', 'rts', 'retweet']
    stop_words = set().union(stopwords.words('english'), additional)
    dataframe['processed_text'] = dataframe['full_text'].str.lower()\
        .str.replace('(@[a-z0-9]+)\w+',' ')\
        .str.replace('(http\S+)', ' ')\
        .str.replace('([^0-9a-z \t])',' ')\
        .str.replace(' +', ' ')\
        .apply(lambda x: [i for i in x.split() if not i in stop_words])
    return dataframe

def stem_words(dataframe):
    ps = PorterStemmer()
    dataframe['stemmed'] = dataframe['processed_text']\
        .apply(lambda x: [ps.stem(i) for i in x if i != ''])
    return dataframe

def extract_sentiment(dataframe):
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
        sia = vd.SentimentIntensityAnalyzer()
        dataframe['sentiment_score_stemmed'] = dataframe['stemmed']\
        .apply(
            lambda x: sum([
                sia.polarity_scores(i)['compound']
                for i in word_tokenize( ' '.join(x) )
            ])
        )
        return dataframe

def categorize_sentiment(dataframe):
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

def main():
    try:
        tweet_id = input('Initial tweet id: ')
        data = read_data(tweet_id)
        print('Found specified tweet document.')
    except:
        print('Specified tweet document id not found.')

    try:
        print('Removing stop words...')
        data = remove_stop_words(data)
        print('Stop words removed.')
        print('processed_text column added.')
    except Exception as e:
        print('Error in removing stop words.')
        print(e)

    try:
        print('Stemming words...')
        data = stem_words(data)
        print('Stemmed words.')
        print('stemmed column added.')
    except Exception as e:
        print('Error in stemming words.')
        print(e)

    try:
        print('Determining sentiment score...')
        data = extract_sentiment_stemmed(data)
        print('Sentiment scores assigned to stemmed words.')
        print('sentiment_score_stemmed column added.')
    except Exception as e:
        print('Error in calculating sentiment scores on stemmed words.')
        print(e)

    try:
        print('Determining stemmed sentiment scores...')
        data = extract_sentiment(data)
        print('Sentiment scores assigned.')
        print('sentiment_score column added.')
    except Exception as e:
        print('Error in calculating sentiment score')
        print(e)

    try:
        print('Categorizing sentiment scores...')
        data = categorize_sentiment(data)
        print('Categories assigned.')
        print('sent_class column added.')
        print('sent_class_stemmed column added.')
    except Exception as e:
        print('Error assigning sentiment categories.')

    try:
        print('Saving data file as '+str(tweet_id)+'.pickle')
        data.to_pickle('../data/processed/'+str(tweet_id)+'.pickle')
        print('File successfully saved as '+str(tweet_id)+'.pickle')
    except Exception as e:
        print('Failed to save data to disk.')
        print(e)

if __name__=='__main__':
    main()
