import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from natsort import natsorted
from scripts import tfproc
import textblob
import subprocess
import sys
from scripts import getdata, tfproc
getdata.page_config()

@st.cache
def tb_corpora():
    cmd = [f"{sys.executable}","-m","textblob.download_corpora"]
    subprocess.run(cmd)
    state.dl_corpora = True

# load data
if 'init' not in state:
    getdata.init_data()
df = state.df_filtered

# placeholder for status updates
placeholder = st.empty()

st.subheader('Term frequency')
getdata.df_summary_header()

# load corpus
if 'dl_corpora' not in state:
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
    tf1, tf1_submit_button = tfproc.tf_form(tf1)

    # when button clicked, update data
    if tf1_submit_button:
        state.tf_run = True

    # plot results
    tfproc.tf_results(tf1)

    # set values to session state
    state.tf_forms[0] = tf1

with tf_col2:

    tf2 = state.tf_forms[1]

    # form to allow user input
    tf2, tf2_submit_button = tfproc.tf_form(tf2)

    # when button clicked, update data
    if tf2_submit_button:
        state.tf_run = True

    # plot results
    tfproc.tf_results(tf2)

    # set values to session state
    state.tf_forms[1] = tf2

placeholder.empty()
