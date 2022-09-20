import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from natsort import natsorted
from scripts import tfproc
import textblob
import subprocess
import sys
from scripts import getdata
getdata.page_config()

@st.cache
def tb_corpora():
    cmd = [f"{sys.executable}","-m","textblob.download_corpora"]
    subprocess.run(cmd)

def tf_form(tf):

    n = int(tf['name'][-1])
    # form to allow user input
    with st.form(key=f'tf{n}_form'):

        tf['kwd'] = st.selectbox('Term frequency vs. TF-IDF rankings',['Terms','TF-IDF'], key=f'tf{n}kwd', index=0)
        # Note: have omitted 'Keywords' from the above list due to excessive processing times

        daterange = state.daterange

        tf['date_start'] = st.selectbox('Start date', daterange, index=0)
        tf['date_end'] = st.selectbox('End date', daterange, index=len(daterange)-1)

        sources = list(df.source.unique())
        tf['source'] =  st.multiselect('Source(s) (leave blank to select all)',
            sources,key=f'tfs{n}',default=sources[0])

        # tf['source'] = st.multiselect('Source(s)',sources,key=f'tfs{n}',default=sources[1])
        tf['ngram'] = st.selectbox('Ngrams',[1,2,3],key=f'tfng{n}', index=n-1)
        tf['omit'] = st.text_input('Terms to omit from the results (separated by a comma)',key=f'tfmin{n}')

        tf_submit_button = st.form_submit_button(label='Update search')

        return tf, tf_submit_button

# load data
if 'init' not in state:
    getdata.init_data()
df = state.df_filtered

# placeholder for status updates
placeholder = st.empty()

st.subheader('Term frequency')
getdata.df_summary_header()

# load corpus
tb_corpora()

placeholder.markdown('*. . . Initializing . . .*\n\n')
placeholder.markdown('*. . . Analyzing term frequency . . .*\n\n')

# body
tf_col1, tf_col2 = st.columns(2)

# set session state to remember filled forms on reload
# initial values for first load
if 'tf_run' not in state:
    state.tf_forms = [
    {   'name':'tf1',
        'kwd':'Terms',
        'date':natsorted(df.cleandate.unique())[0],
        'source':df.source.unique()[0],
        'ngram':1,
        'omit':''
    },
    {   'name':'tf2',
        'kwd':'Terms',
        'date':natsorted(df.cleandate.unique())[0],
        'source':df.source.unique()[0],
        'ngram':2,
        'omit':''
    }]

with tf_col1:

    tf1 = state.tf_forms[0]

    # form to allow user input
    tf1, tf1_submit_button = tf_form(tf1)

    # when button clicked, update data
    if tf1_submit_button:
        state.tf_run = True

    try:
        if tf1['kwd'] == 'Terms':
            t1_df, tf1 = tfproc.get_tf(df, tf1)
        elif tf1['kwd'] == 'TF-IDF':
            t1_df, tf1 = tfproc.get_tfidf(df, tf1)
        elif tf1['kwd'] == 'Keywords':
            t1_df, tf1 = tfproc.get_rake(df, tf1)

        st.markdown(tfproc.results_title(tf1))
        st.table(t1_df)

        # wordcloud
        wc1 = tfproc.get_wc(tf1)
        st.pyplot(wc1)

    except ValueError as ve:
        st.write('There are no results from this search')
        st.write(ve)

    # set values to session state
    state.tf_forms[0] = tf1

with tf_col2:

    tf2 = state.tf_forms[1]

    # form to allow user input
    tf2, tf2_submit_button = tf_form(tf2)

    # when button clicked, update data
    if tf2_submit_button:
        state.tf_run = True

    try:
        if tf2['kwd'] == 'Terms':
            t2_df, tf2 = tfproc.get_tf(df, tf2)
        elif tf2['kwd'] == 'TF-IDF':
            t2_df, tf2 = tfproc.get_tfidf(df, tf2)
        elif tf2['kwd'] == 'Keywords':
            t2_df, tf2 = tfproc.get_rake(df, tf2)


        st.markdown(tfproc.results_title(tf2))
        st.table(t2_df)

        # wordcloud
        wc2 = tfproc.get_wc(tf2)
        st.pyplot(wc2)

    except ValueError:
        st.write('There are no results from this search')

    # set values to session state
    state.tf_forms[1] = tf2

placeholder.empty()
