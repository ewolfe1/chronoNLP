import streamlit as st
from hydralit import HydraHeadApp

class home(HydraHeadApp):

    def run(self):

        def display_df(df):
            # display truncated dataset
            t_df = df[['url','date','title','full_text','source']].sort_values(by='date').sample(5).copy().assign(hack='').set_index('hack')
            for c in['url','full_text','title']:
                t_df[c] = t_df[c].apply(lambda x: x[:100] + '...')

            st.table(t_df)

        # placeholder for status updates
        placeholder = st.empty()
        placeholder.markdown('*. . . Initializing . . .*\n\n')

        st.markdown('Welcome to the newspaper analyzer.')
        st.markdown('***Data sample***')

        # By default, show the current dataset as a truncated
        display_df(st.session_state.df_filtered)

        placeholder.empty()
