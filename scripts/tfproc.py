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

# from multi_rake import Rake

from nltk import FreqDist
from textblob import TextBlob, Word
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

# import subprocess
# import textblob

# @st.cache
# def tb_corpora():
#     cmd = ['python3','-m','textblob.download_corpora']
#     subprocess.run(cmd)
#
# tb_corpora()

# wordcloud
def get_wc(tf):

    # generate a word cloud image:
    wordcloud = WordCloud(background_color="white", colormap='twilight',width=1200, height=600, collocations=False).fit_words(tf['grouped_text_dict'])

    # Display the generated image:
    wc = plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    month = f'{st.session_state.start_date}-{st.session_state.end_date}' if tf['date'] == '.*' else datetime.strftime(datetime.strptime(tf['date'], "%Y-%m"), "%B %Y")
    source = 'All sources' if tf['source'] == '.*' else tf['source']

    #plt.title('{} -- {} ({} articles)'.format(month, source, tf['num']))
    plt.close()
    return wc.figure

def results_title(tf):

    ms = datetime.strftime(datetime.strptime(tf["date_start"],'%Y-%m'),'%B %Y')
    me = datetime.strftime(datetime.strptime(tf["date_end"],'%Y-%m'),'%B %Y')

    kwd_label = {'Terms':'Most frequent terms',
                'TF-IDF':'TF-IDF results',
                'Keywords':'RAKE keywords'}

    dates = f"{ms} to {me}" if ms != me else ms
    title = f"{kwd_label.get(tf['kwd'])} from {dates} --- {'/'.join(tf['source'])} ({tf['num']} articles)"

    return title

# filter df
def filter_df(df, tf):

    df_filtered = df
    class_df = df[((df['cleandate'] >= tf['date_start']) & (df['cleandate'] <= tf['date_end'])) & (df.source.str.contains('|'.join(tf['source'])))].copy()
    tf['num'] = len(class_df)

    try:
        omit = [o.strip() for o in tf['omit'].split(',')]
    except KeyError:
        omit = []

    return class_df, tf, omit

# Term frequency
@st.experimental_memo
def get_tf(df, tf):

    class_df, tf, omit = filter_df(df, tf)

    tb_to_eval = TextBlob(' '.join(class_df.clean_text))
    grouped_text = FreqDist([' '.join(ng) for ng in tb_to_eval.ngrams(tf['ngram'])]).most_common(200)
    grouped_text = [g for g in grouped_text if g[0] not in omit]
    # get weighted string of common words
    tf['grouped_text_dict'] = {t:f for t,f in grouped_text}

    # get most frequent terms and return table of data for chosen month/source
    common_df = pd.DataFrame(grouped_text[:10], columns=['term','frequency'])
    common_df.set_index('term', inplace=True)

    return common_df, tf

# RAKE keywords
@st.experimental_memo
def get_rake(df, tf):

    class_df, tf, omit = filter_df(df, tf)

    rake = Rake(min_chars=3, max_words=tf['ngram'], min_freq=3)
    rake_df = pd.DataFrame(columns=['term'])

    data_full = ' '.join(class_df.full_text)
    data_clean = ' '.join(class_df.clean_text)

    for keyword, score in (rake.apply(data_full)):
        # rake_df = rake_df.append({'term':keyword,
        #                           'rake_score':score}, ignore_index=True)
        rake_df = pd.concat([rake_df, pd.DataFrame([{'term':keyword,
                                                'rake_score':score}])])

    # # filter df to exclude certain phrases
    rake_df = rake_df.sort_values('rake_score', ascending=False).head(200)
    rake_df = rake_df[~rake_df['term'].isin(omit)]

    for i,r in rake_df.iterrows():
        rake_df.at[i, 'frequency'] = data_clean.count(r.term)

    rake_df['frequency'] = rake_df['frequency'].astype(int)
    tf['grouped_text_dict'] = {r['term']:r['rake_score'] for i,r in rake_df.iterrows()}
    rake_df.set_index('term', inplace=True)

    return rake_df.head(10), tf

# TF-IDF
@st.experimental_memo
def get_tfidf(df, tf):

    class_df, tf, omit = filter_df(df, tf)

    cvec = CountVectorizer(stop_words=None, min_df=3, max_df=50, ngram_range=(tf['ngram'], tf['ngram']))
    sf = cvec.fit_transform([t for t in class_df.clean_text.values])
    data = ' '.join(class_df.clean_text)

    transformer = TfidfTransformer()
    transformed_weights = transformer.fit_transform(sf)
    weights = np.asarray(transformed_weights.mean(axis=0)).ravel().tolist()
    weights_df = pd.DataFrame({'term': cvec.get_feature_names(), 'TF-IDF weight': weights})
    weights_df = weights_df[~weights_df['term'].isin(omit)]
    weights_df = weights_df.sort_values(by='TF-IDF weight', ascending=False).head(200)

    for i,r in weights_df.iterrows():
        weights_df.at[i, 'frequency'] = int(data.count(r.term))
    weights_df['frequency'] = weights_df['frequency'].astype(int)
    tf['grouped_text_dict'] = {r['term']:r['TF-IDF weight'] for i,r in weights_df.iterrows()}
    weights_df.set_index('term', inplace=True)

    return weights_df.head(10), tf
