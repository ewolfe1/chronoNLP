import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from datetime import datetime
from natsort import natsorted
# import colorlover as cl
# colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
from ast import literal_eval
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder

from scripts import tools, getdata

def sort_legend(legend_ct, fig):

    new_order = [f'{k} ({v:,} total uses)' for k,v in natsorted(legend_ct.items(), key=lambda x:x[1])]
    ordered_legend = []
    for i in new_order:
        item = [t for t in fig.data if t['name'] == i]
        ordered_legend += item
    return ordered_legend

def items_by_source(dist_val):

    # build plot
    fig = go.Figure()

    df = state.df_filtered
    df['count'] = df.full_text.apply(lambda x: len(x.split()))
    df.sort_values('date', ascending=True, inplace=True)
    legend_ct = {}

    # sorting this way to ensure label is sequential
    for source in df.source.value_counts(ascending=True).keys():

        d_df = df[df.source==source].groupby('date')

        if 'items' in dist_val:
            ydata = d_df.count()['full_text']
            label = d_df.count()['full_text'].sum()
            var = 'items'
        else:
            ydata = d_df['count'].sum()
            label = d_df['count'].sum().sum()
            var = 'words'

        fig.add_trace(go.Bar(x=natsorted([getdata.get_cleandate(n) for n,g in d_df]), y=ydata,
                            name='{} - {:,} {}'.format(source, label, var),
                            marker_color=(state.colors[list(df.source.unique()).index(source)])
            ))

        legend_ct[source] = label

    # Update layout
    fig.update_layout(barmode='stack', xaxis_tickangle=45,
                      title=f'Distribution of {var} over time',
                      )
    fig.update_traces(marker_line_width=0)
    fig.update_yaxes(title_text=var.title())
    fig.update_xaxes(title_text="Time")

    # fig.data = sort_legend(legend_ct, fig)
    fig.update_layout(showlegend=True, legend={'traceorder':'reversed'})

    return fig

def update_overview_df(n, g, tech_df):

    info = {}
    rd = g['readability']
    gl = g['grade_level']

    info['Source'] = n
    info['Readability score'] = f'{round(rd.mean(),2)} ({round(max(rd),2)} high, {round(min(rd),2)} low)'
    # info['Grade level'] = f'{round(gl.mean(),2)} ({round(max(gl),2)} high, {round(min(gl),2)} low)'
    info['Number of items'] = len(g)
    info['Average length'] = f"{int(len(' '.join(g['full_text']).split()) / len(g)):,} words"
    info['Longest'] = f"{g.nlargest(1, ['count'])['count'].values[0]:,} words"
    info['Shortest'] = f"{g.nsmallest(1, ['count'])['count'].values[0]:,} words"
    info['Earliest'] = getdata.format_dates(g.cleandate.min())
    info['Most recent'] = getdata.format_dates(g.cleandate.max())
    tech_df = pd.concat([tech_df, pd.DataFrame([info])])

    return tech_df

# @st.cache_data
def get_tech_details():

    df = state.df_filtered
    tech_df = pd.DataFrame()
    df['count'] = df.full_text.apply(lambda x: len(x.split()))

    tech_df = update_overview_df('(All sources)', df, tech_df)

    for n,g in df.groupby('source'):

        tech_df = update_overview_df(n, g, tech_df)

    tech_df['Number of items'] = tech_df['Number of items'].astype(int)
    tech_df.sort_values(by=['Number of items'], ascending=False, inplace=True)
    tech_df['Number of items'] = tech_df['Number of items'].apply(lambda x: f"{x:,}")
    tech_df.set_index('Source', inplace=True)
    tech_df = tech_df.reindex(columns=['Number of items','Earliest','Most recent',
                        'Average length','Longest','Shortest','Readability score',
                        # 'Grade level'
                        ])
    #return tech_df.style.format({'Number of items':'{:,}'})
    return tech_df


def text_features(num_tc):

    df = state.df_filtered
    # break pos into separate df for eval
    df_pos = df[['date','cleandate','pos_all']].copy()
    try:
        df_pos['pos_all'] = df_pos['pos_all'].apply(literal_eval)
    except:
        pass
    df_pos = df_pos.set_index(['date','cleandate']).apply(lambda x: x.explode()).reset_index()
    df_pos['token'] = df_pos['pos_all'].apply(lambda x: None if isinstance(x, float) else x[0].lower())
    df_pos['pos'] = df_pos['pos_all'].apply(lambda x: None if isinstance(x, float) else x[1])
    def sw(t):
        if t in STOP_WORDS:
            return True
        else:
            return False
    df_pos['stopword'] = df_pos['token'].apply(lambda x: sw(x))
    df_pos = df_pos[~df_pos.token.isnull()]
    df_pos.drop('pos_all', axis=1, inplace=True)

    # count pos
    # c.f. https://newscatcherapi.com/blog/named-entity-recognition-with-spacy
    pos_dict = {
            'Nouns': df_pos[(df_pos['pos'].isin(['NOUN']))],
            'Proper nouns': df_pos[(df_pos['pos'].isin(['PROPN']))],
            'Pronouns': df_pos[(df_pos['pos'].isin(['PRON']))],
            'Verbs': df_pos[(df_pos['pos'].isin(['VERB']))],
            'Adjectives': df_pos[(df_pos['pos'].isin(['ADJ']))],
            'Adverbs': df_pos[(df_pos['pos'].isin(['ADV']))]
            }

    total_words = len(df_pos)
    # total_wo_common = len(df_pos[df_pos['stopword']==True])

    pos_df = pd.DataFrame()

    pos_container = '<div class="outer">'

    for name,data in pos_dict.items():

        count = data['pos'].count()
        top = data['token'].value_counts()[:num_tc]
        pos_df = pd.concat([pos_df, pd.DataFrame([{'Part of speech':name,
                                                   'Count':f"{count:,} ({count/total_words*100:.1f}%)",
                                                  'Most frequent':', '.join([f"{t[0]} ({t[1]:,})" for t in zip(top.keys(), top.values)])
                                                  }])])

        pos_container += '<div class="inner">'
        pos_container += f'<p class="colhead">{name}</p>'
        pos_container += f"<p>{count:,} ({count/total_words*100:.1f}%)</p>"

        pos_container += "<ul>"
        for t in zip(top.keys(), top.values):
            pos_container += f"<li>{t[0]} ({t[1]:,})</li>"
        pos_container += "</ul></div>"
    pos_container += "</div>"

    st.markdown(pos_container, unsafe_allow_html=True)
    # pos_df.set_index(['Part of speech'],inplace=True, drop=True)

    return total_words, df_pos

# @st.cache_data
def get_entities(num_ent):

    df = state.df_filtered
    # break pos into separate df for eval
    df_ent = df[['date','cleandate','entities_all']].copy()
    try:
        df_ent['entities_all'] = df_ent['entities_all'].apply(literal_eval)
    except:
        pass
    df_ent = df_ent.set_index(['date','cleandate']).apply(lambda x: x.explode()).reset_index()
    df_ent['token'] = df_ent['entities_all'].apply(lambda x: None if isinstance(x, float) else x[0].lower())
    df_ent['entity'] = df_ent['entities_all'].apply(lambda x: None if isinstance(x, float) else x[1])
    df_ent = df_ent[~df_ent.token.isnull()]
    df_ent.drop('entities_all', axis=1, inplace=True)

    ent_dict = {}
    for n,g in df_ent.groupby('entity'):
        ent_dict[n] = g.copy()

    ent_df = pd.DataFrame()
    total_words = len(df_ent)

    ent_container = '<div class="outer">'

    for name,data in ent_dict.items():

        count = data['entity'].count()
        top = data['token'].value_counts()[:num_ent]

        ent_df = pd.concat([ent_df, pd.DataFrame([{'Named entity':name,
                                                   'Count':count,
                                                  'Most frequent':', '.join([f"{t[0]} ({t[1]:,})" for t in zip(top.keys(), top.values)])
                                                  }])])
        ent_container += '<div class="inner">'
        ent_container += f'<p class="colhead">{name}</p>'
        ent_container += f"<p>{count:,} ({count/total_words*100:.1f}%)</p>"

        ent_container += "<ul>"
        for t in zip(top.keys(), top.values):
            ent_container += f"<li>{t[0]} ({t[1]:,})</li>"
        ent_container += "</ul></div>"
    ent_container += "</div>"

    st.markdown(ent_container, unsafe_allow_html=True)


def ner_df():

    df = state.df_filtered
    return df[df.full_text,str.contains(state.ner_txt, na=False, case=False)]
