import streamlit as st
import pandas as pd
from scripts import getdata, topicproc
getdata.page_config()

# load data
if 'init' not in st.session_state:
    getdata.init_data()

# placeholder for status updates
# placeholder = st.empty()

# header
st.subheader('Filter this dataset')

# date selector
df = st.session_state.df
daterange = st.session_state.daterange
df_filtered = st.session_state.df_filtered

st.write('**Original dataset**')
st.write(f"*Original dataset includes **{len(df):,} items** from **{len(df.source.unique())} sources** ({df['cleandate'].min()} - {df['cleandate'].max()})*")

with st.form(key='filter_data'):

    date_cols = st.columns((2,2,2))

    daterange_full = st.session_state.daterange_full
    daterange = st.session_state.daterange

    with date_cols[0]:
        start_date = st.selectbox('Start date', daterange_full, index=daterange_full.index(st.session_state.start_date))

    with date_cols[1]:
        end_date = st.selectbox('End date', daterange_full, index=daterange_full.index(st.session_state.end_date))

    df_filtered = df[(df['cleandate'] >= start_date) & (df['cleandate'] <= end_date)]
    df_filtered.reset_index(inplace=True)

    daterange = getdata.get_daterange(df_filtered)

    sources = list(df_filtered.source.unique())
    f_sources = st.multiselect('Select source(s) to review (default is all sources)',sources,key='sources_home')

    df_filtered = df_filtered[df_filtered.source.str.contains('|'.join(s.strip() for s in f_sources))]

    st.write("*Filter by keywords*")
    kwd_cols = st.columns((1,4))
    with kwd_cols[0]:

        kwd_filt = st.radio('*Include only results that*', ['Contain','Do not contain'])

    with kwd_cols[1]:
        keywords = st.text_input('')

    if 'not' in kwd_filt:
        df_filtered = df_filtered[~(df_filtered.clean_text.str.contains('|'.join(k.strip() for k in keywords.split())))]
    else:
        df_filtered = df_filtered[df_filtered.clean_text.str.contains('|'.join(k.strip() for k in keywords.split()))]

    filter = st.form_submit_button("Apply filters")

    if filter:
        st.session_state.start_date = start_date
        st.session_state.end_date = end_date
        st.session_state.df_filtered = df_filtered
        st.session_state.daterange = daterange

if 'df_filtered' in st.session_state and len(st.session_state.df_filtered) != len(st.session_state.df):

    st.write('## Filtered dataset')
    getdata.df_summary_header()

    if 'userdata' in st.session_state:

        st.markdown('Download this filtered dataset.')

        if 'uploaded_file' in st.session_state:
            fn = st.session_state.uploaded_file.replace('.csv','_FILTERED.csv')
        else:
            fn = 'filtered_dataset.csv'

        dl_cols = st.columns((1,1,2))
        with dl_cols[0]:
            st.download_button('Download as CSV', df_filtered.to_csv(index=False, encoding='utf_8'), file_name=fn)
        with dl_cols[1]:
            st.download_button('Download as JSON', df_filtered.to_json(orient='records'), file_name=fn.replace('.csv','.json'))

# option to revert to original dataset
st.markdown('## Reset all filters')
reset_btn = st.button('Reset all filters')

if reset_btn:
    getdata.default_vals()
