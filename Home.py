import streamlit as st
state = st.session_state

#--- I don't understand the necessity of this line. But it is needed
#    to preserve session_state in the cloud. Not locally.
# st.session_state.update(st.session_state)

from scripts import tools, getdata
tools.page_config()

# hack for styling - may be deprecated in future
st.write("""<style>
            div.stSlider{padding:1em 2em}
            img{max-width:75%;margin: auto}
            div.streamlit-expanderHeader{background-color:#8A93DE; color:#ffffff}
            div.row-widget.stRadio > div{flex-direction:row;justify-content: center} #center radio buttons
            table{width:fit-content; min-width:50%;  margin: 0 auto 1rem auto}
            </style>""", unsafe_allow_html=True)



st.markdown("""This site was built to facilitate computational exploration of text-based materials with a time component, providing a means to see changes over time and comparing features from different sources.""")

st.markdown("""*Available tools include:*

* A simple interface to adjust the date range or source(s) analyzed
* Detailed summary of the data, including distribution over time and by source
* Full text searching of the data, plotting the results by frequency over time and by source
* Computationally derived term frequency analysis, allowing a highly customizable means to view statistically significant n-grams used in the texts
* Topic modeling, with a means to see the weighted distribution of algorithmically derived topics over time
* An interface to allow user-uploaded datasets with a time component""")

# placeholder for status updates
placeholder = st.empty()


st.markdown("### Pick a sample dataset to get started")
datapick_cols = st.columns(3)
with datapick_cols[0]:
    with st.container():
        st.info('News articles')
        st.write('3,804 online news articles relating to COVID-19 that were published Douglas County, Kansas between January 28, 2020 and January 31, 2022.')
        if st.button('Select', key='datapick_douglas'):
            state.init_data = 'douglas'
            state.init = False
            getdata.init_data()
with datapick_cols[1]:
    with st.container():
        st.info('Placeholder')
        st.write("Placeholder")
        if st.button('Select', key='placeholder'):
            # state.init_data = 'placeholder'
            state.init = False
            # getdata.init_data()
with datapick_cols[2]:
    with st.container():
        st.info('Use your own content')
        st.write('Upload your own dataset')
        if st.button('Select', key='datapick_ul'):
            state.init_data = 'ul'
            tools.switch_page('Upload_dataset')

# getdata.init_data()
if 'init_data' in state:
    with st.expander('View a sample of the selected data'):
        st.write('')
        st.write(f"You've selected a sample dataset with a total of {len(state.df):,} articles by {len(state.df.source.unique())} publishers. *See the Data Overview page for more details about this dataset.*")
        st.write(state.df[['uniqueID','date','full_text','source','label']].sample(5))

placeholder.empty()
