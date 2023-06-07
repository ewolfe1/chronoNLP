import streamlit as st
state = st.session_state
import pandas as pd
import numpy as np
from natsort import natsorted
from datetime import datetime
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# from multi_rake import Rake
from rake_nltk import Rake

from nltk import FreqDist
from textblob import TextBlob, Word
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from scripts import tools, getdata

# wordcloud
def get_wc(tf):

    # generate a word cloud image:
    wordcloud = WordCloud(background_color="white", colormap='twilight',width=1200, height=600, collocations=False).fit_words(tf['grouped_text_dict'])

    # Display the generated image:
    wc = plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")

    plt.close()
    return wc.figure

def results_title(tf):

    # ms = datetime.strftime(datetime.strptime(tf["date_start"],'%Y-%m'),'%B %Y')
    # me = datetime.strftime(datetime.strptime(tf["date_end"],'%Y-%m'),'%B %Y')
    ms = getdata.format_dates(tf["date_start"])
    me = getdata.format_dates(tf["date_end"])

    kwd_label = {'Terms':'Most frequent terms',
                'TF-IDF':'TF-IDF results',
                'Keywords':'RAKE keywords'}

    dates = f"{ms} to {me}" if ms != me else ms
    source = '/'.join(tf['source'])

    if source == '' or source is  None:
        source = 'All sources in range'
    title = f"""**{kwd_label.get(tf['kwd'])}**\n
Date(s): {dates}\n
Source(s): {source}\n
Number of items: {tf['num']:,}"""

    return title

# filter df
def filter_df(df, tf):

    class_df = df[((df['cleandate'] >= tf['date_start']) & (df['cleandate'] <= tf['date_end'])) & (df.source.str.contains('|'.join(tf['source'])))].copy()
    tf['num'] = len(class_df)

    try:
        omit = [o.strip() for o in tf['omit'].split(',')]
    except KeyError:
        omit = []

    return class_df, tf, omit

# Term frequency
@st.cache_data
def get_tf(df, tf):

    class_df, tf, omit = filter_df(df, tf)

    tb_to_eval = TextBlob(' '.join(class_df[~class_df.clean_text.isnull()].clean_text))
    grouped_text = FreqDist([' '.join(ng) for ng in tb_to_eval.ngrams(tf['ngram'])]).most_common(200)
    grouped_text = [g for g in grouped_text if g[0] not in omit]
    # get weighted string of common words
    tf['grouped_text_dict'] = {t:f for t,f in grouped_text}

    # get most frequent terms and return table of data for chosen month/source
    common_df = pd.DataFrame(grouped_text[:10], columns=['term','frequency'])
    common_df.set_index('term', inplace=True)

    return common_df, tf

# RAKE keywords
@st.cache_data
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
@st.cache_data
def get_tfidf(df, tf):

    class_df, tf, omit = filter_df(df, tf)

    #
    cvec = CountVectorizer(stop_words='english', min_df=1, max_df=0.5, ngram_range=(tf['ngram'], tf['ngram']))
    sf = cvec.fit_transform([t for t in class_df[~class_df.clean_text.isnull()].clean_text.values])
    data = ' '.join(class_df[~class_df.clean_text.isnull()].clean_text)

    transformer = TfidfTransformer()
    transformed_weights = transformer.fit_transform(sf)
    weights = np.asarray(transformed_weights.mean(axis=0)).ravel().tolist()
    weights_df = pd.DataFrame({'term': cvec.get_feature_names_out(), 'TF-IDF weight': weights})
    weights_df = weights_df[~weights_df['term'].isin(omit)]
    weights_df = weights_df.sort_values(by='TF-IDF weight', ascending=False).head(200)

    for i,r in weights_df.iterrows():
        weights_df.at[i, 'frequency'] = int(data.count(r.term))
    weights_df['frequency'] = weights_df['frequency'].astype(int)
    tf['grouped_text_dict'] = {r['term']:r['TF-IDF weight'] for i,r in weights_df.iterrows()}
    weights_df.set_index('term', inplace=True)

    return weights_df.head(10), tf

def tf_form(tf):

    n = int(tf['name'][-1])
    # form to allow user input
    with st.form(key=f'tf{n}_form'):

        tf['kwd'] = st.selectbox('Term frequency vs. TF-IDF rankings',['Terms','TF-IDF'], key=f'tf{n}kwd', index=0)
        # Note: have omitted 'Keywords' from the above list due to excessive processing times

        daterange = state.daterange
        df = state.df_filtered

        tf['date_start'] = st.selectbox('Start date', daterange, index=0)
        tf['date_end'] = st.selectbox('End date', daterange, index=len(daterange)-1)

        sources = list(df.source.unique())
        tf['source'] =  st.multiselect('Source(s) (leave blank to select all)',
            sources,key=f'tfs{n}',default=None)

        # tf['source'] = st.multiselect('Source(s)',sources,key=f'tfs{n}',default=sources[1])
        tf['ngram'] = st.selectbox('Ngrams',[1,2,3],key=f'tfng{n}', index=n-1)
        tf['omit'] = st.text_input('Terms to omit from the results (separated by a comma)',key=f'tfmin{n}')

        tf_submit_button = st.form_submit_button(label='Update search')

        return tf, tf_submit_button

# plot most frequent by month
def plot_tf_month(t_df, tf, df):

    class_df, tf, omit = filter_df(df, tf)

    fig = go.Figure()

    d_df = class_df[~(class_df.clean_text.isnull()) & ~(class_df.lemmas.isnull())].groupby('cleandate')
    timeframe = [g.iloc[0].cleandate for n,g in d_df]
    kw_df = pd.DataFrame({'date':timeframe})

    topterms = [i for i,r in t_df[:5].iterrows() if i not in omit]
    for term in topterms:

        total_uses = ' '.join(['' if isinstance(x, float) else x for x in class_df.clean_text]).count(term)
        kwsearch = [' '.join(g.clean_text).count(term) for n,g in d_df]

        # add to graph
        fig.add_trace(go.Scatter(x=timeframe, y=kwsearch,
                        name=f'{term} ({total_uses:,} total uses)', text=kwsearch,
                        line_shape='spline'))

    return fig

def tf_results(tf):

    df = state.df_filtered

    try:
        if tf['kwd'] == 'Terms':
            t_df, tf = get_tf(df, tf)
        elif tf['kwd'] == 'TF-IDF':
            t_df, tf = get_tfidf(df, tf)
        elif tf1['kwd'] == 'Keywords':
            t_df, tf = get_rake(df, tf)

        st.markdown(results_title(tf))
        tfres_tabs1, tfres_tabs2, tfres_tabs3 = st.tabs(('Word cloud','Table view','Time chart'))

        with tfres_tabs1:

            st.write('*Top 200 terms, weighted by frequency*')
            # wordcloud
            wc = get_wc(tf)
            st.pyplot(wc)

        with tfres_tabs2:

            st.write('*Top ten terms and frequency count*')
            # table
            st.table(t_df)

        with tfres_tabs3:

            st.write('*Top five terms plotted over time*')
            # graph
            st.plotly_chart(plot_tf_month(t_df, tf, df), use_container_width=True)

    except ValueError as ve:
        st.write('There are no results from this search')
        st.write(ve)
