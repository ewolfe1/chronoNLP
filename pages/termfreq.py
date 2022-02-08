import streamlit as st
import pandas as pd
import numpy as np
from natsort import natsorted
from hydralit import HydraHeadApp
import hydralit_components as hc
from scripts import tfproc
import textblob
import subprocess
import sys

class termfreq(HydraHeadApp):

    def run(self):

        @st.cache
        def tb_corpora():
            cmd = [f"{sys.executable}","-m","textblob.download_corpora"]
            subprocess.run(cmd)

        tb_corpora()

        # get source data
        df_filtered = st.session_state.df_filtered

        # placeholder for status updates
        placeholder = st.empty()

        def tf_form(tf):

            n = int(tf['name'][-1])
            # form to allow user input
            with st.form(key=f'tf{n}_form'):

                tf['kwd'] = st.selectbox('Terms used vs. AI generated keywords vs. TF-IDF',['Terms','Keywords','TF-IDF'], key=f'tf{n}kwd', index=0)
                #tf['month'] = st.selectbox('Month',['All months in range'] + natsorted(list(df_filtered.month.unique())),key=f'tfmo{n}', index=1)
                #tf['source'] = st.selectbox('Source',['All sources in range'] + list(df_filtered.source.unique()),key=f'tfs{n}', index=1)
                months = [d for d in natsorted(df_filtered['month'].unique().tolist()) if d not in ['',None]]
                tf['month_start'],tf['month_end'] = st.select_slider('Date range',
                     options=months, value=(months[0],months[-1]), key=f'tfd{n}')
                sources = list(df_filtered.source.unique())
                tf['source'] = st.multiselect('Source',sources,key=f'tfs{n}',default=sources[0])
                tf['ngram'] = st.selectbox('Ngrams',[1,2,3],key=f'tfng{n}', index=n-1)
                tf['omit'] = st.text_input('Terms to omit from the results (separated by a comma)',key=f'tfmin{n}')

                tf_submit_button = st.form_submit_button(label='Update search')

                # if 'All' in tf['month']:
                #     tf['month'] = '.*'
                # if 'All' in tf['source']:
                #     tf['source'] = '.*'

                return tf, tf_submit_button



        # header
        st.subheader('Term frequency')
        placeholder.markdown('*. . . Initializing . . .*\n\n')
        placeholder.markdown('*. . . Analyzing term frequency . . .*\n\n')

        # body
        tf_col1, tf_col2 = st.columns(2)

        # set session state to remember filled forms on reload
        # initial values for first load
        if 'tf_run' not in st.session_state:
            st.session_state.tf_forms = [
            {   'name':'tf1',
                'kwd':'Terms',
                'month':natsorted(df_filtered.month.unique())[0],
                'source':df_filtered.source.unique()[0],
                'ngram':1,
                'omit':''
            },
            {   'name':'tf2',
                'kwd':'Terms',
                'month':natsorted(df_filtered.month.unique())[0],
                'source':df_filtered.source.unique()[0],
                'ngram':2,
                'omit':''
            }]

        with tf_col1:

            tf1 = st.session_state.tf_forms[0]

            # form to allow user input
            tf1, tf1_submit_button = tf_form(tf1)

            # when button clicked, update data
            if tf1_submit_button:
                st.session_state.tf_run = True

            try:
                if tf1['kwd'] == 'Terms':
                    t1_df, tf1 = tfproc.get_tf(df_filtered, tf1)
                elif tf1['kwd'] == 'TF-IDF':
                    t1_df, tf1 = tfproc.get_tfidf(df_filtered, tf1)
                elif tf1['kwd'] == 'Keywords':
                    t1_df, tf1 = tfproc.get_rake(df_filtered, tf1)

                st.markdown(tfproc.results_title(tf1))
                st.table(t1_df)

                # wordcloud
                wc1 = tfproc.get_wc(tf1)
                st.pyplot(wc1)

            except ValueError:
                st.write('There are no results from this search')

            # set values to session state
            st.session_state.tf_forms[0] = tf1

        with tf_col2:

            tf2 = st.session_state.tf_forms[1]

            # form to allow user input
            tf2, tf2_submit_button = tf_form(tf2)

            # when button clicked, update data
            if tf2_submit_button:
                st.session_state.tf_run = True

            try:
                if tf2['kwd'] == 'Terms':
                    t2_df, tf2 = tfproc.get_tf(df_filtered, tf2)
                elif tf2['kwd'] == 'TF-IDF':
                    t2_df, tf2 = tfproc.get_tfidf(df_filtered, tf2)
                elif tf2['kwd'] == 'Keywords':
                    t2_df, tf2 = tfproc.get_rake(df_filtered, tf2)


                st.markdown(tfproc.results_title(tf2))
                st.table(t2_df)

                # wordcloud
                wc2 = tfproc.get_wc(tf2)
                st.pyplot(wc2)

            except ValueError:
                st.write('There are no results from this search')

            # set values to session state
            st.session_state.tf_forms[1] = tf2

        placeholder.empty()
