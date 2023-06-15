import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from natsort import natsorted
from scripts import tools, tfproc
import textblob
import subprocess
import sys
from scripts import tools, getdata, tfproc
tools.page_config()
tools.css()

@st.cache_resource
def tb_corpora():
    cmd = [f"{sys.executable}","-m","textblob.download_corpora"]
    subprocess.run(cmd)
    state.dl_corpora = True

# load data
if 'init' not in st.session_state:
    ready = getdata.init_data()
else:
    ready= True

if ready:
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

    with st.expander('About this page'):
        st.write("""**Term frequency (TF)** is a common natural language processing (NLP) process which \
        calculates the number of times a term (word or phrase) appears in a document, at times \
        relative to the total number of terms in the document. It is often used as a basic \
        feature for tasks such as document classification or simple usage over time.""")
        st.write("""**"Term Frequency-Inverse Document Frequency" (TF-IDF)** is a numerical \
        logarithmic calculation that is a more specific type of term frequency calculation. \
        **Inverse Document Frequency (IDF)** calculates the number of documents that contain \
        the term, in comparison to the total number of documents in the set. TF-IDF uses these two\
        figures to assign weights to different terms, giving a higher weight to terms that have \
        higher frequency within a specific document (higher TF) and lower frequency across the \
        entire collection of documents (lower IDF). This helps identify terms that are both \
        important within a document and distinctive across the collection of documents.""")
        st.write("""This site uses a combination of the Natural Language Toolkit (NLTK), TextBlob, \
        and scikit-learn libraries in Python for these calculations.""")
        st.write("""More information can be found in the respective documentation: \
        https://www.nltk.org/api/nltk.html, https://textblob.readthedocs.io/en/dev/, \
        https://scikit-learn.org/stable/user_guide.html""")
placeholder.empty()
