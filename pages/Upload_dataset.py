import streamlit as st
state = st.session_state
import pandas as pd
import hashlib
from time import sleep
from io import StringIO
from random import randint
from scripts import tools, getdata
tools.page_config()

# def md5(bytes_data):
#     hash_md5 = hashlib.md5()
#     hash_md5.update(bytes_data)
#     return hash_md5.hexdigest()

def empty():
    ul_container.empty()
    sleep(0.01)

def update_upload_step():
    state.upload_step = 2


def ul1():
    empty()
    with ul_container.container():

        st.markdown('### Step 1 of 4 - Upload data file')

        # allow user uploads of different datasets (CSV, JSON)
        st.markdown('This site is designed to allow exploration of text documents with a time-based element. It optionally allows for texts from multiple sources.')
        st.markdown('**Accepted formats:** CSV')
        st.markdown("""
    The follow are the elements that can be accessed in this site. ***Your data does not have to have these headings, as they can be mapped in the next step.***

    * **label** *- a label associated with each item (e.g. title of article, subject) - Optional*
    * **full text** *- the actual text that will be analyzed - Required*
    * **uniqueID** *- a unique identifier for each item in your dataset (e.g. URI, Volume/Issue number, filename) - Required*
    * **source** *- an data point that can enable grouping (e.g. author, publisher) - Optional*
    * **date** *- the date for each item to facilitate a time-based exploration of your data - Required*
    """)


        if 'ul_key' not in state:
            state.ul_key = str(randint(1000, 100000000))

        uploaded_file = st.file_uploader("Select a file", type=['csv','zip'], accept_multiple_files=False, key=state.ul_key)

        if uploaded_file is not None:
            state.uploaded_file = uploaded_file.name
            user_df = getdata.user_upload(uploaded_file)

            if user_df is not None:
                state.user_df = user_df

                st.markdown(f"Your dataset consists of {len(user_df):,} items with {len(user_df.columns)} elements.")
                with st.expander('View a sample of your dataset'):
                    st.table(getdata.display_user_df(user_df))
                    # st.button('Review and continue', on_click=update_upload_step, key=str(randint(1000, 100000000)))
                    # state.upload_step = 2

                if getdata.check_user_df():

                    st.success('Data appears to be already preprocessed. Please identify the date format to continue.')

                    check_data_form = st.form(key='checkuserdata')
                    with check_data_form:
                        check_data_cols = st.columns(2)
                        with check_data_cols[0]:
                            st.write(f"Here is a sample date from your data: {user_df.sample()['date'].values[0]}")
                            state.date_format = st.selectbox('How is the date formatted?',
                                ['Year only (4 digit)','Year, month (any order)',
                                'Year, month, day (day first)','Year, month, day (month first)','None of these'])
                            state.date_access = st.radio('How do you want to be able to group the dates?',['Year','Month','Day'], horizontal=True)
                            check_data_submit = st.form_submit_button('Submit')

                    if check_data_submit:

                        # update dates
                        user_df['date'] = user_df['date'].apply(lambda x: getdata.parse_date(x))
                        user_df['cleandate'] = user_df['date'].apply(lambda x: getdata.get_cleandate(x))

                        daterange = getdata.get_daterange(user_df)
                        getdata.set_user_data(user_df, daterange)

                        empty()
                        with ul_container.container():

                            st.success('Success! You can now use the tools on this site to explore your data.')
                else:
                    st.button('Review and continue', on_click=update_upload_step, key=str(randint(1000, 100000000)))

def ul2():

    empty()
    with ul_container.container():

        st.markdown('### Step 2 of 4 - Review initial data file')
        user_df = state.user_df

        st.table(getdata.display_user_df(user_df))

        userform = st.form(key='userdata')

        procdata = st.empty()

        # get index if column in df
        def get_index(field):
            if field[0] in user_df.columns:
                idx = user_df.columns.tolist().index(field[0])
            elif field[1] in user_df.columns:
                idx = user_df.columns.tolist().index(field[1])
            else:
                idx = 0

            if any(t in field for t in ['title','label','source']):
                idx += 1
            return idx

        with userform:
            st.markdown('To best use the features of this site, please help identify the elements in your data:')
            user_cols = st.columns(3)

            with user_cols[0]:
                user_info = {}
                user_info['label'] = st.selectbox('A single label for the item (optional, e.g., title)', ['No label'] + user_df.columns.tolist(), index=get_index(('label','title')))
                user_info['full_text'] = st.selectbox('Full text (text to be analyzed)', user_df.columns, index=get_index(('full_text','text')))
                user_info['uniqueID'] = st.selectbox('Unique Identifier', user_df.columns, index=get_index(('uniqueID','url')))
                user_info['source'] = st.selectbox('Source (optional field to allow grouping, e.g., author, publisher)', ['No source'] + user_df.columns.tolist(), index=get_index(('source','')))

            with user_cols[1]:
                user_info['date'] =  st.selectbox('Date', user_df.columns, index=get_index(('date','year')))

                # check date format
                def check_date_format():
                    date_sample = str(user_df.sample()['date'].values[0])
                    if len(date_sample) in [6,7]:
                        return 1
                    elif len(date_sample) > 7:
                        return 3
                    else:
                        return 0

                state.date_format = st.selectbox('How is the date formatted?',
                    ['Year only (4 digit)','Year, month (any order)','Year, month, day (day first)','Year, month, day (month first)','None of these'], index=check_date_format())
                state.date_access = st.radio('How do you want to be able to group the dates?',['Year','Month','Day'], horizontal=True)

                st.write(' ')
                user_submit = st.form_submit_button('Preview data')

        # sample data and confirm
        if user_submit:
            user_data_accepted = False
            t_df = user_df[list(set(v for k,v in user_info.items()))].copy()
            t_df.rename(columns = {v:k for k,v in user_info.items()}, inplace = True)

            for c in ['full_text','uniqueID','date']:
                if t_df[c].isnull().values.any():
                    st.write(f"The field **{c}** is required for all rows. You have {t_df[c].isnull().sum()} empty values (of {len(t_df)} rows). Please check your data and try again.")
                    st.stop()
            for c in ['label','source']:
                if user_info[c] == f"No {c}":
                    t_df[c] = f"No {c}"
                elif t_df[c].isnull().values.any():
                    t_df[c] = t_df[c].fillna(f'No {c}')
                    st.write(f"The field **{c}** is an optional field for your data. You have {t_df[c].isnull().sum()} empty values (of {len(t_df)} rows). These values have been auto-filled with the value 'No {c}'.")
                    if st.button('Accept these changes and continue', key=str(randint(1000, 100000000))):
                        user_data_accepted = True
                else:
                    user_data_accepted = True

            if user_data_accepted:
                state.user_df = t_df
                state.upload_step = 3

def ul3():

    empty()
    with ul_container.container():

        st.markdown('### Step 3 of 4 - Review processed data file')
        st.markdown('Please review this data and continue to preprocessing.')

        user_df = state.user_df
        st.table(getdata.display_user_df(user_df))

        st.warning('*Note that, depending on the size of the dataset, the preprocessing step may take quite some time but should only need to be done once per session. Processed data can be downloaded for later re-use and to avoid this step in the future.*')

        if 'userdata' in state:
            state.upload_step = 4
#         st.markdown("""Preprocessing steps include:
#
# * Clean text - remove stopwords and punctuation. Convert to lower case.
# * Create lemmas from clean text.
# * Sentiment analysis of the text.
# * Evaluate readability.
#         """)

        if st.button('Continue to preprocess'):

            user_df = getdata.preprocess(state.user_df)
            daterange = getdata.get_daterange(user_df)

            getdata.set_user_data(user_df, daterange)
            st.experimental_rerun()

            # nlp_placeholder.markdown('***Preprocessing complete***')
def ul4():

    # state.upload_step == 4
    empty()
    with ul_container.container():
        st.markdown('### Step 4 of 4 - Download processed data file')
        st.success('Preprocessing complete. You can now use the tools on this site to explore your data.')

        st.table(getdata.display_user_df(state.df))

        st.markdown('Download the processed data for later use and to avoid re-processing next time.')
        st.download_button('Download CSV', state.df.to_csv(index=False), key=str(randint(1000, 100000000)),
        file_name=state.uploaded_file.replace('.csv','_PREPROCESSED.csv'))

st.markdown('## Upload and pre-process your data')

ul_cols = st.columns((4,1))

ul_container = st.empty()

with ul_cols[1]:
    if st.button('Reset'):
        uploaded_file = None
        state.ul_key = str(randint(1000, 100000000))
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

if state.upload_step == 4:
    ul4()
