# Using virtual environment to create a local Streamlit application

## Startup the environment

### Conda

*Note: Conda seems to load and run app a bit faster than venv*

Create the environment (first run only)

    $conda env create -f environment.yml

**Start the environment**

    $conda activate news_analysis

Load additional dataset (first run only)

    $python -m spacy download en_core_web_sm
    $pip install hydralit
    $pip install textdescriptives
    $pip install multi_rake

**Run the app**

    $streamlit run app.py

Update the environment, e.g. changes to .yml

    $conda env update -f environment.yml --prune

Close the environment

    $conda deactivate

Remove the environment

    $conda env remove -n news_analysis

### Venv

Create the environment (first run only)

    $python -m venv venv/

**Start the environment**

    $source venv/bin/activate

Load additional libraries (first run only)

    $pip install -r requirements.txt
    $python -m spacy download en_core_web_sm

**Run the app**

    $streamlit run app.py

Update the environment, e.g. changes to requirements.txt

    TBD

Close the environment

    $deactivate

Remove the environment

    $rm -r venv/
