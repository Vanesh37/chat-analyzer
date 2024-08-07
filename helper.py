import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import emoji
from collections import Counter
from nltk.corpus import stopwords

# Download and set stop words
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
extract = URLExtract()


def fetch_stats(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    num_messages = df.shape[0]  # number of messages , words
    words = []
    for message in temp['message']:
        words.extend(message.split())

    num_media_msg = df[df['message'] ==
                       '<Media omitted>\n'].shape[0]  # media shared

    links = []
    for message in temp['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_msg, len(links)


def most_busy_users(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    x = temp['user'].value_counts().head()

    temp = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'user': 'name', 'count': 'percent'})
    return x, temp


def create_wordcloud(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    wc = WordCloud(width=500, height=500, min_font_size=10,
                   background_color='white')
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc


def most_common_words(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df


def emoji_helper(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df


def monthly_timeline(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()[
        'message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline


def daily_timeline(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline


def week_activity_map(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()


def month_activity_map(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(
        index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return user_heatmap


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
