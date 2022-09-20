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

from scripts import getdata

def items_by_source():

    # build plot
    fig = go.Figure()

    df = state.df_filtered

    for source in df.source.unique():
        d_df = df[df.source==source].groupby('date')

        fig.add_trace(go.Bar(x=[getdata.get_cleandate(n) for n,g in d_df], y=d_df.count()['label'],
                            name='{} - {:,} items'.format(source, d_df.count()['label'].sum())
            ))

    # Update layout
    fig.update_layout(barmode='stack', xaxis_tickangle=45,
                      title='Distribution of items over time'
                      )
    fig.update_traces(marker_line_width=0)
    fig.update_yaxes(title_text="Items")
    fig.update_xaxes(title_text="Time")

    return fig

def get_tech_details():

    df = state.df_filtered
    tech_df = pd.DataFrame()

    for n,g in df.groupby('source'):

        info = {}
        rd = g['readability']
        gl = g['grade_level']

        info['Source'] = n
        info['Readability score'] = f'{round(rd.mean(),2)} ({round(max(rd),2)} high, {round(min(rd),2)} low)'
        info['Grade level'] = f'{round(gl.mean(),2)} ({round(max(gl),2)} high, {round(min(gl),2)} low)'
        info['Number of items'] = str(len(g))
        info['Average length'] = f"{int(len(' '.join(g['full_text']).split()) / len(g))} words"
        # info['Earliest'] = datetime.strftime(g.date.min(),'%Y-%m-%d')
        # info['Most recent'] = datetime.strftime(g.date.max(),'%Y-%m-%d')
        info['Earliest'] = getdata.format_dates(g.cleandate.min())
        info['Most recent'] = getdata.format_dates(g.cleandate.max())

        # tech_df = tech_df.append(info, ignore_index=True)
        tech_df = pd.concat([tech_df, pd.DataFrame([info])])

    tech_df['Number of items'] = tech_df['Number of items'].astype(int)
    tech_df.sort_values(by=['Number of items'], ascending=False, inplace=True)
    tech_df.set_index('Source', inplace=True)
    tech_df = tech_df.reindex(columns=['Number of items','Earliest','Most recent','Average length','Readability score','Grade level'])
    return tech_df

def text_features():

    df = state.df_filtered
    # break pos into separate df for eval
    df_pos = df[['date','cleandate','pos_all']].copy()
    df_pos['pos_all'] = df_pos['pos_all'].apply(literal_eval)
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
    total_wo_common = len(df_pos[df_pos['stopword']==True])

    pos_df = pd.DataFrame()

    for name,data in pos_dict.items():

        count = data['pos'].count()
        top = data['token'].value_counts()[:12]
        pos_df = pd.concat([pos_df, pd.DataFrame([{'Part of speech':name,
                                                   'Count':f"{count:,} ({count/total_words*100:.1f}%)",
                                                  'Most frequent':', '.join([f"{t[0]} ({t[1]:,})" for t in zip(top.keys(), top.values)])
                                                  }])])
    pos_df.set_index(['Part of speech'],inplace=True, drop=True)
    return total_words, total_wo_common, pos_df
