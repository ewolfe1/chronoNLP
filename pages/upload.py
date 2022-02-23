import streamlit as st
from hydralit import HydraHeadApp
from scripts import getdata
import pandas as pd
import hashlib
from io import StringIO

class upload(HydraHeadApp):

    def run(self):

        def md5(bytes_data):
            hash_md5 = hashlib.md5()
            hash_md5.update(bytes_data)
            return hash_md5.hexdigest()

        st.markdown('## Upload a different dataset')

        # Below is a framework for allowing user uploads of different datasets
        # It is incomplete, and not yet implemented
        st.markdown('***This feature is still in development, and is not fully functional.***')
        st.markdown('Upload your own dataset in CSV or Excel format.')
        st.markdown('Required columns are (1) url, (2) date, (3) source (i.e. publisher), (4) title, and (5) full_text')

        uploaded_file = st.file_uploader("Please upload a file in CSV or Excel format")

        if uploaded_file is not None:

            # # check for already existing data
            # bytes_data = uploaded_file.getvalue()
            # uploaded_hash = md5(bytes_data)
            # hashname = f'{uploaded_file.name}_hash'
            #
            # if (hashname in st.session_state) and (st.session_state[hashname] == uploaded_hash):
            #     st.write(f'y - {st.session_state[hashname]}')
            # else:
            #     st.session_state[hashname] = uploaded_hash
            #     st.write(uploaded_hash)

            user_df = getdata.user_upload(uploaded_file)
            preproc = False

            if user_df is not None:

                #st.session_state.hashname = hashlib.md5()

                nlp_placeholder = st.empty()
                data_placeholder = st.empty()

                with data_placeholder.container():

                    st.markdown('Please review the data and click the button below to proceed. Note that the preprocessing step will take quite some time but should only need to be done once.')

                    st.markdown(f"""
                    Your dataset consists of:

                    * Number of items: {len(user_df):,}
                    * Number of sources: {len(user_df.source.unique())}
                    * Date range: {user_df.date.min()} - {user_df.date.max()}
                    """)

                    getdata.display_user_df(user_df)

                    if st.button('Preprocess data'):

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
                        preproc = True

            if preproc:
                with data_placeholder.container():

                    getdata.display_user_df(st.session_state.df)

                    st.markdown('Download the processed data for later use and to avoid re-processing next time.')
                    st.download_button('Download CSV', user_df.to_csv(index=False), file_name=uploaded_file.name.replace('.csv','_UPDATED.csv'))
