import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import json
import dash_table
from pipeline import main as pipe

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def load_twitter_data(tweet_id):
    data_path = '../data/processed/'
    full_data_path = data_path + str(tweet_id) + '.pickle'
    df = pd.read_pickle(full_data_path)
    return df

def load_src_tweet(tweet_id):
    data_path = '../data/embeded_tweets/'
    full_data_path = data_path + 'tweet_' + str(tweet_id) + '.json'
    with open(full_data_path) as json_file:
        data = json.load(json_file)
    return data['html']

def get_language_dict():
    import requests
    import lxml.html as lh
    # Scrape from the language code table at the url below
    language_code_url = 'https://www.sitepoint.com/iso-2-letter-language-codes/'
    r = requests.get(language_code_url)
    doc = lh.fromstring(r.content)
    # tr elements hold table rows. We can locate them via the xpath.
    tr_elements = doc.xpath('//tr')
    # Create a list of all the text content for each table row element.
    content = [t.text_content() for t in tr_elements]
    # Column names are found at content[0], only interested in content (starting at element 1)
    # Remove the '\n' padding on the left and right of the string
    # Split the string on the '\n' delimiter
    parsed_content = [c.lstrip('\n').rstrip('\n').split('\n') for c in content[1:]]
    # Unpack the parsed content
    k, v = zip(*parsed_content)
    # Lower case the code string to match the code in our twitter data.
    v = [val.lower() for val in v]
    language_dict = {val:key for key, val in zip(k,v)}
    language_dict['und'] = 'Undetermined'
    return language_dict

def translate_lang_code(dataframe):
    lang_dict = get_language_dict()
    dataframe['lang'] = dataframe['lang'].replace(lang_dict, regex=True)
    return dataframe

def get_english_only(dataframe):
    df_en = dataframe[dataframe['lang'].str.contains('English')]\
    .reset_index(drop=True)\
    .copy()
    return df_en

def remove_neutral(dataframe):
    df_not_neut = df.drop(df[((df['sent_class_stemmed']=='neutral') |
        (df['sent_class']=='neutral'))].index, axis=0)\
        .reset_index(drop=True)\
        .copy()
    df_not_neut['sent_class_stemmed'].cat.remove_unused_categories(inplace=True)
    df_not_neut['sent_class'].cat.remove_unused_categories(inplace=True)
    return df_not_neut

def calculate_frequencies(dataframe):
    frequencies = ['min', 'H']
    engage_freq = [dataframe.groupby([
        pd.Grouper(key='created_at', freq=f)])\
    .size()\
    .reset_index(name='count')\
    .set_index('created_at') for f in frequencies]
    rate = ['per minute','per hour']
    data = [go.Scatter(x=engage.index, y=engage['count'], name=f)
            for engage, f in zip(engage_freq, rate)]
    return data

def get_top_words(dataframe):
    import re
    words = df_en['processed_text'].dropna()\
    .apply(lambda x: pd.value_counts(re.findall('([\s]\w+[\s])',' '.join(x))))\
    .sum(axis=0)\
    .to_frame()\
    .reset_index()\
    .sort_values(by=0, ascending=False)
    words.columns = ['word', 'occurences']
    words.reset_index(inplace=True, drop=True)
    return words

def get_summary_table(dataframe):
    summary_df = dataframe[['sentiment_score', 'sentiment_score_stemmed']]\
    .describe()\
    .copy()
    summary_df['metric'] = summary_df.index.tolist()
    summary_df = summary_df[['metric', 'sentiment_score', 'sentiment_score_stemmed']]
    return summary_df
#-----------------------------------------------------------------------------
# TODO: <below are current placeholders to test the application>
# Using call backs ask user for tweet link.
# Parse tweet link and check if data is on disk.
# If data not on disk, call the pipeline to retrieve data.
# pass the tweet_id again to display graphs
tweet_id = 1308853560411656197
df = load_twitter_data(tweet_id)
df = translate_lang_code(df)
emb_tweet = load_src_tweet(tweet_id)
#-----------------------------------------------------------------------------

# fig1 = <TODO: plot sentiment distribution>
df_en = get_english_only(df)
fig1 = go.Figure()
fig1.add_trace(
    go.Histogram(
        x=df_en['sentiment_score_stemmed'],
        name='stemming',
        xbins=dict(
            start=-3.0,
            end=3,
            size=0.5
        )
    )
)
fig1.add_trace(
    go.Histogram(
        x=df_en['sentiment_score'],
        name='no stemming',
        xbins=dict(
            start=-3.0,
            end=3.0,
            size=0.5
        )
    )
)
fig1.update_layout(
    title='Engagement sentiment score distribution',
    xaxis_title='Sentiment scores',
    yaxis_title='Number of Tweets',
    xaxis_tickangle=-45,
    barmode='overlay'
)
fig1.update_traces(opacity=0.75)

# fig2 = <TODO: plot sent class 1>
fig2 = make_subplots(
    rows=1, cols=2,
    subplot_titles=[
        'Sentiment classification distribution<br>(using stemmed words)',
        'Sentiment classification distribution<br>(without stemmed words)'
    ],
    y_title='Number of tweets'
)
fig2.add_trace(
    go.Bar(
        x=df_en['sent_class_stemmed'].value_counts().index,
        y=df_en['sent_class_stemmed'].value_counts(),
        name='stemmed',
        marker=dict(
            colorscale='Viridis',
            color = df_en['sent_class_stemmed'].value_counts())
    ),
    row=1, col=1
)
fig2.add_trace(
    go.Bar(
        x=df_en['sent_class'].value_counts().index,
        y=df_en['sent_class'].value_counts(),
        name='not stemmed',
        marker=dict(
            colorscale='Viridis',
            color = df_en['sent_class'].value_counts())
    ),
    row=1, col=2
)
fig2.update_layout(showlegend=False)
# fig3 = <TODO: plot sent class 2>
fig3 = go.Figure()
fig3.add_trace(
    go.Bar(
        x=df_en['sent_class_stemmed'].value_counts().index,
        y=df_en['sent_class_stemmed'].value_counts(),
        name='stemmed')
    )
fig3.add_trace(
    go.Bar(
        x=df_en['sent_class'].value_counts().index,
        y=df_en['sent_class'].value_counts(),
        name='not stemmed')
    )
fig3.update_layout(
    title='Engagement sentiment class distribution',
    xaxis_title='Sentiment class',
    yaxis_title='Number of Tweets'
)
# fig4 = <TODO: plot pies>
df_not_neut = remove_neutral(df_en)
labels = df_not_neut['sent_class_stemmed'].value_counts().index.tolist()
fig4 = make_subplots(1, 2, specs=[[{'type':'domain'},{'type':'domain'}]],
                    subplot_titles=[
                        'Sentiment class distribution<br>(with stemmed words)',
                        'Sentiment class distribution<br>(without stemmed words)'
                    ])
fig4.add_trace(go.Pie(labels=labels, values=df_not_neut['sent_class_stemmed'].value_counts(),
              name='stemmed'), row=1, col=1)
fig4.add_trace(go.Pie(labels=labels, values=df_not_neut['sent_class'].value_counts(),
              name='not stemmed'), row=1, col=2)

# fig5 = <TODO: rate of engagement>
fig5 = make_subplots(specs=[[{"secondary_y": True}]])
data = calculate_frequencies(df)
fig5.add_trace(
    data[0],
    secondary_y=True,
)

fig5.add_trace(
    data[1],
    secondary_y=False,
)

fig5.update_layout(
    title_text='Tweet audience engagement',
    xaxis_tickformat = '%-d-%-m-%Y<br>%-I:%M %p'
)
fig5.update_yaxes(title_text="Replies<br>(per hour)", secondary_y=False)
fig5.update_yaxes(title_text="Replies<br>(per minute)", secondary_y=True)

# fig6 = <TODO: plot language distribution>
fig6 = go.Figure(
    data=go.Bar(
    x=df['lang'].value_counts().index[:8],
    y=df['lang'].value_counts().head(8),
    marker=dict(
        colorscale='Viridis',
        color = df['lang'].value_counts().head(7),
        colorbar=dict(
            title='Number of Tweets'))))
fig6.update_layout(
    title='Engagement language distribution',
    xaxis_title='Language',
    yaxis_title='Number of Tweets',
    xaxis_tickangle=-45)

# fig7 = <TODO: plot top words used>
words = get_top_words(df_en)
fig7 = go.Figure()
fig7.add_trace(
    go.Bar(
        x=words.head(20)['word'],
        y=words.head(20)['occurences'],
        marker=dict(
            colorscale='Viridis',
            color = df_en['sent_class_stemmed'].value_counts(),
            colorbar=dict(title='usage')
        )
    )
)
fig7.update_layout(
    title='Top 20 words used in replies',
    xaxis_title='Words',
    yaxis_title='Usage count',
    xaxis_tickangle=-45
)

app.layout = html.Div(
    children=[
        html.H1(children='NPS Tweet analysis on replies'),
        html.Iframe(srcDoc=emb_tweet, style={
            'height': 410,
            'width': 500
        }),
        html.H2(children='Sentiment distribution (en)'),
        dash_table.DataTable(
            id='table',
            columns = [{'name': i, 'id': i} for i in get_summary_table(df_en).columns],
            data = get_summary_table(df_en).to_dict('records'),
            style_header={
                'backgroundColor':'rgb(230, 230, 230)',
                'fontWeight':'bold'
            },
            style_cell={
            'height': 'auto',
            # all three widths are needed
            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
            'whiteSpace': 'normal', 'textAlign':'left'}
        ),
        dcc.Graph(id='sent_dist1', figure=fig1),
        html.H2(children='Sentiment classification distribution (en)'),
        dcc.Graph(id='sent_class2', figure=fig3),
        #dcc.Graph(id='sent_class1', figure=fig2),
        dcc.Graph(id='sent_class_pie', figure=fig4),
        html.H2(children='Tweet engagement rate'),
        dcc.Graph(id='engagement_rate', figure=fig5),
        html.H2(children='Language Distribution'),
        dcc.Graph(id='lang_dist', figure=fig6),
        html.H2(children='Top 20 words most commonly used'),
        dcc.Graph(id='top_20', figure=fig7)
    ], style={'textAlign':'center'}
)

if __name__=='__main__':
    app.run_server(debug=True)
