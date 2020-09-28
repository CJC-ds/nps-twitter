from get_replies import main as gr
from preprocessing import main as prep
from get_embedded import main as ge

class data_paths:
    def __init__(self, tweet_id, twitter_user_id, file_format=('csv', 'pickles')):
        self.file_format = file_format
        self.tweet_id = tweet_id
        self.twitter_user_id = twitter_user_id
        self.raw_data_path = '../data/raw/'+str(tweet_id)+file_format[0]
        self.processed_data_path = '../data/processed/replies_to_'+str(tweet_id)+file_format[1]

    def set_file_format(self, raw_file_format, processed_file_format):
        self.file_format = (raw_file_format, processed_file_format)
        self.set_raw_data_path(raw_file_format)
        self.set_processed_data_path(processed_file_format)

    def set_raw_data_path(self, raw_file_format):
        self.raw_data_path = '../data/raw/'+str(self.tweet_id)+self.file_format[0]
    
    def set_processed_data_path(self, processed_file_format):
        self.processed_data_path = '../data/processed/replies_to_' + \
            str(tweet_id)+self.file_format[1]

def main():
    try:
        twitter_user, tweet_id = gr()
    except Exception as e:
        print(e)
        print('Error in retrieving tweets.')
        exit()
    prep(tweet_id)
    dp = data_paths(tweet_id=tweet_id, twitter_user_id=twitter_user)
    tweet_html = ge(tweet_id)

if __name__=='__main__':
    main()
