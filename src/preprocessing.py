import pandas as pd
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import re

def read_data(tweet_id):
    data = pd.read_csv('tweet_dump/replies_to_'+tweet_id+'.csv')
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

def stem_words(dataframe_text_processed):
    ps = PorterStemmer()
    dataframe_text_processed['stemmed'] = dataframe_text_processed['processed_text']\
        .apply(lambda x: [ps.stem(i) for i in x if i != ''])
    return dataframe_text_processed

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
        print('Saving data file as '+str(tweet_id)+'.pickle')
        data.to_pickle('processed_tweets/'+str(tweet_id)+'.pickle')
        print('File successfully saved as '+str(tweet_id)+'.pickle')
    except Exception as e:
        print('Failed to save data to disk.')
        print(e)

if __name__=='__main__':
    main()
