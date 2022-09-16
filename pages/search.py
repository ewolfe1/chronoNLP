import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from datetime import datetime
from natsort import natsorted
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
import plotly.express as px
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# spacy
import spacy
from nltk import FreqDist
from sklearn.preprocessing import minmax_scale
from scripts import saproc, getdata
getdata.page_config()


@st.experimental_memo
def load_model():
      return spacy.load("en_core_web_sm")

nlp = load_model()

# plot a single term across multiple sources
@st.experimental_memo
def plot_term_by_source(df, searchterm, kwsearch_abs_btn):

    term = [w.lemma_ for w in nlp(searchterm.lower().strip())][0]

    fig = go.Figure()

    for source in df.source.unique():

        d_df = df[df.source==source].groupby('cleandate')
        kwsearch = [' '.join(g.lemmas).split().count(term) for n,g in d_df]
        kwcount = "{:,d}".format(sum(kwsearch))

        num_articles = len(df[df.source==source])

        # normalize data if requested
        if kwsearch_abs_btn == 'Normalized':
            kwsearch=([t/num_articles for t in kwsearch])

        fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=kwsearch,
                        name=f'{source} ({kwcount} total uses)', marker_color=(colors[list(df.source.unique()).index(source)])
                ))

    return fig

# plot multiple terms over time
@st.experimental_memo
def plot_terms_by_month(df, searchterm):

    fig_abs = go.Figure()
    fig_norm = go.Figure()

    d_df = df.groupby('cleandate')
    timeframe = [getdata.get_cleandate(g.iloc[0].date) for n,g in d_df]
    kw_df = pd.DataFrame({'date':timeframe})

    for term in searchterm.split(','):

        if ' ' not in term:
            term = [w.lemma_ for w in nlp(term.lower().strip())][0]
            total_uses = ' '.join(df.lemmas).count(term)

            kwsearch_abs = [' '.join(g.lemmas).count(term) for n,g in d_df]
            kwsearch_norm = [' '.join(g.lemmas).count(term)/len(g) for n,g in d_df]
        else:
        # print(term)
            total_uses = ' '.join(df.clean_text).count(term)

            kwsearch_abs = [' '.join(g.clean_text).count(term) for n,g in d_df]
            kwsearch_norm = [' '.join(g.clean_text).count(term)/len(g) for n,g in d_df]
            # normalize to data
        kwsearch_norm = minmax_scale(kwsearch_norm)

        # add to graph
        fig_abs.add_trace(go.Scatter(x=timeframe, y=kwsearch_abs,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch_abs))
        fig_norm.add_trace(go.Scatter(x=timeframe, y=kwsearch_norm,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch_norm))
        # add to df
        kw_df[f'{term} - Raw count'] = kwsearch_abs
        kw_df[f'{term} - Normalized'] = kwsearch_norm

    return fig_abs, fig_norm, kw_df

# load data
if 'init' not in state:
    getdata.init_data()

df_filtered = state.df_filtered

# placeholder for status updates
placeholder = st.empty()

# header
st.subheader('Search for keywords')
getdata.df_summary_header()

#tokenizer = state.tokenizer

# user-driven search
placeholder.markdown('*. . . Analyzing search terms . . .*\n\n')

st.write('View the frequency of one or more keywords over time.')

kw_cols = st.columns(2)
with kw_cols[0]:
    searchterm = st.text_input("Enter keyword(s), separated by a comma", value='covid-19')
    kwmethod_btn = st.radio('', ['Partial match','Exact match'], key='kwmethod', horizontal=True)
    kwsearch_btn = st.radio('View results as a ', ['Graph','Table'], key='kwsearch', horizontal=True)

kw_abs, kw_norm, kw_df = plot_terms_by_month(df_filtered, searchterm)

kw_tab1, kw_tab2, kw_tab3 = st.tabs(["Raw count", "Normalized", "Table"])

with kw_tab1:
    st.write('Raw count of keyword frequency over time')
    st.plotly_chart(kw_abs, use_container_width=True)
with kw_tab2:
    st.write('Keyword frequency over time, normalized relative to the time frequency (scale of 0 to 1).')
    st.plotly_chart(kw_norm, use_container_width=True)
with kw_tab3:
    st.write('Raw and normalized (scale of 0 to 1) frequency counts for each term.')
    st.write(kw_df)

    fn = '_'.join([t.lower().strip() for t in searchterm.split(',')])
    st.download_button(label="Download data as CSV", data=kw_df.to_csv().encode('utf-8'),
         file_name=f'keywords-{fn}.csv', mime='text/csv')
# st.plotly_chart(plot_term_by_source(df_filtered, searchterm_single, kwsearch_abs_btn), use_container_width=True)

placeholder.empty()
