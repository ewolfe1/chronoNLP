import streamlit as st
import pandas as pd
import numpy as np
from natsort import natsorted
from datetime import datetime
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])

from multi_rake import Rake

from nltk import FreqDist
from textblob import TextBlob, Word
from hydralit import HydraHeadApp
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

# wordcloud
def get_wc(tf):

    # generate a word cloud image:
    wordcloud = WordCloud(background_color="white", colormap='twilight',width=1200, height=600, collocations=False).fit_words(tf['grouped_text_dict'])

    # Display the generated image:
    wc = plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    month = f'{st.session_state.s_date}-{st.session_state.e_date}' if tf['month'] == '.*' else datetime.strftime(datetime.strptime(tf['month'], "%Y-%m"), "%B %Y")
    source = 'All sources' if tf['source'] == '.*' else tf['source']

    plt.title('{} -- {} ({} articles)'.format(month, source, tf['num']))
    plt.close()
    return wc.figure

# filter df
def filter_df(df, tf):

    class_df = df[(df.month.str.contains(tf['month'])) & (df.source.str.contains(tf['source']))].copy()
    tf['num'] = len(class_df)

    return class_df, tf

# Term frequency
@st.experimental_memo
def get_tf(df, tf):

    class_df, tf = filter_df(df, tf)

    try:
        omit = [o.strip() for o in tf['omit'].split(',')]
    except KeyError:
        omit = []

    tb_to_eval = TextBlob(' '.join(class_df.clean_text))
    grouped_text = FreqDist([' '.join(ng) for ng in tb_to_eval.ngrams(tf['ngram']) if ng not in omit]).most_common(200)
    # get weighted string of common words
    tf['grouped_text_dict'] = {t:f for t,f in grouped_text}

    # get most frequent terms and return table of data for chosen month/source
    common_df = pd.DataFrame(grouped_text[:10], columns=['term','frequency'])
    common_df.set_index('term', inplace=True)

    return common_df, tf

# RAKE keywords
@st.experimental_memo
def get_rake(df, tf):

    class_df, tf = filter_df(df, tf)

    rake = Rake(min_chars=3, max_words=tf['ngram'], min_freq=3)
    rake_df = pd.DataFrame(columns=['term'])

    data_full = ' '.join(class_df.full_text)
    data_clean = ' '.join(class_df.clean_text)

    for keyword, score in (rake.apply(data_full)):
        rake_df = rake_df.append({'term':keyword,
                                  'rake_score':score}, ignore_index=True)

    # # filter df to exclude certain phrases
    if tf['omit'] != '':
        rake_df = rake_df[~rake_df.term.str.contains('|'.join(tf['omit'])).any(level=0)]
    rake_df = rake_df.sort_values('rake_score', ascending=False).head(200)

    for i,r in rake_df.iterrows():
        rake_df.at[i, 'frequency'] = data_clean.count(r.term)

    rake_df['frequency'] = rake_df['frequency'].astype(int)
    tf['grouped_text_dict'] = {r['term']:r['rake_score'] for i,r in rake_df.iterrows()}
    rake_df.set_index('term', inplace=True)

    return rake_df.head(10), tf

# TF-IDF
@st.experimental_memo
def get_tfidf(df, tf):

    class_df, tf = filter_df(df, tf)

    cvec = CountVectorizer(stop_words=None, min_df=3, max_df=50, ngram_range=(tf['ngram'], tf['ngram']))
    sf = cvec.fit_transform([t for t in class_df.clean_text.values])
    data = ' '.join(class_df.clean_text)

    transformer = TfidfTransformer()
    transformed_weights = transformer.fit_transform(sf)
    weights = np.asarray(transformed_weights.mean(axis=0)).ravel().tolist()
    weights_df = pd.DataFrame({'term': cvec.get_feature_names(), 'TF-IDF weight': weights})
    weights_df = weights_df.sort_values(by='TF-IDF weight', ascending=False).head(200)
    for i,r in weights_df.iterrows():
        weights_df.at[i, 'frequency'] = int(data.count(r.term))
    weights_df['frequency'] = weights_df['frequency'].astype(int)
    tf['grouped_text_dict'] = {r['term']:r['TF-IDF weight'] for i,r in weights_df.iterrows() if r['term'] not in tf['omit']}
    weights_df.set_index('term', inplace=True)

    return weights_df.head(10), tf
