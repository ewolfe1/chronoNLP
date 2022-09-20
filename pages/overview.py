import streamlit as st
state = st.session_state
from scripts import getdata, overviewproc
getdata.page_config()


# load data
if 'init' not in state:
    getdata.init_data()
df_filtered = state.df_filtered

# placeholder for status updates
placeholder = st.empty()

# get source data
placeholder.markdown('*. . . Initializing . . .*\n\n')

# header
st.subheader('Overview of the data')
getdata.df_summary_header()

# articles by publication
placeholder.markdown('*. . . Analyzing item-level data . . .*\n\n')

st.plotly_chart(overviewproc.items_by_source(), use_container_width=True)

st.write('### Analyis of items by source')
st.table(overviewproc.get_tech_details())

st.write('### Textual characteristics of the dataset')
total_words, total_wo_common, pos_df = overviewproc.text_features()
st.write(f"**Total words:** {total_words:,}")
st.write(f"**Total words (Common words removed):** {total_wo_common:,}")
st.table(pos_df)

placeholder.empty()
