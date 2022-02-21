import pandas as pd
import numpy as np
from natsort import natsorted
from datetime import datetime
import streamlit as st
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
import textdescriptives as td
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

import json
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
from ast import literal_eval

@st.experimental_memo
def load_model():
    nlp = spacy.load("en_core_web_sm")
    nlp.Defaults.stop_words |= {'the','we','she','he','said','it','like'}
    nlp.add_pipe('textdescriptives')

    return nlp

@st.experimental_memo
def get_date_df(df):
    # copy df and use date as datetime and index
    date_df = df.copy()
    date_df['date'] = pd.to_datetime(date_df['date'])
    date_df = date_df.set_index('date')
    return date_df

@st.experimental_memo
def get_daterange(df):
    # get a list of dates represented in the data
    df['cleandate'] = df['date'].apply(lambda x: x[:7] if len(x) >= 7 else x[:4])
    daterange = [d for d in natsorted(df['cleandate'].unique().tolist()) if d not in ['',None]]

    return df, daterange

@st.experimental_memo(suppress_st_warning=True)
def preprocess(df, _nlp_placeholder):

    nlp = load_model()

    # placeholder columns
    for c in ['clean_text','lemmas','grade_level','readability']:
        if c not in df.columns:
            df[c] = None

    # processing count
    ct = 1
    _nlp_placeholder = st.empty()

    for i,r in df.iterrows():

        _nlp_placeholder.markdown(f'Processing item {ct} of {len(df)}')

        # call spaCy for cleanup and lemmas - better than textblob's method
        doc = nlp(r['full_text'])

        df.at[i,'clean_text'] =  ' '.join(' '.join(
                [w.text.lower() for w in doc if w.text.lower() not in STOP_WORDS and
                 not w.is_punct and not w.is_digit and not w.is_space]).split())

        df.at[i,'clean_text'] =  ' '.join(' '.join(
                [w.text.lower() for w in doc if w.text.lower() not in STOP_WORDS and \
                 not w.is_punct and not w.is_digit and not w.is_space]).split())
        df.at[i,'lemmas'] = ' '.join([w.lemma_.lower() for w in doc \
                if not w.is_punct and not w.is_digit and not w.is_space])

        # textdescriptives to get readability score
        df.at[i,'grade_level'] = doc._.readability['automated_readability_index']
        df.at[i,'readability'] = doc._.readability['flesch_reading_ease']

        ct += 1

    _nlp_placeholder.markdown('*Text cleaning and lemmatization complete*')

    return df

@st.experimental_memo
def get_sa(df):

    # compound is average; other measures are neg, neu, pos
    df['compound'] = df['full_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    df['title_compound'] = df['title'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

    return df

@st.experimental_memo
def get_data(current_csv, tk_js):

    with open(tk_js) as f:
        data = json.load(f)
        tokenizer = tokenizer_from_json(data)

    # set data source and open as dataframe
    df = pd.read_csv(current_csv, na_filter= False)

    try:
        for c in ['title','full_text','clean_text','lemmas']:
           df[c] = df[c].apply(literal_eval)
           df[c] = df[c].apply(lambda x: tokenizer.sequences_to_texts([x])[0])
    except:
        pass

    sourcenames = {'LJW':'Lawrence Journal-World','UDK':'University Daily Kansan'}
    df.source = df.source.apply(lambda x: sourcenames.get(x) if x in sourcenames else x)

    return df

def get_case_data(case_csv):

    # 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'
    cv_data = pd.read_csv(case_csv)
    cv_data['month'] = cv_data['date'].apply(lambda x: x[:7])
    cv_data  = cv_data[(cv_data['month'] >= st.session_state.start_date) & (cv_data['month'] <= st.session_state.end_date)]

    new = cv_data['cases'].iloc[0]

    for i,r in cv_data.iterrows():
        cv_data.at[i, 'newcases'] = r.cases - new
        new = r.cases

    cv_data['date'] = pd.to_datetime(cv_data['date'])
    cv_data = cv_data.set_index('date')
    cv_data = cv_data.resample('M')

    return cv_data

def display_df(df):
    # display truncated dataset
    t_df = df[['url','date','title','full_text','source']].sort_values(by='date').sample(5).copy().assign(hack='').set_index('hack')
    for c in['url','full_text','title']:
        t_df[c] = t_df[c].apply(lambda x: x[:100] + '...')

    st.table(t_df)

def user_upload(uploaded_file):

    if uploaded_file.name.split('.')[-1] == 'csv':
        df = pd.read_csv(uploaded_file)
        df = df[~df.full_text.isnull()]
        return df.sample(300)
    elif uploaded_file.name.split('.')[-1] in ['xls','xlsx']:
        df = df[~df.full_text.isnull()]
        df = pd.read_excel(uploaded_file)
        return df
    else:
        st.markdown(f"You uploaded {uploaded_file.name}")
        st.markdown("Please upload in CSV, XLS, or XLSX format")
        return None
