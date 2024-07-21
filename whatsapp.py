import streamlit as st
import matplotlib.pyplot as plt
import preprocessor
import helper
import seaborn as sns


def whatsapp():
    st.sidebar.title("whatsapp chat analyzer")

    uploaded_file = st.sidebar.file_uploader("Choose a file")
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        st.dataframe(df)
        # fetch unique usersssss

        user_list = df['user'].unique().tolist()
        user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "overall")
        selected_user = st.sidebar.selectbox("show analysis wrt", user_list)

        if st.sidebar.button("show analysis"):

            # stats analysis

            num_messages, words, num_media_msg, num_links = helper.fetch_stats(
                selected_user, df)
            st.title("Top Statistics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.header("Total Messages")
                st.title(num_messages)

            with col2:
                st.header("Total Words")
                st.title(words)

            with col3:
                st.header("Media Shared")
                st.title(num_media_msg)

            with col4:
                st.header("links Shared")
                st.title(num_links)

            # monthly timeline
            st.title("Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)

            fig, ax = plt.subplots()
            ax.plot(timeline['time'], timeline['message'], color='red')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # daily timeline
            st.title("Dialy Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['only_date'],
                    daily_timeline['message'], color='black')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

            # activity map

            st.title('Activity map')
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most busy day")
                busy_day = helper.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values)
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most busy month")
                busy_month = helper.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title("weekly activity map")
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

            # finding the busiet user in the group(Group level)

            if selected_user == 'overall':
                st.title('Most busy users')
                x, new_df = helper.most_busy_users(selected_user, df)

                fig, ax = plt.subplots()

                col1, col2 = st.columns(2)

                with col1:
                    ax.bar(x.index, x.values)
                    plt.xticks(rotation='vertical')
                    st.pyplot(fig)

                with col2:
                    st.dataframe(new_df)

            # wordcloud
            st.title("Word Cloud")
            df_wc = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # Most common words without stop words
            most_cmn_df = helper.most_common_words(selected_user, df)
            fig, ax = plt.subplots()
            ax.barh(most_cmn_df[0], most_cmn_df[1])
            plt.xticks(rotation='vertical')
            st.title('Most Common Words')
            st.pyplot(fig)
            st.dataframe(most_cmn_df)

            # emojii analysis
            emoji_df = helper.emoji_helper(selected_user, df)
            st.title('Emoji Analysis')
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(emoji_df)

            with col2:
                fig, ax = plt.subplots()
                ax.barh(emoji_df[0], emoji_df[1], color='skyblue')

                st.title('Emoji analysis')
                st.pyplot(fig)

            # Sentiment Analysis
            # Preprocess the data
            df = helper.preprocess(data)

            # Check if there are still any <Media omitted> or group_notifications messages
            if df.empty:
                st.write("No valid messages found.")
            else:
                # Perform sentiment analysis
                sentiments = helper.perform_sentiment_analysis(df['message'])

                # Add sentiment to DataFrame
                df['sentiment'] = sentiments

                # Aggregate sentiments for overall chat mood
                overall_sentiment = df['sentiment'].value_counts().idxmax()

                # Reset index to get continuous numbering
                df.reset_index(drop=True, inplace=True)
                df.index = df.index + 1

                # Display data
                st.header('Sentiment Analysis')
                st.write(df[['user', 'message', 'sentiment']])

                # Display overall mood of the chat
                st.header('Overall Mood of the Chat')
                st.write(
                    f"The overall mood of the chat is {overall_sentiment.lower()}.")
