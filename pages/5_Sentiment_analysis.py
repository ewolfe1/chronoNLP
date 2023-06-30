import streamlit as st
state = st.session_state
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
from scripts import tools, saproc, getdata
tools.page_config()
tools.css()

# load data
if 'init' not in st.session_state:
    ready = getdata.init_data()
else:
    ready= True

if ready:
    df_filtered = state.df_filtered

    # process SA with Vader
    df_filtered = saproc.get_sa(df_filtered)

    # placeholder for status updates
    placeholder = st.empty()

    # header
    st.subheader('Sentiment analysis')
    getdata.df_summary_header()

    # box plots
    placeholder.markdown('*. . . Visualizing data . . .*\n\n')

    # sect 1
    sent_btn = st.radio('Text to analyze', ['Mean of all sources','Plot top 5 individual sources'], horizontal=True, label_visibility="hidden")
    if 'all' in sent_btn:
        sent_query = 'all'
    else:
        sent_query = 'individual'

    st.markdown("### Sentiment over time")
    st.caption("Distribution of mean sentiment by month. Scale: 1.0 is most positive, -1.0 is most negative.")

    sent_topic_plot = saproc.get_topic_plot(df_filtered, sent_query, 'compound')
    st.plotly_chart(sent_topic_plot, use_container_width=True)

    # polarity_plot = saproc.get_topic_plot(df_filtered, sent_query, 'polarity')
    # st.plotly_chart(polarity_plot, use_container_width=True)

    # subjectivity_plot = saproc.get_topic_plot(df_filtered, sent_query, 'subjectivity')
    # st.plotly_chart(subjectivity_plot, use_container_width=True)

    # sect 2
    st.markdown("### Sentiment distribution by source")

    st.caption("Distribution of sentiment within the top five sources. Scale: 1.0 is most positive, -1.0 is most negative.")

    sent_boxplot = saproc.get_sent_boxplot(df_filtered)
    st.plotly_chart(sent_boxplot, use_container_width=True)

    # sect 3
    placeholder.markdown('*. . . Evaluating article sentiment . . .*\n\n')

    # articles by sentiment
    with st.expander("Top articles by sentiment"):

        st.caption("View articles by VADER sentiment analysis score. Scale: 1.0 is most positive, -1.0 is most negative.")
        sa_btn = st.radio('', ['Positive','Negative'], horizontal=True)

        if sa_btn == 'Positive':
            st.markdown(f'10 articles with most positive sentiment analysis scores')
            sa_df = saproc.get_sa_markdown(df_filtered, False)
        else:
            st.markdown(f'10 articles with most negative sentiment analysis scores')
            sa_df = saproc.get_sa_markdown(df_filtered, True)

        sa_head = st.columns([1,2,2,1,1])
        sa_head[0].markdown('**Source**')
        sa_head[1].markdown('**Label**')
        sa_head[2].markdown('**UniqueID**')
        sa_head[3].markdown('**Published date**')
        sa_head[4].markdown('**VADER score**')

        for i,r in sa_df.iterrows():
            sa_cols = st.columns([1,2,2,1,1])
            sa_cols[0].markdown(f'{r.source}')
            sa_cols[1].markdown(f'{r.label}')
            sa_cols[2].markdown(f'{r.uniqueID}')
            sa_cols[3].markdown(f'{r.cleandate}')
            sa_cols[4].markdown(f'{r.compound}')

    with st.expander('About this page'):

        st.markdown("### References")
        st.caption('[1] Jochen Hartmann, "Emotion English DistilRoBERTa-base". https://huggingface.co/j-hartmann/emotion-english-distilroberta-base/, 2022.')

    placeholder.empty()
