import streamlit as st
from scripts import getdata
getdata.page_config()

# hack for styling - may be deprecated in future
st.write("""<style>
            div.stSlider{padding:1em 2em}
            img{max-width:75%;margin: auto}
            div.streamlit-expanderHeader{background-color:#8A93DE; color:#ffffff}
            div.row-widget.stRadio > div{flex-direction:row;justify-content: center} #center radio buttons
            table{width:fit-content; min-width:50%;  margin: 0 auto 1rem auto}
            </style>""", unsafe_allow_html=True)



st.markdown("""This site was built to facilitate computational exploration of text-based materials with a time component, providing a means to see changes over time and comparing features from different sources. The sample data included consists of online news articles relating to COVID-19 that were published Douglas County, Kansas.""")

st.markdown("""*Available tools include:*

* A simple interface to adjust the date range or source(s) analyzed
* Detailed summary of the data, including distribution over time and by source
* Full text searching of the data, plotting the results by frequency over time and by source
* Sentiment analysis of the data, showing the mean sentiment over time and by source
* Computationally derived term frequency analysis, allowing a highly customizable means to view statistically significant n-grams used in the texts
* Topic modeling, with a means to see the weighted distribution of algorithmically derived topics over time
* An interface to allow user-uploaded datasets with a time component""")

# placeholder for status updates
placeholder = st.empty()
placeholder.markdown('*. . . Initializing . . .*\n\n')
placeholder.empty()
