import streamlit as st
from hydralit import HydraHeadApp

class home(HydraHeadApp):

    def run(self):

        x = 'x'
        # # Below is a framework for allowing user uploads of different datasets
        # # It is incomplete, and not yet implemented
        # data_select_btn = st.radio('TEST', ['Use existing dataset','Upload a different dataset'])
        #
        # if data_select_btn == 'Use existing dataset':
        #     display_df(st.session_state.df_filtered)
        #
        # elif data_select_btn == "Upload a different dataset":
        #
        #     st.markdown('Upload your own dataset in CSV or Excel format.')
        #     st.markdown('Required columns are (1) URL, (2) date, (3) source (i.e. publisher), (4) title, and (5) full text')
        #
        #     uploaded_file = st.file_uploader("Please upload a file in CSV or Excel format")
        #
        #     if uploaded_file is not None:
        #         if uploaded_file.name.split('.')[-1] == 'csv':
        #             st.session_state.df = pd.read_csv(uploaded_file)
        #             display_df(st.session_state.df)
        #         elif uploaded_file.name.split('.')[-1] in ['xls','xlsx']:
        #             st.session_state.df = pd.read_excel(uploaded_file)
        #             display_df(st.session_state.df)
        #         else:
        #             st.markdown(f"You uploaded {uploaded_file.name}")
        #             st.markdown("Please upload in CSV, XLS, or XLSX format")
