import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent
import speech_recognition as sr

os.environ["PANDASAI_API_KEY"] = "$2a$10$BvCK6YxJ2CH1SB1UFYCwr.JtZUXsRwUd4uiRpEL8pgU.9zGD7sRd2"

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'csv':
        df = pd.read_csv(uploaded_file)
    elif file_extension in ['xlsx', 'xls']:
        df = pd.read_excel(uploaded_file)
    
    st.dataframe(df.head())
    query = st.write(speech_to_text(language='en'))
    try:
        query = speech_to_text(language='en')
        if query:
            agent = Agent(df)
            result = agent.chat(query)
            st.write(result)
        else:
            st.write("Could not recognize any speech. Please try again.")
    except Exception as e:
        st.write(f"An error occurred: {e}")
else:
    st.write("Please upload a CSV or Excel file.")
