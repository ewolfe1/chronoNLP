import streamlit as st
# state = st.session_state


# set page configuration. Can only be set once per session and must be first st command called
def page_config():

    try:
        st.set_page_config(page_title='Text Explorer', page_icon=':newspaper:', layout='wide') #,initial_sidebar_state='collapsed')
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            return
