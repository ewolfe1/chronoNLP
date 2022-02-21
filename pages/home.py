import streamlit as st
from hydralit import HydraHeadApp
from scripts import getdata

class home(HydraHeadApp):

    def run(self):

        # placeholder for status updates
        placeholder = st.empty()
        placeholder.markdown('*. . . Initializing . . .*\n\n')

        st.markdown('This site was built to facilitate exploration of the online text-based news coverage in Douglas County, Kansas of COVID-19. It can be used for text analysis and visualization of other textual datasets with a time-based component.')
        st.markdown('***Data sample***')

        # By default, show the current dataset as a truncated
        getdata.display_df(st.session_state.df_filtered)

        placeholder.empty()
