import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from datetime import datetime
from natsort import natsorted
# import colorlover as cl
# colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
# import plotly.express as px
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# spacy
import spacy
from nltk import FreqDist
from sklearn.preprocessing import minmax_scale
from scripts import tools, saproc, getdata
tools.page_config()


@st.experimental_memo
def load_model():
    return spacy.load("en_core_web_sm")

nlp = load_model()

# plot a single term across multiple sources
@st.experimental_memo
def plot_term_by_source(df, searchterm, kwmethod_btn):

    if 'Partial' in kwmethod_btn:
        try:
            searchterm = [w.lemma_ for w in nlp(searchterm.lower().strip())][0]
        except IndexError:
            term = searchterm.lower().strip()

    fig_abs = go.Figure()
    fig_norm = go.Figure()

    for source in df.source.unique():

        d_df = df[df.source==source].groupby('cleandate')
        num_articles = len(df[df.source==source])

        kwsearch = [sum(' '.join(g.lemmas).split().count(term.strip()) for term in searchterm.split(',')) for n,g in d_df]
        kwsearch_norm = ([t/num_articles for t in kwsearch])
        kwcount = "{:,d}".format(sum(kwsearch))

        fig_abs.add_trace(go.Scatter(x=[n for n,g in d_df], y=kwsearch,
                        name=f'{source} ({kwcount} total uses)', line_shape='spline', mode='lines',
                        marker_color=(state.colors[list(df.source.unique()).index(source)])
                        ))

        fig_norm.add_trace(go.Scatter(x=[n for n,g in d_df], y=kwsearch_norm,
                        name=f'{source} ({kwcount} total uses)', line_shape='spline', mode='lines',
                        marker_color=(state.colors[list(df.source.unique()).index(source)])
                        ))

    return fig_abs, fig_norm, None

# plot multiple terms over time
@st.experimental_memo
def plot_terms_by_month(df, searchterm, kwmethod_btn):

    fig_abs = go.Figure()
    fig_norm = go.Figure()

    d_df = df[~(df.clean_text.isnull()) & ~(df.lemmas.isnull())].groupby('cleandate')
    timeframe = [getdata.get_cleandate(g.iloc[0].date) for n,g in d_df]
    kw_df = pd.DataFrame({'date':timeframe})
    ct = 0

    for term in searchterm.split(','):

        if 'Partial' in kwmethod_btn:
            try:
                term = [w.lemma_ for w in nlp(term.lower().strip())][0]
            except IndexError:
                term = term.lower().strip()

            total_uses_lemm = ' '.join(df.lemmas).count(term)
            total_uses_all = ' '.join(df.clean_text).count(term)

            if total_uses_lemm > total_uses_all:
                total_uses = total_uses_lemm
                kwsearch_abs = [' '.join(g.lemmas).count(term) for n,g in d_df]
                kwsearch_norm = [' '.join(g.lemmas).count(term)/len(g) for n,g in d_df]
            else:
                total_uses = total_uses_all
                kwsearch_abs = [' '.join(g.clean_text).count(term) for n,g in d_df]
                kwsearch_norm = [' '.join(g.clean_text).count(term)/len(g) for n,g in d_df]

        else:
        # print(term)
            total_uses = ' '.join(df.clean_text).count(term)

            kwsearch_abs = [' '.join(g.clean_text).count(term) for n,g in d_df]
            kwsearch_norm = [' '.join(g.clean_text).count(term)/len(g) for n,g in d_df]
            # normalize to data
        kwsearch_norm = minmax_scale(kwsearch_norm)

        # add to graph
        fig_abs.add_trace(go.Scatter(x=timeframe, y=kwsearch_abs,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch_abs,
                        line_shape='spline',
                        marker_color=(state.colors[ct])))
        fig_norm.add_trace(go.Scatter(x=timeframe, y=kwsearch_norm,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch_norm,
                        line_shape='spline',
                        marker_color=(state.colors[ct])))
        # add to df
        kw_df[f'{term} - Raw count'] = kwsearch_abs
        kw_df[f'{term} - Normalized'] = kwsearch_norm

        ct += 1
    fig_abs.update_layout(showlegend=True)
    fig_norm.update_layout(showlegend=True)

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
    searchterm = st.text_input("Enter keyword(s), separated by a comma (no quotes)", value='test')
    kwmethod_btn = st.radio('', ['Partial match','Exact match'], key='kwmethod', horizontal=True)
    # kwsearch_btn = st.radio('View results as a ', ['Graph','Table'], key='kwsearch', horizontal=True)

kw_abs, kw_norm, kw_df = plot_terms_by_month(df_filtered, searchterm, kwmethod_btn)
kw_src_abs, kw_src_norm, kw_src_df = plot_term_by_source(df_filtered, searchterm, kwmethod_btn)


if searchterm != '':
    kw_tab1, kw_tab2, kw_tab3 = st.tabs(["Raw count (graph)", "Normalized (graph)", "Table"])

    with kw_tab1:
        st.write('### Raw count of keyword frequency over time')
        st.write('**All sources combined**')
        st.plotly_chart(kw_abs, use_container_width=True)

        if len(df_filtered.source.unique()) > 1:

            with st.expander('View plots by individual sources'):
                st.write(f"#### Keywords - {' + '.join([t for t in searchterm.split()])}")
                st.plotly_chart(kw_src_abs, use_container_width=True)

                for term in searchterm.split(','):
                    st.write(f"#### Keywords - {term}")
                    kw_src_abs_t, kw_src_norm_t, kw_src_df = plot_term_by_source(df_filtered, term, kwmethod_btn)
                    st.plotly_chart(kw_src_abs_t, use_container_width=True)

    with kw_tab2:
        st.write('### Keyword frequency over time, normalized relative to the time frequency (scale of 0 to 1).')
        st.write('**All sources combined**')
        st.plotly_chart(kw_norm, use_container_width=True)

        if len(df_filtered.source.unique()) > 1:
            st.write('**Individual sources**')
            st.plotly_chart(kw_src_norm, use_container_width=True)

    with kw_tab3:
        st.write('Raw and normalized (scale of 0 to 1) frequency counts for each term.')
        st.table(kw_df)

        fn = '_'.join([t.lower().strip() for t in searchterm.split(',')])
        st.download_button(label="Download data as CSV", data=kw_df.to_csv().encode('utf-8'),
             file_name=f'keywords-{fn}.csv', mime='text/csv')
    # st.plotly_chart(plot_term_by_source(df_filtered, searchterm_single, kwsearch_abs_btn), use_container_width=True)

placeholder.empty()
