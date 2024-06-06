import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent
import speech_recognition as sr

# Set the API key
PANDASAI_API_KEY = "$2a$10$MHuoFeCBDOCs.FEqhIMqHuwcZLeb61BQwFRx085ugjCgz4NKxxe9S"
os.environ["PANDASAI_API_KEY"] = PANDASAI_API_KEY

st.title("Data Analysis with Speech Input")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.write("Unsupported file format")

        st.dataframe(df.head())

        try:
            query = speech_to_text(language='en')
            if query:
                st.write(f"Recognized query: {query}")
                agent = Agent(df)
                result = agent.chat(query)
                st.write(result)
            else:
                st.write("Could not recognize any speech. Please try again.")
        except Exception as e:
            st.write(f"Speech-to-text conversion failed: {e}")

    except Exception as e:
        st.write(f"Error processing the uploaded file: {e}")
else:
    st.write("Please upload a CSV or Excel file.")