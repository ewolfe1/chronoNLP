import streamlit as st
state = st.session_state
import pandas as pd
from scripts import tools, getdata, topicproc
tools.page_config()

# load data
if 'init' not in state:
    getdata.init_data()

# placeholder for status updates
# placeholder = st.empty()

# header
st.subheader('Filter this dataset')

# date selector
df = state.df
daterange = state.daterange
df_filtered = state.df_filtered

st.write(f"""The original dataset includes **{len(df):,} items** from **{len(df.source.unique())} sources** ({df['cleandate'].min()} - {df['cleandate'].max()}).
Use these filters to review any subset of the data that you wish. Note that filtered datasets can be exported for later review.""")

with st.form(key='filter_data'):

    date_cols = st.columns((2,2,2))

    daterange_full = state.daterange_full
    daterange = state.daterange

    with date_cols[0]:
        start_date = st.selectbox('Start date', daterange_full, index=daterange_full.index(state.start_date))

    with date_cols[1]:
        end_date = st.selectbox('End date', daterange_full, index=daterange_full.index(state.end_date))

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
        state.start_date = start_date
        state.end_date = end_date
        state.df_filtered = df_filtered
        state.daterange = daterange

if 'df_filtered' in state and len(state.df_filtered) != len(state.df):

    st.write('## Filtered dataset')
    getdata.df_summary_header()

    if 'userdata' in state:

        st.markdown('Download this filtered dataset.')

        if 'uploaded_file' in state:
            fn = state.uploaded_file.replace('.csv','_FILTERED.csv')
        else:
            fn = 'filtered_dataset.csv'

        dl_cols = st.columns((1,3))
        with dl_cols[0]:
            st.download_button('Download as CSV', df_filtered.to_csv(index=False, encoding='utf_8'), file_name=fn)

# option to revert to original dataset
st.markdown('## Reset all filters')
reset_btn = st.button('Reset all filters')

if reset_btn:
    getdata.default_vals()
