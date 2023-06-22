import streamlit as st
state = st.session_state
from scripts import tools, getdata, overviewproc
tools.page_config()
tools.css()
from spacy.lang.en.stop_words import STOP_WORDS
from natsort import natsorted
from st_aggrid import AgGrid, JsCode, GridOptionsBuilder

# load data
if 'init' not in st.session_state:
    ready = getdata.init_data()
else:
    ready= True
state = st.session_state

if ready:
    # placeholder for status updates
    placeholder = st.empty()
    tools.css()

    # get source data
    placeholder.markdown('*. . . Initializing . . .*\n\n')
    df_filtered = state.df_filtered

    # header
    st.subheader('Review textual characteristics of the data')
    getdata.df_summary_header()

    tc_placeholder = st.empty()

    tc_tabs1, tc_tabs2 = st.tabs(['Parts of speech', 'Named entities'])
    with tc_tabs1:
        st.write('### Parts of speech analysis')
        num_tc_cols = st.columns((2,1,5))
        with num_tc_cols[0]:
            num_tc = st.slider('Number of results to display', 5, 50, value=15, step=5, key="num_tc")
        with num_tc_cols[2]:
            with st.expander('More about parts of speech'):
                st.write("""**Part-of-speech (POS) tagging** is a natural language processing (NLP) task \
                that involves labeling words within a text with their corresponding grammatical \
                part of speech, such as noun, verb, adverb, etc.""")
                st.write("""This site uses spaCy 3's default model and pipeline ("en_core_web_sm") for \
                POS and NER tagging, which evaulates each word in its context and position within a \
                sentence to automatically assign these and other linguistic labels.""")
                st.write("More information can be found in spaCy's documentation: https://spacy.io/usage/linguistic-features")
        tc_placeholder = st.info('Please wait. Processing items . . .')
        total_words, df_pos = overviewproc.text_features(num_tc)
        tc_placeholder.empty()

        tc_placeholder.write(f"**Total word count:** {total_words:,}")

        st.write(df_pos)

    with tc_tabs2:
        st.write('### Named entities in the text')
        num_ent_cols = st.columns((2,1,5))
        with num_ent_cols[0]:
            num_ent = st.slider('Number of results to display', 5, 50, value=15, step=5, key="num_ent")
        with num_ent_cols[2]:
            with st.expander('More about named entities'):
                st.write("""**Named entity recognition (NER) tagging** is a common NLP task that uses \
                statistical predictions to identify and label a variety of named and numeric entities \
                within a given text. There are many potential NER categories, but spaCy reconizes the \
                following:""")

                st.markdown("""<ul style="margin:0 0 2em 2em;">
                    <li>CARDINAL: Numerals that do not fall under another type.</li>
                    <li>DATE: Absolute or relative dates or periods.</li>
                    <li>EVENT: Named hurricanes, battles, wars, sports events, etc.</li>
                    <li>FAC: Buildings, airports, highways, bridges, etc.</li>
                    <li>GPE: Countries, cities, states.</li>
                    <li>LAW: Named documents made into laws.</li>
                    <li>LANGUAGE: Any named language.</li>
                    <li>LOC: Non-GPE locations, mountain ranges, bodies of water.</li>
                    <li>MONEY: Monetary values, including unit.</li>
                    <li>NORP: Nationalities or religious or political groups.</li>
                    <li>ORDINAL: “first”, “second”, etc.</li>
                    <li>ORG: Companies, agencies, institutions, etc.</li>
                    <li>PERCENT: Percentage, including ”%“.</li>
                    <li>PERSON: People, including fictional.</li>
                    <li>PRODUCT: Objects, vehicles, foods, etc. (Not services.)</li>
                    <li>QUANTITY: Measurements, as of weight or distance.</li>
                    <li>TIME: Times smaller than a day.</li>
                    <li>WORK_OF_ART: Titles of books, songs, etc.</li>
                </ul>""", unsafe_allow_html=True)

                st.write("""This site uses spaCy 3's default model and pipeline ("en_core_web_sm") for \
                POS and NER tagging, which evaulates each word in its context and position within a \
                sentence to automatically assign these and other linguistic labels.""")
                st.write("More information can be found in spaCy's documentation: https://spacy.io/usage/linguistic-features")
        overviewproc.get_entities(num_ent)

    placeholder.empty()
