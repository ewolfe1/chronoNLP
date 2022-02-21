import streamlit as st
from streamlit import components
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import colorlover as cl
colors = cl.to_rgb(cl.scales['7']['qual']['Set2'])
import gensim
import gensim.corpora as corpora
from gensim.models import CoherenceModel
from hydralit import HydraHeadApp

class topics(HydraHeadApp):
# def app():

    def run(self):

        @st.experimental_memo
        def get_ta_models(data):
            # Build the bigram model
            bigram = gensim.models.Phrases(data, min_count=3, threshold=60) # higher threshold fewer phrases.
            bigram_mod = gensim.models.phrases.Phraser(bigram)

            def make_bigrams(texts):
                return [bigram_mod[doc] for doc in texts]

            data_bigrams = make_bigrams([bigram_mod[doc] for doc in data])
            # Create Dictionary
            id2word = corpora.Dictionary(data_bigrams)
            # Create Corpus
            texts = data_bigrams
            # Term Document Frequency
            corpus = [id2word.doc2bow(text) for text in texts]
            return data_bigrams, id2word, corpus

        def get_lda_model(id2word, corpus, num_topics):
            lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus,id2word=id2word,
                    num_topics=num_topics, random_state=100, update_every=1,
                    chunksize=200, passes=2, alpha='auto', per_word_topics=True)

            return lda_model

        #@st.experimental_memo
        def get_topic_df(df_filtered, _lda_model, corpus):
            # make df of top topics
            topic_df = pd.DataFrame()

            for i,r in df_filtered.iterrows():

                tops = _lda_model.get_document_topics(corpus[i])
                td = {t[0]:t[1] for t in tops}

                td['top_topic'] = [str(k) for k,v in td.items() if v == max([v for k,v in td.items()])][0]
                td['docid'] = str(i)
                td['date'] = r['date']
                topic_df = topic_df.append(td, ignore_index=True)

            return topic_df

        def get_wc(lda_model, i):
            weighted = {kwd[0]:kwd[1] for kwd in lda_model.show_topic(i, topn=100)}
            wordcloud = WordCloud(background_color="white", colormap='twilight').generate_from_frequencies(weighted)

            wc = plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            plt.close()
            return wc.figure

        # distribution of topics over time
        def topics_by_month(lda_model, topic_df, ta_abs_btn):

            # build plot
            fig = go.Figure()
            t_df = pd.DataFrame()

            for n,g in topic_df.groupby(topic_df.date.str[:7]):
                data = {'month':n}
                if ta_abs_btn == 'Absolute':
                    for c in g[[c for c in g.columns if str(c).isdigit()]]:
                        data[c] = g[c].agg(sum)
                        sizemin=3
                else:
                    for c in g[[c for c in g.columns if str(c).isdigit()]]:
                        data[c] = g[c].agg(sum) / len(g)
                        sizemin=6
                t_df = t_df.append(data, ignore_index=True)
            t_df = t_df.sort_values('month')

            for topic_num in t_df[[c for c in t_df.columns if str(c).isdigit()]]:
                kwds = ', '.join([lda_model.id2word[t[0]] for t in lda_model.get_topic_terms(topic_num)])
                fig.add_trace(go.Scatter(x=t_df.month.tolist(), y=t_df[topic_num],
                        mode='markers',marker=dict(
                                         size=t_df[topic_num],
                                         sizemin=sizemin),
                                         name=f'Topic {topic_num + 1} - {kwds}'))
                fig.update_layout(legend=dict(yanchor="top", y=-0.1, xanchor="left", x=0, itemsizing='constant'))
                fig.update_layout(height=700)

            return fig

        def plot_coherence(coherence_df):

            coherence_df['Number of topics'] = coherence_df['Number of topics'].astype(int)
            coherence_df.set_index('Number of topics', inplace=True)

            fig = make_subplots(specs=[[{"secondary_y": True}]], x_title='Number of topics')

            fig.add_trace(go.Scatter(x=coherence_df.index, y=coherence_df['Coherence'],
                                    mode='lines'))
            fig.update_yaxes(title_text="Coherence", secondary_y=False, showgrid=False)

            fig.add_trace(go.Scatter(x=coherence_df.index, y=coherence_df['Perplexity'],
                                    mode='lines'), secondary_y=True)
            fig.update_yaxes(title_text="Perplexity", secondary_y=True, showgrid=False)

            return fig

        date_df = st.session_state.date_df
        df_filtered = st.session_state.df_filtered

        # get source data
        data = [t.split() for t in df_filtered.clean_text.values.tolist()]

        # placeholder for status updates
        topic_placeholder = st.empty()
        placeholder = st.empty()

        # header
        st.subheader('Topic modeling')

        placeholder.markdown('*. . . Initializing . . .*\n\n')

        placeholder.markdown('*. . . Compiling data (step 1 of 4) . . .*\n')
        data_bigrams, id2word, corpus = get_ta_models(data)

        placeholder.markdown('*. . . Building topic models for dataset  (step 2 of 4) . . .*\n')

        if 'num_topics' not in st.session_state:
            st.session_state.num_topics = 12
        lda_model = get_lda_model(id2word, corpus, st.session_state.num_topics)
        placeholder.markdown('*. . . Assigning articles to topics  (step 3 of 4) . . .*\n')
        topic_df = get_topic_df(df_filtered, lda_model, corpus)

        # plot topic frequency over time
        placeholder.markdown('*. . . Visualizing data (step 4 of 4) . . .*\n')

        st.caption('Click an item in the legend to exclude from the results. Double click to isolate that item.')
        st.caption("'Absolute' will show the raw count of articles on that topic. 'Normalized' will show the relative proportion of that topic for a given month (scale is 0 to 1.0)")

        ta_abs_btn = st.radio('', ['Absolute','Normalized'])

        st.plotly_chart(topics_by_month(lda_model, topic_df, ta_abs_btn),use_container_width=True, height=400)

        # perform topic modeling and convert to df
        with st.expander("Review topics"):

            for i in range(0,lda_model.num_topics):
                num_top = len(topic_df[topic_df.top_topic==str(i)])
                try:
                    num_all = topic_df[i].count()
                except:
                    num_all = 0

                sa_cols = st.columns([2,2,3])

                with sa_cols[0]:

                    st.markdown(f'## Topic {i+1}')
                    st.markdown(f'**Statistically present in** {num_all:,} articles')
                    st.markdown(f'**Primary topic in** {num_top:,} articles')

                with sa_cols[1]:
                    st.markdown(f'**Top keywords**')
                    st.markdown(f"{', '.join([lda_model.id2word[t[0]] for t in lda_model.get_topic_terms(i)])}")

                try:

                    # working code to add top five articles by topic
                    # sa_cols[0].markdown(f"**Top articles for this topic**  ({topic_df[i].count()} articles total)")
                    # topic_art = ""
                    # for idx,r in topic_df.sort_values(by=[i], ascending=False)[:5].iterrows():
                    #     topic_art = topic_art + f"""* [{tokenizer.sequences_to_texts([df_filtered.iloc[idx]['title']])[0]}]({df_filtered.iloc[idx]['url']})  ({df_filtered.iloc[idx]['source']}, {r.date})\n"""
                    #sa_cols[0].markdown(topic_art)

                    wc = get_wc(lda_model, i)
                except:
                    st.markdown(f'Topic {i+1} has no statistically significant results to display')

                sa_cols[2].pyplot(wc)

        placeholder.empty()

        # evaluate topics
        with st.expander('Change number of topics'):

            st.markdown('Select a number of topics here. If you want to evaluate a number of topics, please note that it will take several minutes.')

            nt_cols = st.columns([1,3])
            with nt_cols[0]:
                st.session_state.num_topics = int(st.selectbox('Number of topics to generate', range(5,16)))

            topic_btn = st.button(label='Explore number of topics')
            if topic_btn:

                coherence_df = pd.DataFrame()
                ct = 1

                for num_topics in range(5,16):

                    topic_placeholder.markdown(f'. . . *Evaluating coherence of {num_topics} topics ({ct} of 11)* . . .')
                    ct += 1
                    lda_model_results = get_lda_model(id2word, corpus, num_topics)

                    # Compute Perplexity - a measure of how good the model is. lower the better.
                    perplexity = lda_model_results.log_perplexity(corpus)
                    # Compute Coherence Score - Higher the topic coherence, the topic is more human interpretable
                    coherence_model_lda = CoherenceModel(model=lda_model_results, texts=data_bigrams, dictionary=id2word, coherence='c_v')
                    coherence_lda = coherence_model_lda.get_coherence()
                    coherence_df = coherence_df.append({'Number of topics':num_topics, 'Perplexity':perplexity, 'Coherence':coherence_lda}, ignore_index=True)
                    #st.markdown('{} topics - {} (lower is better) / {} (higher is better)'.format(num_topics, perplexity, coherence_lda))


                coh_cols = st.columns([3,1])
                with coh_cols[0]:
                    st.plotly_chart(plot_coherence(coherence_df))
                with coh_cols[1]:
                    st.dataframe(coherence_df)


        topic_placeholder.empty()
