import streamlit as st
import matplotlib.pyplot as plt
import preprocessor
from helper import *


def whatsapp():
    uploaded_file = st.sidebar.file_uploader("Upload Chat File")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        st.title('WhatsApp Chat Analysis')
        st.dataframe(df, width=1000, height=500)

        # fetch unique users
        user_list = df['user'].unique().tolist()
        user_list.sort()
        user_list.insert(0, "overall")

        selected_user = st.sidebar.selectbox("show analysis wrt", user_list)

        if st.sidebar.button("show analysis"):

            num_messages, words, num_media_messages, num_links = fetch_stats(
                selected_user, df)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Total messages")
                st.title(num_messages)
            with col2:
                st.header("Total words")
                st.title(words)
            with col3:
                st.header("Media shared")
                st.title(num_media_messages)
            with col4:
                st.header("links shared")
                st.title(num_links)

            # finding the busiest user in the group(group level)
            if selected_user == 'overall':
                st.title('Most Busy Users')
                x, new_df = most_busy_users(df)
                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values, color='red')
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)
                with col2:
                    st.dataframe(new_df)

            # WordCloud
            st.title("WordCloud")
            df_wc = create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # most common words
            st.title("Common Words")
            most_common_df = most_common_words(selected_user, df)

            st.dataframe(most_common_df)

            # Preprocess the data
            df = preprocess(data)

            # Check if there are still any <Media omitted> or group_notifications messages
            if df.empty:
                st.write("No valid messages found.")
            else:
                # Perform sentiment analysis
                sentiments = perform_sentiment_analysis(df['message'])

                # Add sentiment to DataFrame
                df['sentiment'] = sentiments

                # Aggregate sentiments for overall chat mood
                overall_sentiment = df['sentiment'].value_counts().idxmax()

                # Reset index to get continuous numbering
                df.reset_index(drop=True, inplace=True)
                df.index = df.index + 1

                # Display data
                st.header('WhatsApp Sentiment Analysis')
                st.write(df[['user', 'message', 'sentiment']])

                # Display overall mood of the chat
                st.header('Overall Mood of the Chat')
                st.write(
                    f"The overall mood of the chat is {overall_sentiment.lower()}.")
