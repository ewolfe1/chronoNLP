import streamlit as st
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

def articles_by_pub():

    date_df = st.session_state.df_filtered
    date_df = date_df.set_index('date')

    # build plot with a secondary y axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    for source in date_df.source.unique():
        d_df = date_df[date_df.source==source].resample('M')
        fig.add_trace(go.Bar(x=[datetime.strftime(n,'%b %Y') for n,g in d_df], y=d_df.count()['title'],
                            name='{} - {:,} items'.format(source, d_df.count()['title'].sum()),
                            marker_color=(colors[list(date_df.source.unique()).index(source)])
            ))

    # Update layout
    fig.update_layout(barmode='stack', xaxis_tickangle=45,
                      title='Distribution of items over time'
                      )
    fig.update_yaxes(title_text="Items", secondary_y=False, showgrid=False)

    return fig

def get_tech_details():

    df = st.session_state.df_filtered
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
if 'init' not in st.session_state:
    getdata.init_data()
df_filtered = st.session_state.df_filtered

# placeholder for status updates
placeholder = st.empty()

# get source data
placeholder.markdown('*. . . Initializing . . .*\n\n')

# header
st.subheader('Technical details')
getdata.df_summary_header()

# articles by publication
placeholder.markdown('*. . . Analyzing publication data . . .*\n\n')

st.plotly_chart(articles_by_pub(), use_container_width=True)
st.table(get_tech_details())

placeholder.empty()
