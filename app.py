from hydralit import HydraApp
import hydralit_components as hc
import streamlit as st
st.set_page_config(page_title='News Article Explorer', page_icon=':newspaper:', layout='wide') #,initial_sidebar_state='collapsed')
from datetime import datetime
from natsort import natsorted

# Custom imports
from scripts import getdata, loader
from pages import home, technical, sentiment, termfreq, topics, search, upload


# hack for styling - may be deprecated in future
st.write("""<style>s
            div.stSlider{padding:0 2em 0 2em}
            img{max-width:75%;margin: auto}
            div.streamlit-expanderHeader{background-color:#8A93DE; color:#ffffff}
            div.row-widget.stRadio > div{flex-direction:row;justify-content: center} #center radio buttons
            table{width:fit-content; min-width:50%;  margin: 0 auto 1rem auto}
            </style>""", unsafe_allow_html=True)


def get_date_range(start_date, end_date, df):
    start_date, end_date = st.select_slider('',
         options=daterange, value=(daterange[0],daterange[-1]), key='date_init')
    df_filtered = df[(df['cleandate'] >= start_date) & (df['cleandate'] <= end_date)]

    return start_date, end_date, df_filtered

# start app
over_theme = {'txc_inactive': '#ffffff','menu_background':'#8A93DE'}
app = HydraApp(
    title='Exploring newspaper data',
    favicon=':newspaper:',
    hide_streamlit_markers=False,
    use_navbar=True,
    navbar_sticky=True,
    navbar_animation=False,
    navbar_theme=over_theme
)

# Add all your application here
# app.add_app("Home", home.home())
app.add_app("Technical analysis", technical.technical())
app.add_app("Search", search.search())
app.add_app("Sentiment analysis", sentiment.sentiment())
app.add_app("Term frequency", termfreq.termfreq())
app.add_app("Topic modeling", topics.topics())
app.add_app("Upload data", upload.upload())

# override default loader
app.add_loader_app(loader.MyLoadingApp(delay=0))

# set input data files
current_csv = 'data/current_articles.csv'
tk_js = 'data/tokenizer.json'
case_csv = 'data/us-counties-douglas-ks.csv'

# placeholder for status updates
placeholder = st.empty()
placeholder.markdown('*. . . Initializing . . .*\n\n')

# configure data range and filter data
df = getdata.get_data(current_csv, tk_js)
df, daterange = getdata.get_daterange(df)

placeholder.markdown('*. . . Pre-processing data . . .*\n\n')

# leave as placeholder for preprocessing on the fly
# much quicker to do in advance (~5 min for 3,500 articles)
# df = getdata.preprocess(df)

# sentiment analysis - ~ 30 seconds for 3,500 articles
df = getdata.get_sa(df)

if 'userdata' not in st.session_state:

    st.session_state.df = df
    st.session_state.daterange = daterange

placeholder.empty()

# date selector
with st.sidebar:

    df = st.session_state.df
    daterange = st.session_state.daterange

    start_date, end_date = st.select_slider('Select a custom date range',
         options=daterange, value=(daterange[0],daterange[-1]), key='date_home')
    df_filtered = df[(df['cleandate'] >= start_date) & (df['cleandate'] <= end_date)]
    df_filtered.reset_index(inplace=True)
    date_df = getdata.get_date_df(df_filtered)
    st.session_state.daterange = getdata.get_daterange(df_filtered)
    try:
        s_date = datetime.strftime(datetime.strptime(df_filtered.date.min(), "%Y-%m-%d"), "%B %-d, %Y")
        e_date = datetime.strftime(datetime.strptime(df_filtered.date.max(), "%Y-%m-%d"), "%B %-d, %Y")
    except:
        s_date = df_filtered.date.min()
        e_date = df_filtered.date.max()

    sources = list(df_filtered.source.unique())
    st.multiselect('Select source(s) to review (default is all sources)',sources,key='sources_home')

    data_summ = f'Reviewing data for **{len(df_filtered):,} articles** from **{len(df_filtered.source.unique())} sources** ({s_date} - {e_date})'
    st.markdown(data_summ)

st.session_state.start_date = start_date
st.session_state.s_date = s_date
st.session_state.end_date = end_date
st.session_state.e_date = e_date
st.session_state.df_filtered = df_filtered
st.session_state.date_df = date_df
st.session_state.daterange = daterange
st.session_state.case_csv = case_csv
# st.session_state.data_summ = data_summ

placeholder.empty()

# The main app
app.run()
