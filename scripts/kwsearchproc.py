import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
import re
from datetime import datetime
from natsort import natsorted
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy
from nltk import FreqDist
from sklearn.preprocessing import minmax_scale
from scripts import getdata

def searchtips():
    st.write("""The keyword search feature allows searches with the following patterns:

* test - will return all exact matches for 'test'
* test site - all exact matches for 'test site'
* test\* - a single count for all matches beginning with 'test' (e.g., 'test', 'testing')
* ^test\* - individual counts for each match beginning with 'test'
* \*test - a single count for all matches ending with 'test' (e.g., 'detest', 'test')
* ^\*test - individual counts for each match ending with 'test'
* \*test\* - a single count for all matches containing the characters 'test' (e.g., 'test', 'detesting')
* ^\*test\* - individual counts for each match containing the characters 'test'

*You may find that wildcard search return unwanted results. If so, enter these terms into the 'Words to omit' box and try the search again.*""")

def get_pattern(term, fulltext, omit):

    # formatting
    for o in omit.split(','):
        fulltext = fulltext.replace(o.lower().strip(),'')
    tokens = [ft.strip() for ft in fulltext.split()]
    term = term.strip().lower()
    t = term
    rep = ['*','^','.',',','”','"']
    for r in rep:
        t = t.replace(r,'')

    if term.startswith('^'):
        return_all = True
        term = term.replace('^','')
    else:
        return_all = False

    # partial matches
    if term.startswith('*') and term.endswith('*'):
        matches = re.findall(t, fulltext)
        # return multiple matches
        if return_all:
            matchdict = {tm:tokens.count(tm) for tm in set([w for w in tokens if t in w])}
            return matchdict
    elif term.endswith('*'):
        matches = re.findall(fr'\b{t}', fulltext)
        # return multiple matches
        if return_all:
            matchdict = {tm:tokens.count(tm) for tm in set([w for w in tokens if w.startswith(t)])}
            return matchdict
    elif term.startswith('*'):
        matches = re.findall(fr'{t}\b', fulltext)
        # return multiple matches
        if return_all:
            matchdict = {tm:tokens.count(tm) for tm in set([w for w in tokens if w.endswith(t)])}
            return matchdict
    # exact count (single word or phrase)
    else:
        matches = re.findall(fr'\b{t}\b', fulltext)

    matchdict = {t:len(matches)}
    return matchdict

def kwd_count(term, fulltext, omit):

    # formatting
    for o in omit.split(','):
        fulltext = fulltext.replace(o.lower().strip(),'')
    tokens = [ft.strip() for ft in fulltext.split()]
    term = term.strip().lower()
    t = term
    rep = ['*','^','.',',','”','"']
    for r in rep:
        t = t.replace(r,'')

    # partial matches
    if term.startswith('*') and term.endswith('*'):
        matches = re.findall(t, fulltext)
    elif term.endswith('*'):
        matches = re.findall(fr'\b{t}', fulltext)
    elif term.startswith('*'):
        matches = re.findall(fr'{t}\b', fulltext)
    # exact count (single word or phrase)
    else:
        matches = re.findall(fr'\b{t}\b', fulltext)

    return len(matches)

def sort_legend(legend_ct, fig):

    new_order = [f'{k} ({v:,} total uses)' for k,v in natsorted(legend_ct.items(), key=lambda x:x[1])]
    ordered_legend = []
    for i in new_order:
        item = [t for t in fig.data if t['name'] == i]
        ordered_legend += item
    return ordered_legend

# plot a single term across multiple sources
@st.cache_resource
def plot_term_by_source(df, term, omit):

    fig_abs = go.Figure()
    fig_norm = go.Figure()
    df = df[~(df.clean_text.isnull())]
    legend_ct = {}

    for source in df.source.unique():

        d_df = df[df.source==source].groupby('cleandate')
        num_articles = len(df[df.source==source])

        if type(term) == list:
            # kwsearch = [sum(kwd_count(t, ' '.join(g.clean_text), omit) for t in term) for n,g in d_df]
            kwsearch = [sum(kwd_count(t, ' '.join(g.full_text.str.lower()), omit) for t in term) for n,g in d_df]
            kwsearch_norm = ([t/num_articles for t in kwsearch])
            total_uses = sum(kwsearch)
        else:
            # kwsearch = [kwd_count(term, ' '.join(g.clean_text), omit) for n,g in d_df]
            kwsearch = [kwd_count(term, ' '.join(g.full_text.str.lower()), omit) for n,g in d_df]
            kwsearch_norm = ([t/num_articles for t in kwsearch])
            total_uses = sum(kwsearch)

        if all(i==0 for i in kwsearch):
            continue

        fig_abs.add_trace(go.Scatter(x=[n for n,g in d_df], y=kwsearch,
                        name=f'{source} ({total_uses:,} total uses)', line_shape='spline', mode='lines+markers', connectgaps=True,
                        marker_color=(state.colors[list(df.source.unique()).index(source)])
                        ))

        fig_norm.add_trace(go.Scatter(x=[n for n,g in d_df], y=kwsearch_norm,
                        name=f'{source} ({total_uses:,} total uses)', line_shape='spline', mode='lines+markers', connectgaps=True,
                        marker_color=(state.colors[list(df.source.unique()).index(source)])
                        ))
        legend_ct[source] = total_uses

    fig_abs.data = sort_legend(legend_ct, fig_abs)
    fig_abs.update_layout(showlegend=True, legend={'traceorder':'reversed'})

    fig_norm.data = sort_legend(legend_ct, fig_norm)
    fig_norm.update_layout(showlegend=True, legend={'traceorder':'reversed'})

    return fig_abs, fig_norm, None

# plot multiple terms over time
@st.cache_resource
def plot_terms_by_month(df, stlist, omit):

    fig_abs = go.Figure()
    fig_norm = go.Figure()

    d_df = df[~(df.full_text.isnull())].groupby('cleandate')
    timeframe = [getdata.get_cleandate(g.iloc[0].date) for n,g in d_df]
    kw_df = pd.DataFrame({'date':timeframe})
    legend_ct = {}
    ct = 0

    for term in stlist:

        total_uses = kwd_count(term, ' '.join(df.full_text), omit)
        if total_uses == 0:
            continue

        kwsearch_abs = [kwd_count(term, ' '.join(g.full_text.str.lower()), omit) for n,g in d_df]
        kwsearch_norm = [kwd_count(term, ' '.join(g.full_text.str.lower()), omit)/len(g) for n,g in d_df]
        # normalize to data
        kwsearch_norm = minmax_scale(kwsearch_norm)

        # add to graph
        fig_abs.add_trace(go.Scatter(x=timeframe, y=kwsearch_abs,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch_abs,
                        mode='lines+markers', connectgaps= True,
                        line_shape='spline')) # , marker_color=(state.colors[ct])
        fig_norm.add_trace(go.Scatter(x=timeframe, y=kwsearch_norm,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch_norm,
                        mode='lines+markers', connectgaps= True,
                        line_shape='spline')) # , marker_color=(state.colors[ct])
        # add to df
        kw_df[f'{term} - Raw count'] = kwsearch_abs
        kw_df[f'{term} - Normalized'] = kwsearch_norm
        legend_ct[term] = total_uses

        ct += 1

    fig_abs.data = sort_legend(legend_ct, fig_abs)
    fig_abs.update_layout(showlegend=True, legend={'traceorder':'reversed'})

    fig_norm.data = sort_legend(legend_ct, fig_norm)
    fig_norm.update_layout(showlegend=True, legend={'traceorder':'reversed'})

    return fig_abs, fig_norm, kw_df

def get_tabs(df, term, omit):

    try:
        if kwd_count(term, ' '.join(df.full_text), omit) == 0:
            return
    except AttributeError:
        pass

    if type(term) == list:
        st.write(f"#### Keywords - all")
        st.write(f'{" + ".join(term)}')
    else:
        st.write(f"#### Keyword - {term}")

    kw_src_abs_t, kw_src_norm_t, kw_src_df = plot_term_by_source(df, term, omit)
    t1, t2, t3 = st.tabs(["Raw count (graph)", "Normalized (graph)", "Table"])

    with t1:
        st.write('Raw count of keyword frequency over time')
        st.plotly_chart(kw_src_abs_t, use_container_width=True)

    with t2:
        st.write('Keyword frequency over time, normalized relative to the publication frequency (scale of 0 to 1).')
        st.plotly_chart(kw_src_norm_t, use_container_width=True)

    with t3:
        st.write('Raw and normalized (scale of 0 to 1) frequency counts for each term.')
        st.table(kw_src_df)

        # fn = '_'.join([t.lower().strip() for t in terms])
        # st.download_button(label="Download data as CSV", data=kw_src_df.to_csv().encode('utf-8'),
        #      file_name=f'keywords-{fn}.csv', mime='text/csv', key=f'kw_dl{terms.index(term)}')
