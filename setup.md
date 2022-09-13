# Using virtual environment to create local Streamlit application

## pyenv

***https://realpython.com/intro-to-pyenv***

$brew install pyenv  
$brew install pyenv-virtualenv

*Note that several of these libraries need Python 3.8 or earlier
$pyenv virtualenv 3.8.13 pyenv



## Venv

*This method is also easier to use with Streamlit Sharing, as not all libraries are available in conda*

Create the environment (first run only)

    $python -m venv venv/

**Start the environment**

    $source venv/bin/activate

Load additional libraries (first run only, or if requirements change)

    $pip install -r requirements.txt

**Run the app**

    $streamlit run app.py

Close the environment

    $deactivate

Remove the environment

    $rm -r venv/

## Conda

*Note: Conda seems to load and run app a bit faster than venv, but requires a few extra steps*  

Rename environment_CONDA.yml to environment.yml

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
