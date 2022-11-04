import streamlit as st
state = st.session_state
from natsort import natsorted
from scripts import tools, getdata, kwsearchproc
tools.page_config()

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

with kw_cols[1]:
    with st.expander('Tips on keyword searching'):
        kwsearchproc.searchtips()

# combined counts
stlist = []
if searchterm != '':
    searchterm = [t.strip().lower() for t in searchterm.split(',')]
    st.write("***Search terms included in results:***")
    for t in searchterm:
        if '*' in t:
            matchdict = kwsearchproc.get_pattern(f'^{t}', ' '.join(df.clean_text), omit)
        else:
            matchdict = kwsearchproc.get_pattern(t, ' '.join(df.clean_text), omit)
        # matchstr = ', '.join(natsorted([f'{k} ({v:,})' for k,v in matchdict.items()]))
        matchstr = ', '.join(natsorted([k for k,v in matchdict.items() if kwsearchproc.kwd_count(k, ' '.join(df.clean_text), omit) > 0]))

        st.write(f"**{t.strip()}** -- {matchstr}")

        if t.startswith('^'):
            stlist.extend(natsorted([k for k,v in matchdict.items() if k in matchstr]))
        else:
            stlist.extend([t])

    st.write('### Keyword frequency')

    kw_abs, kw_norm, kw_df = kwsearchproc.plot_terms_by_month(df, stlist, omit)
    kw_tab1, kw_tab2, kw_tab3 = st.tabs(["Raw count (graph)", "Normalized (graph)", "Table"])

    with kw_tab1:
        st.write('Raw count of keyword frequency over time (all sources)')
        st.plotly_chart(kw_abs, use_container_width=True)

    with kw_tab2:
        st.write('Keyword frequency over time, normalized relative to the publication frequency (scale of 0 to 1) (all sources)')
        st.plotly_chart(kw_norm, use_container_width=True)

    with kw_tab3:
        st.write('Raw and normalized (scale of 0 to 1) frequency counts for each term.')
        st.table(kw_df)

        # fn = '_'.join([t.lower().strip() for t in searchterm.split(',')])
        # st.download_button(label="Download data as CSV", data=kw_df.to_csv().encode('utf-8'),
        #      file_name=f'keywords-{fn}.csv', mime='text/csv')

    # counts by source
    if len(df.source.unique()) > 1:

        with st.expander('View plots by individual sources'):

            # plot all terms
            kwsearchproc.get_tabs(df, stlist, omit)
            if len(stlist) > 1:

                # plot individual terms
                for term in stlist:
                    kwsearchproc.get_tabs(df, term, omit)

placeholder.empty()
