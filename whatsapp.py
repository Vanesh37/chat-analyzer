import streamlit as st
import matplotlib.pyplot as plt
import preprocessor
import helper
import seaborn as sns
from fpdf import FPDF
import os


def whatsapp():
    st.sidebar.title("WhatsApp Chat Analyzer")

    uploaded_file = st.sidebar.file_uploader("Choose a file")

    # Initialize session state variables
    if 'monthly_timeline' not in st.session_state:
        st.session_state.monthly_timeline = False
    if 'daily_timeline' not in st.session_state:
        st.session_state.daily_timeline = False
    if 'activity_map' not in st.session_state:
        st.session_state.activity_map = False
    if 'busy_users' not in st.session_state:
        st.session_state.busy_users = False
    if 'wordcloud' not in st.session_state:
        st.session_state.wordcloud = False
    if 'common_words' not in st.session_state:
        st.session_state.common_words = False
    if 'emoji_analysis' not in st.session_state:
        st.session_state.emoji_analysis = False
    if 'sentiment_analysis' not in st.session_state:
        st.session_state.sentiment_analysis = False

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        data = bytes_data.decode("utf-8")
        df = preprocessor.preprocess(data)

        st.dataframe(df)

        # Fetch unique users
        user_list = df['user'].unique().tolist()
        if 'group_notification' in user_list:
            user_list.remove('group_notification')
        user_list.sort()
        user_list.insert(0, "overall")

        selected_user = st.sidebar.selectbox(
            "Show analysis with respect to", user_list)

        num_messages, words, num_media_msg, num_links = 0, 0, 0, 0

        if st.sidebar.button("Show Analysis"):
            # Stats Analysis
            num_messages, words, num_media_msg, num_links = helper.fetch_stats(
                selected_user, df)
            st.session_state.num_messages = num_messages
            st.session_state.words = words
            st.session_state.num_media_msg = num_media_msg
            st.session_state.num_links = num_links

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
                st.header("Links Shared")
                st.title(num_links)

            # Monthly Timeline Plot
            timeline = helper.monthly_timeline(selected_user, df)
            fig1, ax1 = plt.subplots()
            ax1.plot(timeline['time'], timeline['message'], color='red')
            ax1.set_title("Monthly Timeline")
            ax1.set_xlabel("Time")
            ax1.set_ylabel("Messages")
            plt.xticks(rotation='vertical')

            # Store in session state
            st.session_state.fig1 = fig1

            # Daily Timeline Plot
            daily_timeline = helper.daily_timeline(selected_user, df)
            fig2, ax2 = plt.subplots()
            ax2.plot(daily_timeline['only_date'],
                     daily_timeline['message'], color='black')
            ax2.set_title("Daily Timeline")
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Messages")
            plt.xticks(rotation='vertical')

            # Store in session state
            st.session_state.fig2 = fig2

            # Most Busy Day Plot
            busy_day = helper.week_activity_map(selected_user, df)
            fig3, ax3 = plt.subplots()
            ax3.bar(busy_day.index, busy_day.values)
            ax3.set_title("Most Busy Day")
            ax3.set_xlabel("Day of the Week")
            ax3.set_ylabel("Messages")
            plt.xticks(rotation='vertical')

            # Store in session state
            st.session_state.fig3 = fig3

            # Most Busy Month Plot
            busy_month = helper.month_activity_map(selected_user, df)
            fig4, ax4 = plt.subplots()
            ax4.bar(busy_month.index, busy_month.values, color='orange')
            ax4.set_title("Most Busy Month")
            ax4.set_xlabel("Month")
            ax4.set_ylabel("Messages")
            plt.xticks(rotation='vertical')

            # Store in session state
            st.session_state.fig4 = fig4

            # Weekly Activity Heatmap
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig5, ax5 = plt.subplots()
            sns.heatmap(user_heatmap, ax=ax5)
            ax5.set_title("Weekly Activity Map")

            # Store in session state
            st.session_state.fig5 = fig5

            # Most Busy Users (Group Level)
            if selected_user == 'overall':
                x, new_df = helper.most_busy_users(selected_user, df)
                fig6, ax6 = plt.subplots()
                ax6.bar(x.index, x.values)
                ax6.set_title("Most Busy Users")
                ax6.set_xlabel("Users")
                ax6.set_ylabel("Message Count")
                plt.xticks(rotation='vertical')

                # Store in session state
                st.session_state.fig6 = fig6
                st.session_state.new_df = new_df

            # Word Cloud Plot
            df_wc = helper.create_wordcloud(selected_user, df)
            fig7, ax7 = plt.subplots()
            ax7.imshow(df_wc)
            ax7.set_title("Word Cloud")
            ax7.axis("off")

            # Store in session state
            st.session_state.fig7 = fig7

            # Most Common Words Plot
            most_cmn_df = helper.most_common_words(selected_user, df)
            fig8, ax8 = plt.subplots()
            ax8.barh(most_cmn_df[0], most_cmn_df[1])
            ax8.set_title("Most Common Words")
            ax8.set_xlabel("Word Frequency")
            ax8.set_ylabel("Words")
            plt.xticks(rotation='vertical')

            # Store in session state
            st.session_state.fig8 = fig8
            st.session_state.most_cmn_df = most_cmn_df

            # Emoji Analysis Plot
            emoji_df = helper.emoji_helper(selected_user, df)
            fig9, ax9 = plt.subplots()
            ax9.barh(emoji_df[0], emoji_df[1], color='skyblue')
            ax9.set_title("Emoji Analysis")
            ax9.set_xlabel("Frequency")
            ax9.set_ylabel("Emoji")

            # Store in session state
            st.session_state.fig9 = fig9
            st.session_state.emoji_df = emoji_df

            # Sentiment Analysis
            sentiments = helper.perform_sentiment_analysis(df['message'])
            df['sentiment'] = sentiments
            overall_sentiment = df['sentiment'].value_counts().idxmax()

            # Store in session state
            st.session_state.df = df
            st.session_state.overall_sentiment = overall_sentiment

    # Button for Monthly Timeline
    if uploaded_file is not None and "fig1" in st.session_state:
        if st.button("Monthly Timeline"):
            st.session_state.monthly_timeline = not st.session_state.monthly_timeline
        if st.session_state.monthly_timeline:
            st.pyplot(st.session_state.fig1)

    # Button for Daily Timeline
    if uploaded_file is not None and "fig2" in st.session_state:
        if st.button("Daily Timeline"):
            st.session_state.daily_timeline = not st.session_state.daily_timeline
        if st.session_state.daily_timeline:
            st.pyplot(st.session_state.fig2)

    # Button for Activity Map
    if uploaded_file is not None and "fig3" in st.session_state and "fig4" in st.session_state and "fig5" in st.session_state:
        if st.button("Activity Map"):
            st.session_state.activity_map = not st.session_state.activity_map
        if st.session_state.activity_map:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(st.session_state.fig3)
            with col2:
                st.pyplot(st.session_state.fig4)
            st.pyplot(st.session_state.fig5)

    # Button for Most Busy Users
    if uploaded_file is not None and "fig6" in st.session_state and selected_user == 'overall':
        if st.button("Most Busy Users"):
            st.session_state.busy_users = not st.session_state.busy_users
        if st.session_state.busy_users:
            col1, col2 = st.columns(2)
            with col1:
                st.pyplot(st.session_state.fig6)
            with col2:
                st.dataframe(st.session_state.new_df)

    # Button for Word Cloud
    if uploaded_file is not None and "fig7" in st.session_state:
        if st.button("Word Cloud"):
            st.session_state.wordcloud = not st.session_state.wordcloud
        if st.session_state.wordcloud:
            st.pyplot(st.session_state.fig7)

    # Button for Most Common Words
    if uploaded_file is not None and "fig8" in st.session_state:
        if st.button("Most Common Words"):
            st.session_state.common_words = not st.session_state.common_words
        if st.session_state.common_words:
            st.pyplot(st.session_state.fig8)
            st.dataframe(st.session_state.most_cmn_df)

    # Button for Emoji Analysis
    if uploaded_file is not None and "fig9" in st.session_state:
        if st.button("Emoji Analysis"):
            st.session_state.emoji_analysis = not st.session_state.emoji_analysis
        if st.session_state.emoji_analysis:
            st.pyplot(st.session_state.fig9)
            st.dataframe(st.session_state.emoji_df)

    # Button for Sentiment Analysis
    if uploaded_file is not None and "df" in st.session_state:
        if st.button("Sentiment Analysis"):
            # Reset index to get continuous numbering
            df = st.session_state.df
            df.reset_index(drop=True, inplace=True)
            df.index = df.index + 1

            # Display data
            st.write(df[['user', 'message', 'sentiment']])
            st.write(
                f"Overall Sentiment: {st.session_state.overall_sentiment}")
            sentiment_counts = st.session_state.df['sentiment'].value_counts(
                normalize=True) * 100
            sentiment_labels = sentiment_counts.index
            sentiment_sizes = sentiment_counts.values

            fig, ax = plt.subplots(figsize=(2, 2))
            ax.pie(
                sentiment_sizes,
                labels=sentiment_labels,
                autopct='%1.1f%%',
                colors=['#66b3ff', '#99ff99', '#ffcc99']
            )
            ax.axis('equal')

            st.pyplot(fig)

    # PDF Report Generation
    if uploaded_file is not None and st.sidebar.button("Generate Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Adding text content to PDF
        pdf.cell(200, 10, txt="WhatsApp Chat Analysis Report",
                 ln=True, align="C")
        pdf.ln(10)

        # Statistics Section
        pdf.cell(200, 10, txt="Top Statistics", ln=True, align="L")
        pdf.ln(5)
        pdf.cell(
            200, 10, txt=f"Total Messages: {st.session_state.num_messages}", ln=True, align="L")
        pdf.cell(
            200, 10, txt=f"Total Words: {st.session_state.words}", ln=True, align="L")
        pdf.cell(
            200, 10, txt=f"Media Shared: {st.session_state.num_media_msg}", ln=True, align="L")
        pdf.cell(
            200, 10, txt=f"Links Shared: {st.session_state.num_links}", ln=True, align="L")
        pdf.ln(10)

        # Save plots as images and add to PDF
        for i, fig in enumerate([st.session_state.fig1, st.session_state.fig2, st.session_state.fig3,
                                 st.session_state.fig4, st.session_state.fig5, st.session_state.fig6,
                                 st.session_state.fig7, st.session_state.fig8, st.session_state.fig9], start=1):
            if fig:
                img_path = f"temp_fig_{i}.png"
                fig.savefig(img_path)
                pdf.image(img_path, x=10, w=180)
                pdf.ln(10)
                # Clean up the image file after adding it to the PDF
                os.remove(img_path)

        # Save PDF file and provide a download button
        pdf_output_path = "chat_analysis_report.pdf"
        pdf.output(pdf_output_path)

        with open(pdf_output_path, "rb") as pdf_file:
            st.sidebar.download_button(
                label="Download Report",
                data=pdf_file,
                file_name=pdf_output_path,
                mime="application/pdf"
            )
