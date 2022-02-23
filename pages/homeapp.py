import streamlit as st
from hydralit import HydraHeadApp
from scripts import getdata

class homeapp(HydraHeadApp):

    def run(self):

        # placeholder for status updates
        placeholder = st.empty()
        placeholder.markdown('*. . . Initializing . . .*\n\n')

        st.markdown("""This site was built to facilitate computational exploration of text-based materials with a time component, providing a means to see changes over time and comparing features from different sources. The sample data included consists of online news articles relating to COVID-19 that were published Douglas County, Kansas.""")

        st.markdown("""*Available tools include:*

        * A simple interface to adjust the date range or source(s) analyzed
        * Detailed summary of the data, including distribution over time and by source
        * Full text searching of the data, plotting the results by frequency over time and by source
        * Sentiment analysis of the data, showing the mean sentiment over time and by source
        * Computationally derived term frequency analysis, allowing a highly customizable means to view statistically significant n-grams used in the texts
        * Topic modeling, with a means to see the weighted distribution of algorithmically derived topics over time
        * An interface to allow user-uploaded datasets with a time component""")

        placeholder.empty()

        with st.expander('View a sample of the current data'):
            # By default, show the current dataset as a truncated
            getdata.display_initial_df(st.session_state.df_filtered)
