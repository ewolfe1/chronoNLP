import streamlit as st
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
        st.markdown('**Accepted formats:** CSV, JSON')
        st.markdown("""
    **Allowed elements:**

    * uniqueID (e.g., url)
    * date (preferred format: YYYY-MM-DD / YYYY-MM / YYYY)
    * title
    * full text
    * source (optional)
    """)

        uploaded_file = st.file_uploader("Select a file", type=['csv','json'], accept_multiple_files=False)

        if uploaded_file is not None:

            user_df = getdata.user_upload_prelim(uploaded_file)

            if user_df is not None:

                st.session_state.user_df = user_df

                st.markdown(f"Your dataset consists of {len(user_df):,} items")
                getdata.display_user_df(user_df)

            if st.button('Continue'):
                st.session_state.upload_step = 2

def ul2():

    empty()
    with ul_container.container():

        st.markdown('### Step 2 of 4 - Review initial data file')
        user_df = st.session_state.user_df

        getdata.display_user_df(user_df)

        userform = st.form(key='userdata')

        procdata = st.empty()

        with userform:
            st.markdown('To best use the features of this site, please help identify the data elements:')
            user_cols = st.columns(3)

            with user_cols[0]:
                user_info = {}
                user_info['title'] = st.selectbox('Title of item', user_df.columns)
                user_info['full_text'] = st.selectbox('Full text', user_df.columns)
                user_info['date'] =  st.selectbox('Date', user_df.columns)
            with user_cols[1]:
                user_info['uniqueID'] = st.selectbox('Unique Identifier', user_df.columns)
                source = st.selectbox('Source (optional)', user_df.columns.tolist() + ['None (single source data)'])
                if source == 'None (single source data)':
                    source = 'Single source'
                user_info['source'] = source

                st.write(' ')
                user_submit = st.form_submit_button('Preview data')

        # sample data and confirm
        if user_submit:
            t_df = user_df[list(set(v for k,v in user_info.items()))].copy()
            t_df.rename(columns = {v:k for k,v in user_info.items()}, inplace = True)

            st.session_state.user_df = t_df
            st.session_state.upload_step = 3
            # with procdata.container():
            #     t_df = user_df[list(set(v for k,v in user_info.items()))].copy()
            #     t_df.rename(columns = {v:k for k,v in user_info.items()}, inplace = True)
            #     # st.session_state.user_df = t_df
            #     st.markdown('Please review this data and continue to preprocessing.')
            #     getdata.display_user_df(t_df)
            #
            #     if st.button('Accept and continue'):
            #
            #         st.session_state.upload_step = 3

def ul3():

    empty()
    with ul_container.container():

        st.markdown('### Step 3 of 4 - Review processed data file')
        st.markdown('Please review this data and continue to preprocessing.')

        user_df = st.session_state.user_df
        getdata.display_user_df(user_df)

        st.markdown('*Note that the preprocessing step will take quite some time but should only need to be done once per session. You will be able to download the processed data for later re-use.*')

        nlp_placeholder = st.empty()

        user_df = getdata.preprocess(st.session_state.user_df, nlp_placeholder)#
        daterange = getdata.get_daterange(user_df)

        # tell streamlit we are using user data
        st.session_state.userdata = True
        st.session_state.df = user_df
        st.session_state.df_filtered = user_df
        st.session_state.daterange = daterange
        st.session_state.daterange_full = daterange
        st.session_state.start_date = daterange[0]
        st.session_state.end_date = daterange[-1]
        st.session_state.init = True

        nlp_placeholder.markdown('***Preprocessing complete***')
        getdata.display_user_df(user_df)

st.markdown('## Upload and pre-process your data')

if 'upload_step' not in st.session_state:
    st.session_state.upload_step = 1

ul_container = st.empty()

if st.session_state.upload_step == 1:
    ul1()


if st.session_state.upload_step == 2:
    ul2()


if st.session_state.upload_step == 3:
    ul3()


if st.session_state.upload_step == 4:

    empty()
    with ul_container.container():
        st.markdown('### Step 4 of 4 - Download processed data file')
        st.markdown('Please review this data and continue to preprocessing.')

        getdata.display_user_df(st.session_state.df)

        st.markdown('Download the processed data for later use and to avoid re-processing next time.')
        st.download_button('Download CSV', user_df.to_csv(index=False), file_name=uploaded_file.name.replace('.csv','_PREPROCESSED.csv'))
        # st.session_state.uploaded_file = uploaded_file.name

            #     nlp_placeholder = st.empty()
            #     data_placeholder = st.empty()
            #
            #     with data_placeholder.container():
            #
            #         st.markdown('Please review the data')
            #
            #
            #         st.markdown(f"""
            #         Your dataset consists of:
            #
            #             * Number of items: {len(user_df):,}
            #             * Number of sources: {len(user_df.source.unique())}
            #             * Date range: {user_df.date.min().date()} - {user_df.date.max().date()}
            #         """)
            #

            #     if st.button('Preprocess data'):
            #
            #         # preprocessing on the fly
            #         user_df = getdata.preprocess(user_df, nlp_placeholder)
            #
            #         # sentiment analysis - ~ 30 seconds for 3,500 articles
            #         user_df = getdata.get_sa(user_df)
            #         daterange = getdata.get_daterange(user_df)
            #
            #         # tell streamlit we are using user data
            #         st.session_state.userdata = True
            #         st.session_state.df = user_df
            #         st.session_state.df_filtered = user_df
            #         st.session_state.daterange = daterange
            #         st.session_state.daterange_full = daterange
            #         st.session_state.start_date = daterange[0]
            #         st.session_state.end_date = daterange[-1]
            #         st.session_state.init = True
            #
            #         nlp_placeholder.markdown('***Preprocessing complete***')
            #         preproc = True
            #
            # if preproc:
            #     with data_placeholder.container():
            #
            #         getdata.display_user_df(st.session_state.df)
            #
            #         st.markdown('Download the processed data for later use and to avoid re-processing next time.')
            #         st.download_button('Download CSV', user_df.to_csv(index=False), file_name=uploaded_file.name.replace('.csv','_PREPROCESSED.csv'))
            #         st.session_state.uploaded_file = uploaded_file.name
