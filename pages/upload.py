import streamlit as st
state = st.session_state
import pandas as pd
import hashlib
from time import sleep
from io import StringIO
from scripts import getdata
getdata.page_config()

def md5(bytes_data):
    hash_md5 = hashlib.md5()
    hash_md5.update(bytes_data)
    return hash_md5.hexdigest()

def empty():
    ul_container.empty()
    sleep(0.01)

def ul1():
    empty()
    with ul_container.container():

        st.markdown('### Step 1 of 4 - Upload data file')

        # allow user uploads of different datasets (CSV, JSON)
        st.markdown('This site is designed to allow exploration of text documents with a time-based element. It optionally allows for texts from multiple sources.')
        st.markdown('**Accepted formats:** CSV')
        st.markdown("""
    The follow are the elements that can be accessed in this site. ***Your data does not have to have these headings, as they can be mapped in the next step.***

    * **label** *- a label associated with each item (e.g. title of article, subject)*
    * **full text** *- the actual text that will be analyzed*
    * **uniqueID** *- a unique identifier for each item in your dataset (e.g. URI, Volume/Issue number)*
    * **source** *- an optional field that can enable grouping (e.g. author, publisher)*
    * **date** *- the date for each item to facilitate a time-based exploration of your data (preferred format: YYYY-MM-DD / YYYY-MM / YYYY)*
    """)

        uploaded_file = st.file_uploader("Select a file", type=['csv'], accept_multiple_files=False)

        if uploaded_file is not None:
            state.uploaded_file = uploaded_file.name
            user_df = getdata.user_upload(uploaded_file)

            if user_df is not None:
                state.user_df = user_df

                st.markdown(f"Your dataset consists of {len(user_df):,} items with {len(user_df.columns)} elements.")

                getdata.display_user_df(user_df)

                check_data = getdata.check_user_df()

                if check_data:
                    st.write('Data appears to be already preprocessed. You can now use the tools on this site to explore your data.')
                else:
                    if st.button('Continue'):
                        state.upload_step = 2

def ul2():

    empty()
    with ul_container.container():

        st.markdown('### Step 2 of 4 - Review initial data file')
        user_df = state.user_df

        getdata.display_user_df(user_df)

        userform = st.form(key='userdata')

        procdata = st.empty()

        with userform:
            st.markdown('To best use the features of this site, please help identify the elements in your data:')
            user_cols = st.columns(3)

            with user_cols[0]:
                user_info = {}
                user_info['label'] = st.selectbox('A single label for the item', user_df.columns)
                user_info['full_text'] = st.selectbox('Full text', user_df.columns)
                user_info['uniqueID'] = st.selectbox('Unique Identifier', user_df.columns)
                source = st.selectbox('Source', user_df.columns.tolist() + ['None (single source data)'])
                if source == 'None (single source data)':
                    source = 'Single source'
                user_info['source'] = source

            with user_cols[1]:
                user_info['date'] =  st.selectbox('Date', user_df.columns)
                state.date_format = st.selectbox('How is the date formatted?',
                    ['Year only (4 digit)','Year, month (any order)','Year, month, day (day first)','Year, month, day (month first)','None of these'])
                state.date_access = st.radio('How do you want to be able to group the dates?',['Year','Month','Day'], horizontal=True)

                st.write(' ')
                user_submit = st.form_submit_button('Preview data')

        # sample data and confirm
        if user_submit:
            t_df = user_df[list(set(v for k,v in user_info.items()))].copy()
            t_df.rename(columns = {v:k for k,v in user_info.items()}, inplace = True)

            state.user_df = t_df
            state.upload_step = 3

            # For some reason, the following method retains upload_step==2
            #  with procdata.container():
            #     t_df = user_df[list(set(v for k,v in user_info.items()))].copy()
            #     t_df.rename(columns = {v:k for k,v in user_info.items()}, inplace = True)
            #     state.user_df = t_df
                # st.markdown('Please review this data and continue to preprocessing.')
                # getdata.display_user_df(t_df)
                #
                # if st.button('Accept and continue'):
                #     state.user_df = t_df
                #     state.upload_step = 3

def ul3():

    empty()
    with ul_container.container():

        st.markdown('### Step 3 of 4 - Review processed data file')
        st.markdown('Please review this data and continue to preprocessing.')

        user_df = state.user_df
        getdata.display_user_df(user_df)

        st.markdown('*Note that the preprocessing step will take quite some time but should only need to be done once per session. You will be able to download the processed data for later re-use and to avoid this step in the future.*')

#         st.markdown("""Preprocessing steps include:
#
# * Clean text - remove stopwords and punctuation. Convert to lower case.
# * Create lemmas from clean text.
# * Sentiment analysis of the text.
# * Evaluate readability.
#         """)

        if st.button('Continue to preprocess'):
            nlp_placeholder = st.empty()

            user_df = getdata.preprocess(state.user_df, nlp_placeholder)
            daterange = getdata.get_daterange(user_df)

            set_user_data(user_df, daterange)


            # nlp_placeholder.markdown('***Preprocessing complete***')
            # state.upload_step == 4
            empty()
            with ul_container.container():
                st.markdown('### Step 4 of 4 - Download processed data file')
                st.markdown('Preprocessing complete. You can now use the tools on this site to explore your data.')

                getdata.display_user_df(state.df)

                st.markdown('Download the processed data for later use and to avoid re-processing next time.')
                st.download_button('Download CSV', user_df.to_csv(index=False), file_name=state.uploaded_file.replace('.csv','_PREPROCESSED.csv'))

st.markdown('## Upload and pre-process your data')

ul_cols = st.columns((4,1))

ul_container = st.empty()

with ul_cols[1]:
    if st.button('Reset'):
        empty()
        state.upload_step = 1

if 'upload_step' not in state:
    state.upload_step = 1

if state.upload_step == 1:
    ul1()

if state.upload_step == 2:
    ul2()

if state.upload_step == 3:
    ul3()

# if state.upload_step == 4:

    # empty()
    # with ul_container.container():
    #     st.markdown('### Step 4 of 4 - Download processed data file')
    #     st.markdown('Preprocessing complete. You can now use the tools on this site to explore your data.')
    #
    #     getdata.display_user_df(state.df)
    #
    #     st.markdown('Download the processed data for later use and to avoid re-processing next time.')
    #     st.download_button('Download CSV', user_df.to_csv(index=False), file_name=uploaded_file.name.replace('.csv','_PREPROCESSED.csv'))
