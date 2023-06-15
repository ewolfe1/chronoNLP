import streamlit as st
from scripts import tools, getdata, overviewproc
tools.page_config()
tools.css()

# load data
if 'init' not in st.session_state:
    ready = getdata.init_data()
else:
    ready= True
state = st.session_state

if ready:
    # placeholder for status updates
    placeholder = st.empty()

    # get source data
    placeholder.markdown('*. . . Initializing . . .*\n\n')

    df_filtered = state.df_filtered

    # header
    st.subheader('Get an overview of the data')
    getdata.df_summary_header()

    # articles by publication
    placeholder.markdown('*. . . Analyzing item-level data . . .*\n\n')

    st.write('### Distribution of texts')
    dist_val = st.radio('Select graphing method',
                        ['Number of items', 'Word count'],
                        horizontal=True)
    st.plotly_chart(overviewproc.items_by_source(dist_val), use_container_width=True)

    st.write('### Analysis of items by source')
    st.dataframe(overviewproc.get_tech_details(), use_container_width=True)

    placeholder.empty()
