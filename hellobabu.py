import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text

st.write(speech_to_text(language='en'))
