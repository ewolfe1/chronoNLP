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
    nlp.add_pipe('textdescriptives')
    nlp.Defaults.stop_words |= {'the','we','she','he','said','it','like'}

nlp = load_model()


@st.experimental_memo
def get_date_df(df):
    # copy df and use date as datetime and index
    date_df = df.copy()
    date_df['date'] = pd.to_datetime(date_df['date'])
    date_df = date_df.set_index('date')
    return date_df

@st.experimental_memo
def get_months(df):
    # get a list of months represented in the data
    df['month'] = df['date'].apply(lambda x: x[:7])
    months = [d for d in natsorted(df['month'].unique().tolist()) if d not in ['',None]]
    return df, months

@st.experimental_memo
def preprocess(df):

    for i,r in df.iterrows():

        # call spaCy for cleanup and lemmas - better than textblob's method
        doc = nlp(r['full_text'])

        df.at[i,'clean_text'] =  ' '.join(' '.join(
                [w.text.lower() for w in doc if w.text not in STOP_WORDS and not w.is_punct]).split())
        df.at[i,'lemmas'] = ' '.join([w.lemma_.lower() for w in doc])

        # textdescriptives to get readability score
        df.at[i,'grade_level'] = doc._.readability['automated_readability_index']
        df.at[i,'readability'] = doc._.readability['flesch_reading_ease']

    return df

@st.experimental_memo
def get_sa(df, _placeholder):

    # compound is average; other measures are neg, neu, pos
    _placeholder.markdown('*. . . Pre-processing data (Step 1 of 2). . .*\n\n')
    df['compound'] = df['full_text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])
    _placeholder.markdown('*. . . Pre-processing data (Step 2 of 2). . .*\n\n')
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
