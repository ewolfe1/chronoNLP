import streamlit as st
from scripts import tools, getdata, overviewproc
tools.page_config()

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

    st.plotly_chart(overviewproc.items_by_source(), use_container_width=True)

    st.write('### Analysis of items by source')
    st.dataframe(overviewproc.get_tech_details(), use_container_width=True)

    st.write('### Textual characteristics of the dataset')
    tc_placeholder = st.empty()
    tc_placeholder = st.info('Please wait. Processing . . .')

    total_words, total_wo_common, pos_df = overviewproc.text_features()
    tc_placeholder.empty()
    st.write(f"**Total words:** {total_words:,}")
    st.write(f"**Total words (Common words removed):** {total_wo_common:,}")
    st.table(pos_df)

    placeholder.empty()
