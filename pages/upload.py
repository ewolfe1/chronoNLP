import streamlit as st
from hydralit import HydraHeadApp
from scripts import getdata

class upload(HydraHeadApp):

    def run(self):

        st.markdown('## Upload a different dataset')

        # Below is a framework for allowing user uploads of different datasets
        # It is incomplete, and not yet implemented
        st.markdown('***This feature is still in development, and is not yet functional.***')
        st.markdown('Upload your own dataset in CSV or Excel format.')
        st.markdown('Required columns are (1) url, (2) date, (3) source (i.e. publisher), (4) title, and (5) full_text')

        uploaded_file = st.file_uploader("Please upload a file in CSV or Excel format")

        if uploaded_file is not None:

            user_df = getdata.user_upload(uploaded_file)

            if user_df is not None:
                getdata.display_df(user_df)

                st.markdown('Please review the data and click to proceed. Note that the preprocessing step will take quite some time but should only need to be done once.')
                if st.button('Preprocess data'):

                    nlp_placeholder = st.empty()

                    # preprocessing on the fly
                    # much quicker to do in advance (~5 min for 3,500 articles)
                    user_df = getdata.preprocess(user_df, nlp_placeholder)

                    # sentiment analysis - ~ 30 seconds for 3,500 articles
                    user_df = getdata.get_sa(user_df)
                    user_df, daterange = getdata.get_daterange(user_df)

                    # tell streamlit we are using user data
                    st.session_state.userdata = True
                    st.session_state.df = user_df
                    st.session_state.daterange = daterange

                    nlp_placeholder.markdown('Preprocessing complete')

                    getdata.display_df(st.session_state.df)
