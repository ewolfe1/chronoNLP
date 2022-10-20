import streamlit as st
state = st.session_state
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
# # import colorlover as cl
# colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])


@st.cache
def get_topic_plot(df, sent_query):
    fig = go.Figure()

    d_df = df.groupby('cleandate')
    sents = [g[sent_query].mean() for n,g in d_df]

    # sum of all sources
    fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=sents,
                    name='All', mode='lines+markers', connectgaps=True, line_shape='spline',line_smoothing=.2,
                     marker_color='black'
            ))

    # individual sources
    for source in df.source.unique():

        d_df = df[df.source==source].groupby('cleandate')
        sents = [g[sent_query].mean() for n,g in d_df]

        fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=sents,
                        name=source, mode='lines+markers', connectgaps=True, line_shape='spline',line_smoothing=.2,
                         marker_color=(state.colors[list(df.source.unique()).index(source)])))

    fig.update_layout(yaxis_range=['-1.05','1.05'])

    return fig

@st.cache
def get_sent_boxplot(df, sent_query):

    fig = go.Figure()

    for source in df.source.unique():

        # box plot
        # fig.add_trace(go.Box(y=df[df.source==source][sent_query].tolist(), name=source,jitter=0.4,pointpos=1.6,boxpoints='all',
        # marker_color=state.colors[list(df.source.unique()).index(source)]), showlegend=False))

        # violin plot
        fig.add_trace(go.Violin(y=df[df.source==source][sent_query].tolist(), box_visible=False, points='all',meanline_visible=True,meanline_color='black', fillcolor=colors[list(df.source.unique()).index(source)], opacity=0.6, x0=source))

    fig.update_layout(showlegend=False)
    return fig

# plot sentiment of multiple terms over time
def plot_sa_multiterm(df, searchterm_multi, sent_query):

    fig = go.Figure()

    for term in searchterm_multi.split(','):

        term = term.strip().lower()
        search_df = pd.DataFrame([r for i, r in df.iterrows() if term in r.clean_text + r.lemmas])

        d_df = search_df.groupby('cleandate')
        sents = [g[sent_query].mean() for n,g in d_df]

        # sum of all sources
        fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=sents,
                        name=term, mode='lines+markers', connectgaps=True, line_shape='spline',line_smoothing=.2
                         #marker_color=(state.colors[searchterm_multi.split(',').index(term)])
                ))

    fig.update_layout(yaxis_range=['-1.05','1.05'])

    return fig

@st.cache
def get_sent_boxplot_multiterm(df, searchterm_multi, sent_query):

    fig = go.Figure()

    for term in searchterm_multi.split(','):

        term = term.strip().lower()
        search_df = pd.DataFrame([r for i, r in df.iterrows() if term in r.clean_text + r.lemmas])

        # box plot
        # fig.add_trace(go.Box(y=df[df.source==source][sent_query].tolist(), name=source,jitter=0.4,pointpos=1.6,boxpoints='all',
        # marker_color=(state.colors[list(df.source.unique()).index(source)]), showlegend=False))

        # violin plot
        fig.add_trace(go.Violin(y=search_df[sent_query].tolist(), box_visible=False, points='all',meanline_visible=True,meanline_color='black', opacity=0.6, x0=term))
        # fillcolor=state.colors[list(df.source.unique()).index(source)],

    fig.update_layout(showlegend=False)
    return fig
