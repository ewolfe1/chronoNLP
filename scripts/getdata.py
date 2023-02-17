import pandas as pd
import numpy as np
import zipfile
from natsort import natsorted
from datetime import datetime
from dateutil.parser import parse
import streamlit as st
state = st.session_state
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacytextblob.spacytextblob import SpacyTextBlob
import seaborn as sns
import time
import textdescriptives as td
import json
from tensorflow.keras.preprocessing.text import Tokenizer, tokenizer_from_json
from ast import literal_eval
from scripts import tools


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
            #print('No Date or Invalid Date')
            return None
    else:
        try:
            return parse(str(x), default=datetime(2022, 1, 1))
        except:
            #print('No Date or Invalid Date')
            return None

def clean_tok(t):
    return t.strip().replace("’","'").replace(" - ","")

# pre-processing texts (cleaning, lemmas, readability)
def preprocess(df):

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
    nlp_placeholder = st.empty()

    for i,r in df.iterrows():

        nlp_placeholder.markdown(f'Processing item {ct:,} of {len(df):,} ({int(ct/len(df)*100)}% complete)')

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

    nlp_placeholder.markdown('*Text cleaning and lemmatization complete.*')

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

    if 'init_data' in state and state.init_data == 'douglas':
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
    state.colors = [c for c in sns.color_palette('Set2', len(state.df.source.unique())).as_hex()]

# load default data when no data is present
def init_data():

    # # if data already exists, skip the rest
    if 'init' in state and state.init == True:
        return
    data_set = True
    data_select = st.empty()

    # uncomment this block to undo default dataset
    # # default data has not been set
    # if 'init_data' not in state:
    #
    #     data_set = False
    #
    #     with data_select.container():
    #         st.info("Default data has not been set. This may have been caused by reloading the page, which can cause the user's cache to be reset.")
    #         data_info = st.empty()
    #
    #         for i in [5,4,3,2,1]:
    #             data_info.warning(f"Returning you to the home page in {i} seconds.")
    #             time.sleep(1)
    #
    #         tools.switch_page('Home')

    # comment out the next two lines to unde default dataset
    state.init_data = 'douglas'
    data_set = True

    if data_set == True:

        data_select.empty()
        # set input data files
        if state.init_data == 'douglas':
            current_csv = 'data/DouglasCoKs.csv'
            tk_js = 'data/tokenizer.json'
            state.date_access = 'Month'
        elif state.init_data == 'placeholder':
            current_csv = 'data/placeholder.csv'
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

        # set other default values for session_state
        state.df = df
        default_vals()

        loading.empty()

        state.init = True
        return True


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
    state.colors = [c for c in sns.color_palette('Set2', len(state.df.source.unique())).as_hex()]

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

def read_zip(zf):

    zipinfo = st.empty()
    csv_inv = None
    with zipfile.ZipFile(zf, "r") as z:
        csvs = [fn for fn in z.namelist() if fn.endswith('.csv') and not fn.split('/')[-1].startswith('._')]
        txts = [fn for fn in z.namelist() if fn.endswith('.txt') and not fn.split('/')[-1].startswith('._')]

    with zipinfo.container():
        st.info('Preparing ZIP file')

        if len(csvs) == 0:
            st.markdown(f'No CSV files were found in the ZIP file. Please check the contents and try again.')
            csv_inv = None
            st.stop()
        if len(csvs) == 1:
            csv_inv = csvs[0]
            st.markdown(f'Found {len(txts)} TXT files in this ZIP file.')
            st.markdown(f'Found one CSV file in the ZIP file. "{csv_inv}" will be used as the inventory.')
        if len(csvs) > 1:
            zcols = st.columns(2)
            with zcols[0]:
                st.markdown(f'Found {len(txts)} TXT files in this ZIP file.')
                csv_inv = st.selectbox('The ZIP file contained more than one CSV file. Which one is the inventory?', [''] + csvs)

        if csv_inv not in [None, '']:
            with zipfile.ZipFile(zf, "r") as z:
                with z.open(csv_inv) as c:
                    try:
                        df = pd.read_csv(c)
                        # drop empty columns and duplicates
                        df.dropna(how='all', axis=1, inplace=True)
                        df.drop_duplicates(inplace=True)
                        st.write(f'Here is a sample of your inventory ({len(df):,} items). Please select the column that contains the filename. The other data will be mapped in the next step. Note that only entries that can be mapped to a txt file will be retained.')

                        st.write(df.head(1))

                        fn_cols = st.columns(2)
                        with fn_cols[0]:
                            # user id filename in df
                            with st.form(key='zip_inv'):
                                fn_column = st.selectbox('Choose a column that matches your filenames.', df.columns)
                                fn_submit = st.form_submit_button('Go')

                        if fn_submit:
                            df[fn_column] = df[fn_column].apply(lambda x: '' if isinstance(x, float) else str(x))

                            txtmatch = st.empty()
                            success, fail = 0,0

                            # for each txt in the zip file, find matching entry in df
                            df['full_text'] = None


                            for i,r in df.iterrows():
                                try:
                                    txt = [fn for fn in z.namelist() if r[fn_column] in fn][0]
                                    df.at[i, 'full_text'] = ' '.join(z.read(txt).decode('utf-8').split())
                                    success += 1
                                except:
                                    st.error(f'{r[fn_column]} is in the csv, but was not found in the zip file.')
                                    fail += 1

                            # for t in txts:
                            #
                            #     ct += 1
                            #     txtmatch.write(f'Matching text files to inventory: {ct} of {len(txts)}')
                            #     match = df.index[(df[fn_column]==t) | (df[fn_column]==t.replace('.txt',''))].tolist()
                            #
                            #     if len(match) == 0:
                            #         st.error(f'No matching entry in the inventory for {t} - **skipped**')
                            #         fail += 1
                            #     elif len(match) >1:
                            #         st.error(f'More than one matching entry in the inventory for {t} - **skipped**')
                            #         dupe += 1
                            #     # only one match, read full text into df
                            #     else:
                            #         try:
                            #             with z.open(t) as f:
                            #                 full_text = (' '.join(z.read(t).decode('utf-8').split()))
                            #                 df.at[match[0], 'full_text'] = full_text
                            #                 success += 1
                            #         except:
                            #             print(f'File [{fn}] was not able to be read as a text file.')
                            #             fail += 1
                            #             continue
                            st.write("#### Status report")
                            st.write(f"""* Number of txt files in ZIP file:   **{len(txts):,}**
* Inventory found:   **{csv_inv}**
* Number of entries in the inventory:   **{len(df):,}**
* Number of txt files matched to inventory:   **{success:,}**
* Number of txt files not found in inventory:   **{fail:,}**
                            """)

                            # filter to only entries with a full_text entry
                            df = df[~df.full_text.isnull()]
                            return df

                    except:
                        # if csv can't be read as a df, error
                        st.write('This CSV file cannot be read. Please check the contents and try again.')
                        raise
                        st.stop()


# allow user upload (csv, excel, json)
def user_upload(uploaded_file):

    if uploaded_file.type == 'text/csv':
        df = pd.read_csv(uploaded_file)
        return df
    elif uploaded_file.type == 'application/zip':
        df = read_zip(uploaded_file)
        # return df.sample(30)
        return df
    # elif uploaded_file.type == 'application/json':
    #     df = pd.read_json(uploaded_file)
    #     # return df.sample(30)
    #     return df
    else:
        st.markdown(f"You uploaded {uploaded_file.name} -- Please upload in CSV format.")
        return None
