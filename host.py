import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent
import speech_recognition as sr

os.environ["PANDASAI_API_KEY"] = "$2a$10$BvCK6YxJ2CH1SB1UFYCwr.JtZUXsRwUd4uiRpEL8pgU.9zGD7sRd2"

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
df = pd.read_excel(uploaded_file)
st.dataframe(df.head())
query = st.write(speech_to_text(language='en'))
agent = Agent(df)
result = agent.chat(query)
st.write(result)
    
