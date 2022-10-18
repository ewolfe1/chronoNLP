import streamlit as st
# state = st.session_state


# set page configuration. Can only be set once per session and must be first st command called
def page_config():

    try:
        st.set_page_config(page_title='Text Explorer', page_icon=':newspaper:', layout='wide') #,initial_sidebar_state='collapsed')
    except st.errors.StreamlitAPIException as e:
        if "can only be called once per app" in e.__str__():
            return

# Note: this is a hack that may break in the future
# Could be cleaned up a bit
def switch_page(page_name):
    from streamlit import _RerunData, _RerunException
    from streamlit.source_util import get_pages

    def standardize_name(name: str) -> str:
        return name.lower().replace("_", " ")

    page_name = standardize_name(page_name)

    pages = get_pages("Home.py")

    for page_hash, config in pages.items():
        if standardize_name(config["page_name"]) == page_name:
            raise _RerunException(
                _RerunData(
                    page_script_hash=page_hash,
                    page_name=page_name,
                )
            )

    page_names = [standardize_name(config["page_name"]) for config in pages.values()]

    raise ValueError(f"Could not find page {page_name}. Must be one of {page_names}")
