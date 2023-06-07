import streamlit as st
state = st.session_state
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
# from transformers import pipeline
# classifier = pipeline("sentiment-analysis", model="michellejieli/emotion_text_classifier")
import statistics
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])

# sentiment analysis
@st.cache_data
def get_sa(df):

    nltk.download('vader_lexicon')
    analyzer = SentimentIntensityAnalyzer()

    def return_sa(text):
        try:
            return analyzer.polarity_scores(text)['compound']
        except AttributeError:
            return None

    # compound is weighted average; other measures are neg, neu, pos
    df['compound'] = df['full_text'].apply(lambda x: return_sa(x))

    return df


@st.cache_resource
def get_topic_plot(df, sent_query):

    fig = go.Figure()

    d_df = df.groupby('cleandate')
    sents = [g['compound'].mean() for n,g in d_df]

    if sent_query == 'all':
        # sum of all sources
        fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=sents,
                        name='All', mode='lines', line_shape='spline',line_smoothing=.2,
                         marker_color='black'
                ))

    else:
        # individual sources
        for source in df.source.value_counts(ascending=False)[:5].keys():

            d_df = df[df.source==source].groupby('cleandate')
            sents = [g['compound'].mean() for n,g in d_df]

            fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=sents,
                            name=source, mode='lines', line_shape='spline',line_smoothing=.2,
                             marker_color=(state.colors[list(df.source.unique()).index(source)])))

    fig.update_layout(yaxis_range=['-1.05','1.05'])

    return fig

@st.cache_resource
def get_sent_boxplot(df):

    fig = go.Figure()

    srcs = df.source.value_counts(ascending=False)[:5].keys()
    for source in srcs:

        # box plot
        # fig.add_trace(go.Box(y=df[df.source==source][sent_query].tolist(), name=source,jitter=0.4,pointpos=1.6,boxpoints='all',
        # marker_color=state.colors[list(df.source.unique()).index(source)]), showlegend=False))

        # violin plot
        fig.add_trace(go.Violin(y=df[df.source==source]['compound'].tolist(), box_visible=False,
        points='all',meanline_visible=True,meanline_color='black',
        fillcolor=colors[list(srcs).index(source)],
        opacity=0.6, x0=source))

    fig.update_layout(showlegend=False)
    return fig
