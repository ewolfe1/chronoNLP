import streamlit as st
state = st.session_state
from natsort import natsorted
import re
import os
from scripts import tools, getdata, kwsearchproc
tools.page_config()

def local_css(file_name):
    with open(os.path.abspath(file_name)) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")
# /Users/e996w533/Documents/ta-project/streamlit/style.css

# load data
if 'init' not in state:
    getdata.init_data()

df = state.df_filtered

# placeholder for status updates
placeholder = st.empty()

# header
st.subheader('Search for keywords')
getdata.df_summary_header()

# keyword search
# placeholder.markdown('*. . . Analyzing search terms . . .*\n\n')

st.write('View the frequency of one or more keywords over time.')

kw_cols = st.columns(2)
with kw_cols[0]:
    searchterm = st.text_input("Enter keyword(s), separated by a comma", value='test')
    omit = st.text_input("Words to omit from the results, separated by a comma (no quotes)")

    if omit != '':
        omit_set = set(omit.lower().strip() for omit in omit.split(','))
    else:
        omit_set = set()

with kw_cols[1]:
    with st.expander('Tips on keyword searching'):
        kwsearchproc.searchtips()

kwd_process = st.empty()
kwd_process.info('*. . . Evaluating relevant search terms . . .*')

# combined counts
stlist = []
if searchterm != '':
    searchterm = [t.strip().lower() for t in searchterm.split(',')]
    text_to_match = ' '.join(df.full_text.str.lower())
    with st.expander('Search terms included in results'):
        st.write("""*These are the individual terms that match the above search string.\
        Note that only the first ten will be charted due to resource considerations. \
        To see details for additional terms, perform separate searches.*""")

        stlist_cols = st.columns((1,8))

        with stlist_cols[1]:

            for n,t in enumerate(searchterm):
                kwd_process.info(f'*. . . Evaluating relevant search terms . . . ({n+1} of {len(searchterm)})*')
                if '*' in t:
                    matchdict = kwsearchproc.get_pattern(f'^{t}', text_to_match, omit)
                else:
                    matchdict = kwsearchproc.get_pattern(t, text_to_match, omit)

                matchstr = ', '.join(natsorted(list(set([f"{kwsearchproc.strip_punct(k)} ({kwsearchproc.get_ct(df, k, omit):,})" for k,v in matchdict.items() \
                                    if kwsearchproc.get_ct(df, k, omit) > 0]))))

                st.write(f"**{t.strip()}** -- {matchstr}")

                if t.startswith('^'):
                    stlist.extend(natsorted([k for k,v in matchdict.items() if k in matchstr]))
                else:
                    stlist.extend([t])

                stlist = [t for t in stlist if t not in omit]

    # Limit to first ten results. Can hang up if there are too many results to graph
    stlist = stlist[:10]

    kwd_process.info('*. . . Visualizing search results . . .*')

    kw_abs, kw_norm, kw_df = kwsearchproc.plot_terms_by_month(df, stlist, omit)

    tablist = ['All terms'] + stlist if len(stlist) > 1 else stlist
    kw_terms_tabs = st.tabs(tablist)

    # with kw_terms_tabs[0]:
    for t in zip(kw_terms_tabs,tablist):

        if t[1] == 'All terms':
            term = stlist
        else:
            term = [t[1]]
        with t[0]:
            # st.write('### Keyword frequency')

            kw_abs, kw_norm, kw_df = kwsearchproc.plot_terms_by_month(df, term, omit)
            kw_tablist = ["Raw count", "Normalized",
                        "Data", "Keyword in context"]
            if len(df.source.unique()) > 1:
                kw_src_abs_t, kw_src_norm_t, kw_src_df = kwsearchproc.plot_term_by_source(df, term, omit)
                kw_tablist = kw_tablist + ['Raw count by source','Normalized by source','Data by source']
                kt1,kt2,kt3,kt4,kt5,kt6,kt7 = st.tabs(kw_tablist)

                with kt5:
                    st.write('Raw count of keyword frequency over time')
                    st.plotly_chart(kw_src_abs_t, use_container_width=True)
                with kt6:
                    st.write('Keyword frequency over time, normalized relative to the publication frequency (scale of 0 to 1).')
                    st.plotly_chart(kw_src_norm_t, use_container_width=True)
                with kt7:
                    st.write(kw_src_df)

            else:
                kt1,kt2,kt3,kt4 = st.tabs(kw_tablist)

            with kt1:
                st.write('Raw count of keyword frequency over time')
                st.plotly_chart(kw_abs, use_container_width=True)

            with kt2:
                st.write('Keyword frequency over time, normalized relative to the publication frequency (scale of 0 to 1)')
                st.plotly_chart(kw_norm, use_container_width=True)

            with kt3:
                st.write('Raw (R) and Normalized (N) (scale of 0 to 1) frequency counts for each term.')
                st.table(kw_df)

                # fn = '_'.join([t.lower().strip() for t in searchterm.split(',')])
                # st.download_button(label="Download data as CSV", data=kw_df.to_csv().encode('utf-8'),
                #      file_name=f'keywords-{fn}.csv', mime='text/csv')

            with kt4:
                st.write('### Keyword in context')
                kwic_df = kwsearchproc.kwic(df, term)
                st.dataframe(kwic_df)

                st.write('**View most common words occurring nearby the selected keyword(s)**')
                kwd_tf_cols = st.columns((1,2,2,2))
                left_df, right_df, all_df = kwsearchproc.cooccurence(kwic_df)
                with kwd_tf_cols[1]:
                    st.write('Left and Right of the keyword')
                    st.write(all_df)
                with kwd_tf_cols[2]:
                    st.write('Left only')
                    st.write(left_df)
                with kwd_tf_cols[3]:
                    st.write('Right only')
                    st.write(right_df)




    # for tab in kw_terms_tabs[1:]:
    #     with tab:
    #         st.write('test')



    #
    #     # counts by source
    #     indivsrc = st.empty()
    #     if len(df.source.unique()) > 1:
    #
    #         # with st.expander('View plots by individual sources'):
    #         if st.button('View plots by individual sources'):
    #
    #             with indivsrc.container():
    #
    #                 # plot all terms
    #                 kwsearchproc.get_tabs(df, stlist, omit)
    #                 if len(stlist) > 1:
    #
    #                     # plot individual terms
    #                     for term in stlist:
    #                         kwsearchproc.get_tabs(df, term, omit)
    #
    # with kwd_tab2:
    #
    #     for term in stlist:
    #         st.write(f'#### {term}')
    #         # st.write(kwsearchproc.kwic(df, term), unsafe_allow_html=True)
    #         kwic_df = kwsearchproc.kwic(df, term)
    #         #st.write(kwic_df)
    #         # st.write(kwsearchproc.kwic(df, term).to_markdown(None), use_container_width=True)
    #
    #         st.write('**View most common words occurring nearby the selected keyword(s)**')
    #         kwd_tf_cols = st.columns((1,2,2,2))
    #         left_df, right_df, all_df = kwsearchproc.cooccurence(kwic_df)
    #         with kwd_tf_cols[1]:
    #             st.write('Left and Right of the keyword')
    #             st.write(all_df)
    #         with kwd_tf_cols[2]:
    #             st.write('Left only')
    #             st.write(left_df)
    #         with kwd_tf_cols[3]:
    #             st.write('Right only')
    #             st.write(right_df)


kwd_process.empty()
placeholder.empty()
