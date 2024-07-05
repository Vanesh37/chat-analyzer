
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
import emoji
from collections import Counter

extract=URLExtract()

def fetch_stats(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    num_messages = df.shape[0] # number of messages , words
    words = []
    for message in temp['message']:
        words.extend(message.split())

    num_media_msg = df[df['message']=='<Media omitted>\n'].shape[0] #media shared

    links=[]
    for message in temp['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_msg,len(links)

def most_busy_users(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    x = temp['user'].value_counts().head()

    temp=round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'user': 'name', 'count': 'percent'})
    return x,temp

def create_wordcloud(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    wc=WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    df_wc=wc.generate(temp['message'].str.cat(sep=" "))

    return df_wc

def most_common_words(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    words = []

    for message in temp['message']:
        words.extend(message.split())

    from collections import Counter

    most_cmn_df= pd.DataFrame(Counter(words).most_common(25))
    return most_cmn_df

def emoji_helper(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != 'overall':
        df = df[df['user'] == selected_user]

    user_heatmap=df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)
    return  user_heatmap
