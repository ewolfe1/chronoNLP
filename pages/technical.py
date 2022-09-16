import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from datetime import datetime
from natsort import natsorted
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from scripts import getdata
getdata.page_config()

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

        info['Publication'] = n
        info['Readability score'] = f'{round(rd.mean(),2)} ({round(max(rd),2)} high, {round(min(rd),2)} low)'
        info['Grade level'] = f'{round(gl.mean(),2)} ({round(max(gl),2)} high, {round(min(gl),2)} low)'
        info['Number of items'] = str(len(g))
        info['Average length'] = f"{int(len(' '.join(g['full_text']).split()) / len(g))} words"
        # info['Earliest article'] = datetime.strftime(datetime.strptime(g.date.min(),"%Y-%m-%d"),'%B %-d, %Y')
        info['Earliest'] = datetime.strftime(g.date.min(),'%Y-%m-%d')
        info['Most recent'] = datetime.strftime(g.date.max(),'%Y-%m-%d')
        # tech_df = tech_df.append(info, ignore_index=True)
        tech_df = pd.concat([tech_df, pd.DataFrame([info])])

    tech_df['Number of items'] = tech_df['Number of items'].astype(int)
    tech_df.sort_values(by=['Number of items'], ascending=False, inplace=True)
    tech_df.set_index('Publication', inplace=True)
    tech_df = tech_df.reindex(columns=['Number of items','Earliest','Most recent','Average length','Readability score','Grade level'])
    return tech_df

# load data
if 'init' not in state:
    getdata.init_data()
df_filtered = state.df_filtered

# placeholder for status updates
placeholder = st.empty()

# get source data
placeholder.markdown('*. . . Initializing . . .*\n\n')

# header
st.subheader('Technical details')
getdata.df_summary_header()

# articles by publication
placeholder.markdown('*. . . Analyzing publication data . . .*\n\n')

st.plotly_chart(items_by_source(), use_container_width=True)
st.table(get_tech_details())

placeholder.empty()
