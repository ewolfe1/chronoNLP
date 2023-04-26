import streamlit as st
state = st.session_state
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, ColumnsAutoSizeMode
import numpy as np
import re
import random
from datetime import datetime
import string
from natsort import natsorted
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import spacy
import nltk
from nltk.corpus import stopwords
stopwords = stopwords.words('english')
from nltk import FreqDist
from nltk.corpus import stopwords
from textblob import TextBlob, Word
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

def strip_punct(k):
    return re.sub(r'[^\w\s]', '', k)

def get_ct(df, k, omit):
    return kwd_count(strip_punct(k), ' '.join(df.full_text), omit)

@st.cache_data
def get_pattern(term, fulltext, omit):

    # formatting
    omit_set = set(omit.lower().strip() for omit in omit.split(','))
    tokens = [token.strip() for token in fulltext.split() if token.lower().strip() not in omit_set]

    term = term.strip().lower()

    rep = ['*','^','.',',','”','"']
    t = term.strip().lower().translate(str.maketrans('', '', ''.join(rep)))

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

@st.cache_data
def kwd_count(term, fulltext, omit):

    # formatting
    omit_set = set(omit.lower().strip() for omit in omit.split(','))
    tokens = [token.strip() for token in fulltext.split() if token.lower().strip() not in omit_set]

    t = term.strip().lower()
    t = re.sub(r'[^\w\s]', '', t)

    if term.startswith('*') and term.endswith('*'):
        matches = re.findall(t, rf'{fulltext}')
    elif term.endswith('*'):
        matches = re.findall(fr'\b{t}', rf'{fulltext}')
    elif term.startswith('*'):
        matches = re.findall(fr'{t}\b', rf'{fulltext}')
    # exact count (single word or phrase)
    else:
        matches = re.findall(fr'\b{t}\b', rf'{fulltext}')

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

    source_df = pd.DataFrame()

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

        source_df = pd.concat([source_df, pd.DataFrame([kwsearch], columns=[n for n,g in d_df], index=[f'{source} (R)'])])
        source_df = pd.concat([source_df, pd.DataFrame([kwsearch_norm], columns=[n for n,g in d_df], index=[f'{source} (N)'])])

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

    return fig_abs, fig_norm, source_df.T

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
        kw_df[f'{term} (R)'] = kwsearch_abs
        kw_df[f'{term} (N)'] = kwsearch_norm
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
        # st.table(kw_src_df)
        gb = GridOptionsBuilder.from_dataframe(kw_src_df)
        gridOptions = gb.build()
        column_defs = gridOptions["columnDefs"]
        for col_def in column_defs:
            col_name = col_def["field"]
            max_len = kw_src_df[col_name].astype(str).str.len().max() + 5
            col_def["width"] = max_len
        grid_response = AgGrid(
            kw_src_df,
            columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS,
            gridOptions=gridOptions,
            # alwaysShowHorizontalScroll = True,
            #fit_columns_on_grid_load=True,
            width='100%'
        )

        # fn = '_'.join([t.lower().strip() for t in terms])
        # st.download_button(label="Download data as CSV", data=kw_src_df.to_csv().encode('utf-8'),
        #      file_name=f'keywords-{fn}.csv', mime='text/csv', key=f'kw_dl{terms.index(term)}')


def get_re_pattern(term):

    if term.startswith('*') and term.endswith('*'):
        pattern = term.replace('*','')
    elif term.endswith('*'):
        pattern = fr"\b{term.replace('*','')}"

    elif term.startswith('*'):
        pattern = fr"{term.replace('*','')}\b"
    else:
        pattern = fr'\b{term}\b'

    return pattern


def kwic(df, term):

    if type(term) == list:
        pattern = '|'.join([get_re_pattern(t) for t in term])
        term = '|'.join(term)
    else:
        pattern = get_re_pattern(term)

    t_df = df[df.full_text.str.contains(term, case=False, na=False)]
    kwic_df = pd.DataFrame()

    for i,r in t_df.iterrows():

        words = r.full_text.split()
        n = 7

        # Loop through each word and find matches
        for iw, word in enumerate(words):
            if re.search(pattern, word, re.IGNORECASE):

                prev = words[max(0, iw-(n+1)):iw]
                t = words[iw]
                next = words[iw+1:iw+(n+2)]

                if len(prev) > n:
                    prev = ['...'] + prev[1:]
                # else:
                #     prev = prev[:n]
                if len(next) > n:
                    next = next[:-1] + ['...']
                # else:
                #     next = next[:n]

                kwic_df = pd.concat([kwic_df, pd.DataFrame([{'cleandate':r.cleandate,
                            'left':" ".join(prev),
                            'keyword':t,
                            'right':" ".join(next),
                            'uniqueID':r.uniqueID}])])

    kwic_df.sort_values('cleandate', ascending=True, inplace=True)
    kwic_df.reset_index(inplace=True, drop=True)

    kwic_df.set_index('cleandate', inplace=True)
    return kwic_df

# look at nearby words
def cooccurence(df):

    left = ' '.join(df[~df.left.isnull()].left.str.lower().tolist())
    right = ' '.join(df[~df.right.isnull()].right.str.lower().tolist())
    all = ' '.join([left, right])

    def get_freq(l):

        tb_to_eval = TextBlob(l)
        grouped_text = FreqDist([' '.join(ng) for ng in tb_to_eval.ngrams(1)]).most_common(200)
        grouped_text = [g for g in grouped_text if g[0].lower() not in stopwords and g[0].lower().isalpha()]
        # grouped_text_dict = {t:f for t,f in grouped_text}
        common_df = pd.DataFrame(grouped_text[:10], columns=['term','frequency'])
        common_df.set_index('term', inplace=True)

        return common_df

    left_df = get_freq(left)
    right_df = get_freq(right)
    all_df = get_freq(all)

    return left_df, right_df, all_df
