import streamlit as st
from hydralit import HydraHeadApp

# short script to override default loading animation
class MyLoadingApp(HydraHeadApp):

    def __init__(self, title = 'Loader', delay=0,loader=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.delay = delay
        self._loader = loader

    def run(self,app_target):

        try:
            app_target.run()

        except Exception as e:
            st.image("./resources/failure.png",width=100,)
            st.error('An error has occurred, someone will be punished for your inconvenience, we humbly request you try again.')
            st.error('Error details: {}'.format(e))
