import pandas as pd
from glob import glob
import pickle
import itertools as it
import re
from google.oauth2 import service_account
import pandas_gbq
import configparser

path_to_table_info = 'gbq_table_path.ini'
CONFIG = configparser.ConfigParser()
CONFIG.read(path_to_table_info)
project_id = CONFIG['GBQ_PATH']['project_id']
table_name = CONFIG['GBQ_PATH']['table_name']
credentials = service_account.Credentials.from_service_account_file(
    'gbq_key.json')

import google.cloud.bigquery_storage_v1.client
from functools import partialmethod

# Set a two hours timeout
google.cloud.bigquery_storage_v1.client.BigQueryReadClient.read_rows = partialmethod(google.cloud.bigquery_storage_v1.client.BigQueryReadClient.read_rows, timeout=3600*2)

def make_tweet_id_df(id, df):
    l = list(it.repeat(id, df.shape[0]))
    s = pd.Series(l, name='og_tweet_id')
    new_df = pd.concat([s.to_frame(), df], axis=1)
    new_df.drop('index', axis=1, inplace=True)
    return new_df

def upload_all_archived():
    path = '../data/processed/'
    files = '*.pickle'
    full_path = path + files
    filenames = glob(full_path)
    dfs = [pd.read_pickle(f) for f in filenames]
    tweet_ids = [int(s) for f in filenames for s in re.split(r'; |, |\\|\.', f) if s.isdigit()]
    new_dfs = [make_tweet_id_df(id, df) for df, id in zip(dfs, tweet_ids)]
    new_df = pd.concat(new_dfs)
    pandas_gbq.to_gbq(
        new_df,
        table_name,
        project_id=project_id,
        if_exists='replace',
        credentials=credentials)

def upload_specified_dataset(tweet_id):
    path = '../data/processed/'
    file_path = path + tweet_id +'.pickle'
    df = pd.read_pickle(file_path)
    new_df = make_tweet_id_df(int(tweet_id), df)
    pandas_gbq.to_gbq(
        new_df,
        table_name,
        project_id=project_id,
        if_exists='append',
        credentials=credentials)

def has_tweet_id(tweet_id):
    q = """
    SELECT og_tweet_id
    FROM twitter.tweets
    WHERE og_tweet_id = {}
    """.format(tweet_id)
    df = pandas_gbq.read_gbq(
        q,
        project_id=project_id,
        credentials=credentials
    )
    if df.shape[0] >= 1:
        return True
    else:
        return False
    return q


def main(*args):
    try:
        tweet_id = args[0]
        if has_tweet_id(tweet_id) == False:
            upload_specified_dataset(tweet_id)
            print('uploaded specified tweet: '+str(args[0])+'.')
        else:
            print('tweet_id already exists on GBQ.')
            print('Replacing table instead...')
            upload_all_archived()
            print('uploaded all archived.')
    except:
        upload_all_archived()
        print('uploaded all archived.')


if __name__=='__main__':
    main()
