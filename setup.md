% Using virtual environment to create local Streamlit application

# Venv

*This method is also easier to use with Streamlit Sharing, as not all libraries are available in conda*

Create the environment (first run only)

    $python -m venv venv/

**Start the environment**

    $source venv/bin/activate

Load additional libraries (first run only, or if requirements change)

    $pip install -r requirements.txt

    * Any issues? See Troubleshooting notes in requirements.txt

**Run the app**

    $streamlit run app.py

Close the environment

    $deactivate

Remove the environment

    $rm -r venv/

## TROUBLESHOOTING

Requires Python =<3.8 (as of Aug 2022, no tensorflow on PY3.9 or above)

See requirements.txt to make sure you have the right version of tensorflow installed.

M1 Mac: If hypy (dependency of some libraries) fails, may need to run the following:

    export HDF5_DIR=/opt/homebrew/Cellar/hdf5/[VERSION]
    pip install h5py
    pip install -r requirements.txt

M1 Mac: if grpcio fails, try the following

    export GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
    export GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1
    pip install -r requirements.txt

Problems with installing tensorflow factories (e.g. spacytextblob)? You may need a Rust compiler (check carefully the error message), try this:

    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"


# Conda [instructions may be incomplete]

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
