import streamlit as st
state = st.session_state
from streamlit_extras.switch_page_button import switch_page

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



st.markdown("""This site was built to help facilitate computational exploration of text-based materials with a time component, providing a means to see changes over time and comparing features from different sources.""")

st.markdown("""*Available tools include:*

* A simple interface to adjust the date range or source(s) analyzed
* Detailed summary of the data, including distribution over time and by source
* Parts-of-speech (POS) and Named Entity Recognition
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
        st.write('3,753 news articles relating to COVID-19, published between January 28, 2020 and January 31, 2022.')
        if st.button('Select', key='datapick_douglas'):
            state.init_data = 'douglas'
            state.init = False
            getdata.init_data()
with datapick_cols[1]:
    with st.container():
        st.info('Blog posts')
        st.write("757 blog posts from the History of Black Writing project at the University of Kansas, published between 2011 and 2021.")
        if st.button('Select', key='hbw'):
            state.init_data = 'hbw'
            state.init = False
            getdata.init_data()
with datapick_cols[2]:
    with st.container():
        st.info('Use your own content')
        st.write('Upload your own dataset')
        if st.button('Select', key='datapick_ul'):
            state.init_data = 'ul'
            switch_page('upload_dataset')

# getdata.init_data()
if 'init_data' in state:
    with st.expander('View a sample of the selected data'):
        st.write('')
        st.write(f"You've selected a sample dataset with a total of {len(state.df):,} articles by {len(state.df.source.unique())} publishers. See the *Data Overview* page for more details about this dataset.")
        st.write(state.df[['uniqueID','date','full_text','source','label']].sample(5))

with st.expander('More about the sample datasets'):

    st.write("""***Sample dataset 1***\n
    A collection of 3,753 news articles from six online publications in Douglas County, Kansas published between January 28, 2020 and January 31, 2022.
    Articles were collected from three city publications (The Lawrence Journal-World, The Lawrence Times, and the The Eudora Times)
    and three student university publications (The University Daily Kansan, The Baker Orange, and The Indian Leader).
    Articles were selected as part of a web archiving project identifying online content relating to COVID-19.\n""")

    st.write("""***Sample dataset 2***\n
    A collection of 757 posts from the blog of the History of Black Writing (HBW) project at the University of Kansas, published between 2011 and 2021.
    Learn more about the HBW at https://hbw.ku.edu/.""")

placeholder.empty()
