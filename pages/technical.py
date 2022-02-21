import streamlit as st
#import streamlit.components.v1 as components
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
from hydralit import HydraHeadApp

class technical(HydraHeadApp):
#def app():

    def run(self):

        def articles_by_pub(date_df):

            # build plot with a secondary y axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])

            for source in date_df.source.unique():
                d_df = date_df[date_df.source==source].resample('M')
                fig.add_trace(go.Bar(x=[datetime.strftime(n,'%b %Y') for n,g in d_df], y=d_df.count()['title'],
                                    name='{} - {:,} articles'.format(source, d_df.count()['title'].sum()),
                                    marker_color=(colors[list(date_df.source.unique()).index(source)])
                    ))

            # Update layout
            fig.update_layout(barmode='stack', xaxis_tickangle=45,
                              title='Number of monthly articles published relating to COVID-19 - {:,} total'.format(len(date_df)))
            fig.update_yaxes(title_text="Articles", secondary_y=False, showgrid=False)

            # include cases as line graph
            if 'userdata' not in st.session_state:
                cv_data = getdata.get_case_data(st.session_state.case_csv)

                # cases
                fig.add_trace(go.Scatter(x=[datetime.strftime(n,'%b %Y') for n,g in cv_data], y=[g.newcases.mean() for n,g in cv_data],
                                name='New daily COVID-19 cases reported', mode='lines',marker_color='indianred', line_shape='spline',line_smoothing=.2),
                                secondary_y=True
                        )
                fig.update_yaxes(title_text="New daily COVID cases", secondary_y=True, showgrid=False)

            return fig

        @st.experimental_memo
        def get_tech_details(df):
            tech_df = pd.DataFrame()

            for n,g in df.groupby('source'):

                info = {}
                rd = g['readability']
                gl = g['grade_level']

                info['Publication'] = n
                info['Readability score'] = f'{round(rd.mean(),2)} ({round(max(rd),2)} high, {round(min(rd),2)} low)'
                info['Grade level'] = f'{round(gl.mean(),2)} ({round(max(gl),2)} high, {round(min(gl),2)} low)'
                info['Number of articles'] = str(len(g))
                info['Average article length'] = f"{int(len(' '.join(g['full_text']).split()) / len(g))} words"
                # info['Earliest article'] = datetime.strftime(datetime.strptime(g.date.min(),"%Y-%m-%d"),'%B %-d, %Y')
                info['Earliest article'] = g.date.min()
                info['Most recent article'] = g.date.max()
                tech_df = tech_df.append(info, ignore_index=True)

            tech_df['Number of articles'] = tech_df['Number of articles'].astype(int)
            tech_df.sort_values(by=['Number of articles'], ascending=False, inplace=True)
            tech_df.set_index('Publication', inplace=True)
            tech_df = tech_df.reindex(columns=['Number of articles','Earliest article','Most recent article','Average article length','Readability score','Grade level'])
            return tech_df

        df_filtered = st.session_state.df_filtered
        date_df = st.session_state.date_df

        # placeholder for status updates
        placeholder = st.empty()

        # get source data
        placeholder.markdown('*. . . Initializing . . .*\n\n')

        # header
        st.subheader('Technical details')

        # articles by publication
        placeholder.markdown('*. . . Analyzing publication data . . .*\n\n')

        st.plotly_chart(articles_by_pub(date_df), use_container_width=True)
        st.table(get_tech_details(df_filtered))

        placeholder.empty()
