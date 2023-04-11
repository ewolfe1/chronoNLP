import streamlit as st
state = st.session_state
from scripts import tools, getdata, overviewproc
tools.page_config()
from spacy.lang.en.stop_words import STOP_WORDS
from natsort import natsorted

# load data
if 'init' not in st.session_state:
    ready = getdata.init_data()
else:
    ready= True
state = st.session_state

if ready:
    # placeholder for status updates
    placeholder = st.empty()

    # get source data
    placeholder.markdown('*. . . Initializing . . .*\n\n')
    df_filtered = state.df_filtered

    # header
    st.subheader('Review textual characteristics of the data')
    getdata.df_summary_header()

    # articles by publication
    # placeholder.markdown('*. . . Analyzing item-level data . . .*\n\n')

    tc_placeholder = st.empty()
    tc_placeholder = st.info('Please wait. Processing items . . .')

    total_words, total_wo_common, pos_df = overviewproc.text_features()
    tc_placeholder.empty()

    st.write(f"**Total word count:** {total_words:,}")

    st.write('### Parts of speech analysis')

    st.table(pos_df)

    st.write('### Named entities in the text')
    st.table(overviewproc.get_entities())


    with st.expander('About this page'):
        st.write("""**Part-of-speech (POS) tagging** is a natural language processing (NLP) task \
        that involves labeling words within a text with their corresponding grammatical \
        part of speech, such as noun, verb, adverb, etc.""")
        st.write("""**Named entity recognition (NER) tagging** is another NLP taks that uses \
        statistical predictions to identify and label a variety of named and numeric entities \
        within a given text. There are many potential NER categories, but spaCy reconizes the \
        following:

    * PERSON:      People, including fictional.
    * NORP:        Nationalities or religious or political groups.
    * FAC:         Buildings, airports, highways, bridges, etc.
    * ORG:         Companies, agencies, institutions, etc.
    * GPE:         Countries, cities, states.
    * LOC:         Non-GPE locations, mountain ranges, bodies of water.
    * PRODUCT:     Objects, vehicles, foods, etc. (Not services.)
    * EVENT:       Named hurricanes, battles, wars, sports events, etc.
    * WORK_OF_ART: Titles of books, songs, etc.
    * LAW:         Named documents made into laws.
    * LANGUAGE:    Any named language.
    * DATE:        Absolute or relative dates or periods.
    * TIME:        Times smaller than a day.
    * PERCENT:     Percentage, including ”%“.
    * MONEY:       Monetary values, including unit.
    * QUANTITY:    Measurements, as of weight or distance.
    * ORDINAL:     “first”, “second”, etc.
    * CARDINAL:    Numerals that do not fall under another type.
    https://towardsdatascience.com/explorations-in-named-entity-recognition-and-was-eleanor-roosevelt-right-671271117218""")

        st.write("""This site uses spaCy 3's default model and pipeline ("en_core_web_sm") for \
        POS and NER tagging, which evaulates each word in its context and position within a \
        sentence to automatically assign these and other linguistic labels.""")
        st.write("More information can be found in spaCy's documentation: https://spacy.io/usage/linguistic-features")
    placeholder.empty()
