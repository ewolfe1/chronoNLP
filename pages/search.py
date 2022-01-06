import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
from datetime import datetime
from natsort import natsorted
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
import plotly.express as px
import plotly.graph_objs as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
# spacy
import spacy
from nltk import FreqDist

from scripts import saproc
from hydralit import HydraHeadApp

class search(HydraHeadApp):

    def run(self):

        @st.cache
        def load_model():
        	  return spacy.load("en_core_web_sm")

        nlp = load_model()

        # plot a single term across multiple sources
        @st.experimental_memo
        def plot_term_by_source(date_df, searchterm, kwsearch_abs_btn):

            term = [w.lemma_ for w in nlp(searchterm.strip())][0]

            fig = go.Figure()

            for source in date_df.source.unique():

                d_df = date_df[date_df.source==source].groupby('month')
                kwsearch = [' '.join(g.lemmas).split().count(term) for n,g in d_df]
                kwcount = "{:,d}".format(sum(kwsearch))

                num_articles = len(date_df[date_df.source==source])

                # normalize data if requested
                if kwsearch_abs_btn == 'Normalized':
                    kwsearch=([t/num_articles for t in kwsearch])

                fig.add_trace(go.Scatter(x=[n for n,g in d_df], y=kwsearch,
                                name=f'{source} ({kwcount} total uses)', marker_color=(colors[list(date_df.source.unique()).index(source)])
                        ))

            return fig

        # plot multiple terms over time
        @st.experimental_memo
        def plot_terms_by_month(date_df, searchterm_multi):

            fig = go.Figure()

            for term in searchterm_multi.split(','):

                term = [w.lemma_ for w in nlp(term.strip())][0]

                d_df = date_df.groupby('month')
                kwsearch = [' '.join(g.lemmas).split().count(term) for n,g in d_df]
                total_uses = ' '.join(date_df.lemmas).split().count(term)

                # add to graph
                fig.add_trace(go.Scatter(x=[n for n,g in date_df.resample('M')], y=kwsearch,
                                name=f'{term} ({total_uses:,} total uses)', text=kwsearch))

            return fig


        date_df = st.session_state.date_df
        df_filtered = st.session_state.df_filtered
        #tokenizer = st.session_state.tokenizer

        # placeholder for status updates
        placeholder = st.empty()

        # header
        st.subheader('Search for keywords')

        # user-driven search
        placeholder.markdown('*. . . Analyzing search terms . . .*\n\n')
        with st.expander("Search for a single term"):

            st.caption("'Absolute' will show the raw count of occurrences of a single term. 'Normalized' will show the relative proportion of that term within a given source.")

            searchterm_single = st.text_input("Compare a single keyword across all sources", value="covid-19")

            kwsearch_abs_btn = st.radio('', ['Absolute','Normalized'])
            st.plotly_chart(plot_term_by_source(date_df, searchterm_single, kwsearch_abs_btn), use_container_width=True)

            if st.checkbox(f'See the sentiment analysis for articles containing the term "{searchterm_single}"', key='search_sa_btn'):

                search_df = pd.DataFrame([r for i, r in df_filtered.iterrows() if searchterm_single.lower() in r.clean_text + r.lemmas])

                sent_query = 'compound' # see sentiment.py
                sent_topic_plot = saproc.get_topic_plot(search_df, sent_query)
                st.plotly_chart(sent_topic_plot, use_container_width=True)

                sent_boxplot = saproc.get_sent_boxplot(search_df, sent_query)
                st.plotly_chart(sent_boxplot, use_container_width=True)

        with st.expander("Compare multiple terms"):

            searchterm_multi = st.text_input("Compare multiple keywords (separate with a comma)", value="covid-19,vaccine")
            st.write('Charting multiple keywords from all sources')
            st.plotly_chart(plot_terms_by_month(date_df, searchterm_multi),use_container_width=True)

            if st.checkbox('See the sentiment analysis of these results', key='searchmulti_sa_btn'):
                st.plotly_chart(saproc.plot_sa_multiterm(df_filtered, searchterm_multi, 'compound'), use_container_width=True)

                st.plotly_chart(saproc.get_sent_boxplot_multiterm(df_filtered, searchterm_multi, 'compound'), use_container_width=True)

        placeholder.empty()
