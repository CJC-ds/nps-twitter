import tweepy
import configparser
import urllib.parse
import json


def setup_api_config(path_to_credentials, wait_on_limit=False):
    """
    Handles setting up credentials to access the Twitter API via tweepy wrapper.

    Args:
    path_to_credentials (String):
        Path to the credentials.ini file location.

    Returns:
    api (tweepy.api.API):
        Twitter API wrapper object.
        See http://docs.tweepy.org/en/latest/api.html
    """
    # Configure the credentials
    CONFIG = configparser.ConfigParser()
    CONFIG.read(path_to_credentials)

    # Define each key
    consumer_key = CONFIG['API']['key']
    consumer_secret = CONFIG['API']['secret']
    access_token = CONFIG['Access']['token']
    access_token_secret = CONFIG['Access']['secret']

    auth = tweepy.OAuthHandler(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret)
    auth.set_access_token(
        key=access_token,
        secret=access_token_secret)
    api = tweepy.API(
        auth,
        wait_on_rate_limit=wait_on_limit,
        wait_on_rate_limit_notify=wait_on_limit
    )
    return api


def main(*args):
    path = 'credentials.ini'
    api = setup_api_config(path)
    print('Retrieving initial tweet for embedding..')
    result = api.get_oembed(id=args[0])
    storage_path = '../data/embeded_tweets/'
    file_name = storage_path+'tweet_'+str(args[0])+'.json'
    with open(file_name, 'w') as jfile:
        json.dump(result, jfile,
                  indent=4, separators=(', ', ': '), sort_keys=True)
    return result['html']


if __name__ == '__main__':
    main()
