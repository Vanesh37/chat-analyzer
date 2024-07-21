import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
extract = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    # fetch the total number of messages
    num_messages = df.shape[0]

    # fetch the total number of media
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch total links
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    # fetch the total number of words
    words = []
    for message in df['message']:
        words.extend(message.split())
    return num_messages, len(words), num_media_messages, len(links)


def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df


def create_wordcloud(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    wc = WordCloud(width=500, height=500, min_font_size=10,
                   background_color='white')
    df_wc = wc.generate(df['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open('stop_words_english.txt', 'r', encoding='utf-8')
    stop_words = f.read()
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notifications']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))

    return most_common_df


def preprocess(data):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:am|pm)\s-\s)'
    blocks = re.split(pattern, data)
    dates = [block.strip() for block in blocks[1::2]]
    messages = blocks[0::2]

    if len(messages) != len(dates):
        dates.append('')

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})
    df = df[df['message_date'] != '']

    users = []
    messages = []
    for message in df['user_message']:
        entry = re.split('([\w\W]+?):\s', message)
        if len(entry) > 1:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notifications')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message', 'message_date'], inplace=True)

    # Filter out messages containing <Media omitted> and group_notifications
    df = df[~df['message'].str.contains('<Media omitted>')]
    df = df[~df['user'].str.contains('group_notifications')]

    return df


# Function to perform sentiment analysis
nltk.download('vader_lexicon')


def perform_sentiment_analysis(messages):
    sia = SentimentIntensityAnalyzer()
    sentiments = []
    for message in messages:
        sentiment = sia.polarity_scores(message)
        if sentiment['compound'] >= 0.05:
            sentiment_type = 'Positive'
        elif sentiment['compound'] <= -0.05:
            sentiment_type = 'Negative'
        else:
            sentiment_type = 'Neutral'
        sentiments.append(sentiment_type)
    return sentiments
