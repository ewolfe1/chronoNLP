import pandas as pd
import numpy as np
from natsort import natsorted
from datetime import datetime
from dateutil.parser import parse
import streamlit as st
state = st.session_state
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacytextblob.spacytextblob import SpacyTextBlob
import seaborn as sns

import textdescriptives as td
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
from ast import literal_eval


# set page configuration. Can only be set once per session and must be first st command called
def page_config():

    if 'config' not in state:
        st.set_page_config(page_title='Text Explorer', page_icon=':newspaper:', layout='wide') #,initial_sidebar_state='collapsed')
    state.config = True

# load NLP model for spaCy
@st.experimental_memo
def load_model():

    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        spacy.cli.download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")

    # add some additional stopwords to list
    nlp.Defaults.stop_words |= {'the','we','she','he','said','it','like'}
    nlp.add_pipe('textdescriptives')
    nlp.add_pipe("spacytextblob")

    return nlp

nlp = load_model()


# get date range from df
def get_daterange(df):
    # get a list of dates represented in the data
    daterange = [d for d in natsorted(df['cleandate'].unique().tolist()) if d not in ['',None]]
    state.daterange = daterange

    return daterange

# format date
def format_dates(d):

    try:
        d = datetime.strftime(datetime.strptime(d, "%Y-%m-%d"), "%B %-d, %Y")
    except:
        try:
            d = datetime.strftime(datetime.strptime(d, "%Y-%m"), "%B %Y")
        except:
            try:
                d = datetime.strftime(datetime.strptime(d, "%Y"), "%Y")
            except:
                pass

    return d

# df summary header
def df_summary_header():

    df = state.df_filtered
    daterange = state.daterange
    st.write(f'*Working dataset includes **{len(df):,} items** from **{len(df.source.unique())} sources** ({daterange[0]} - {daterange[-1]})*')

# sentiment analysis
@st.experimental_memo
def get_sa(df):

    nltk.download('vader_lexicon')
    analyzer = SentimentIntensityAnalyzer()

    def return_sa(text):
        try:
            return analyzer.polarity_scores(text)['compound']
        except AttributeError:
            return None

    # compound is weighted average; other measures are neg, neu, pos
    df['compound'] = df['full_text'].apply(lambda x: return_sa(x))
    df['label_compound'] = df['label'].apply(lambda x: return_sa(x))

    return df

# format date based on user preference
def get_cleandate(x):

    if state['date_access'] == 'Year':
        return f'{x.year}'
    elif state['date_access'] == 'Month':
        return f'{x.year}-{x.month:02}'
    else:
        return f'{x.year}-{x.month:02}-{x.day:02}'

# parse dates for grouping
def parse_date(x):
    # format date
    if 'date_format' in state and 'day first' in state['date_format']:
        try:
            return parse(str(x), default=datetime(2022, 1, 1), dayfirst=True)
        except:
            print('No Date or Invalid Date')
            return None
    else:
        try:
            return parse(str(x), default=datetime(2022, 1, 1))
        except:
            print('No Date or Invalid Date')
            return None

def clean_tok(t):
    return t.strip().replace("’","'").replace(" - ","")

# pre-processing texts (cleaning, lemmas, readability)
@st.experimental_memo(suppress_st_warning=True)
def preprocess(df, _nlp_placeholder):

    # check for already preprocessed data
    cols_to_check = ['clean_text','lemmas','grade_level','readability',
                    'polarity','subjectivity','compound','label_compound',
                    'pos_all','entities_all']

    if all((c in df.columns) and (df[c].count()==len(df)) for c in cols_to_check):
        st.markdown('Data appears to be already preprocessed.')
        return df

    # create placeholder columns
    for c in cols_to_check:
        if c not in df.columns:
            df[c] = None

    # processing count
    ct = 1
    _nlp_placeholder = st.empty()

    for i,r in df.iterrows():

        _nlp_placeholder.markdown(f'Processing item {ct:,} of {len(df):,} ({int(ct/len(df)*100)}% complete)')

        if not r[cols_to_check].isnull().any():
            continue

        # call spaCy for cleanup and lemmas - better than textblob's method
        doc = nlp(r['full_text'])

        clean_text =  ' '.join(' '.join(
                [w.text.lower() for w in doc if w.text.lower() not in STOP_WORDS and \
                 not w.is_punct and not w.is_digit and not w.is_space]).split())
        # need to account for blank values here
        if clean_text == '' or clean_text == None:
            clean_text = ''
        df.at[i,'clean_text'] = clean_text
        df.at[i,'lemmas'] = ' '.join([w.lemma_.lower() for w in doc \
                if not w.is_punct and not w.is_digit and not w.is_space])

        # textdescriptives to get readability score
        df.at[i,'grade_level'] = doc._.readability['automated_readability_index']
        df.at[i,'readability'] = doc._.readability['flesch_reading_ease']

        # sentiment and Objectivity ratings from textblob
        df.at[i,'polarity'] = doc._.blob.polarity
        df.at[i,'subjectivity'] = doc._.blob.subjectivity

        # pos and ner
        df.at[i,'pos_all'] =  [(clean_tok(t.text), t.pos_) for t in doc if t.pos_ not in ['PUNCT','SPACE']]
        df.at[i, 'entities_all'] = [(clean_tok(ent.text), ent.label_) for ent in doc.ents]

        ct += 1

    # update dates
    df['date'] = df['date'].apply(lambda x: parse_date(x))
    df['cleandate'] = df['date'].apply(lambda x: get_cleandate(x))

    _nlp_placeholder.markdown('*Gathering Sentiment analysis*')
    df = get_sa(df)

    _nlp_placeholder.markdown('*Text cleaning and lemmatization complete.*')

    return df

# load default dataset
@st.experimental_memo
def get_data(current_csv, tk_js):

    # set data source and open as dataframe
    df = pd.read_csv(current_csv, na_filter= False, parse_dates=['date'])
    df = df[[c for c in df.columns if 'Unnamed' not in c]]
    df[['source','full_text','label']].applymap(lambda x: x.encode('utf-8').decode('ascii', 'ignore'))

    if tk_js != None:
        with open(tk_js) as f:
            data = json.load(f)
            tokenizer = tokenizer_from_json(data)
        try:
            for c in ['label','full_text','clean_text','lemmas']:
               df[c] = df[c].apply(literal_eval)
               df[c] = df[c].apply(lambda x: tokenizer.sequences_to_texts([x])[0])
        except:
            pass

    if 'init_data' in state and state.init_data == 'ljw':
        sourcenames = {'LJW':'Lawrence Journal-World','UDK':'University Daily Kansan'}
        df.source = df.source.apply(lambda x: sourcenames.get(x) if x in sourcenames else x)

    return df

def default_vals():

    # reset all values to full dataset
    state.df_filtered = state.df
    daterange = get_daterange(state.df)
    state.daterange = daterange
    state.daterange_full = daterange
    state.start_date = daterange[0]
    state.end_date = daterange[-1]
    state.colors = sns.color_palette(None, len(state.df.source.unique()))

# load default data when no data is present
def init_data():

    # # if data already exists, skip the rest
    if 'init' in state and state.init == True:
        return

    # set input data files
    if 'init_data' not in state or state.init_data == 'ljw':
        current_csv = 'data/ljw.csv'
        tk_js = 'data/tokenizer.json'
        state.date_access = 'Month'
    elif state.init_data == 'shak':
        current_csv = 'data/shakespearePlays.csv'
        tk_js = None
        state.date_access = 'Year'

    # placeholder for status updates
    loading = st.empty()
    loading.markdown('***Loading data. Please wait***')

    # configure data range and filter data
    df = get_data(current_csv, tk_js)

    # update dates
    df['date'] = df['date'].apply(lambda x: parse_date(x))
    df['cleandate'] = df['date'].apply(lambda x: get_cleandate(x))

    # leave as placeholder for preprocessing on the fly
    # much quicker to do in advance (~5 min for 3,500 articles)
    # df = getdata.preprocess(df)

    # sentiment analysis - ~ 30 seconds for 3,500 articles
    df = get_sa(df)

    # set other default values for session_state
    state.df = df
    default_vals()

    loading.empty()

    state.init = True
    return


# display sample df
def display_initial_df(df):
    # display truncated dataset
    t_df = df[['uniqueID','date','label','full_text','source']].sort_values(by='date').sample().copy().assign(hack='').set_index('hack')
    for c in['uniqueID','full_text','label']:
        t_df[c] = t_df[c].apply(lambda x: x[:100] + '...')

    st.table(t_df)

# checking pre-processed data to avoid doing twice
def check_user_df():

    cols_to_check = ['label','date','source','full_text','uniqueID','clean_text',
            'lemmas','grade_level','readability','polarity','subjectivity',
            'cleandate','compound','label_compound']
    df = state.user_df
    if all(c in df.columns for c in cols_to_check):
        return True
    else:
        return False

def set_user_data(df, daterange):

    # tell streamlit we are using user data
    state.userdata = True
    state.df = df
    state.df_filtered = df
    state.daterange = daterange
    state.daterange_full = daterange
    state.start_date = daterange[0]
    state.end_date = daterange[-1]
    state.init = True
    state.colors = sns.color_palette(None, len(df.source.unique()))

# display user-uploaded df
def display_user_df(df):

    # display truncated dataset
    t_df = df.sample(3).copy().assign(hack='').set_index('hack')
    for c in t_df.columns:
        try:
            t_df[c] = t_df[c].apply(lambda x: x[:100] + '...' if len(str(x)) > 100 else x)
        except TypeError:
            try:
                t_df[c] = t_df[c].apply(lambda x: x[:5])
            except:
                pass

    return t_df

# allow user upload (csv, excel, json)
def user_upload(uploaded_file):

    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)

        # return df.sample(100)
        return df

    # elif uploaded_file.type == 'application/json':
    #     df = pd.read_json(uploaded_file)
    #     # return df.sample(30)
    #     return df
    else:
        st.markdown(f"You uploaded {uploaded_file.name} -- Please upload in CSV format.")
        return None
