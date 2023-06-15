import streamlit as st
import os
# state = st.session_state


# set page configuration. Can only be set once per session and must be first st command called
def page_config():

    try:
        st.set_page_config(page_title='ChronoNLP', page_icon=':newspaper:', layout='wide') #,initial_sidebar_state='collapsed')
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            return

def css():

    with open(os.path.abspath('style.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
