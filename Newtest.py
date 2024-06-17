import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent, SmartDataframe
import speech_recognition as sr

# Set the API key
PANDASAI_API_KEY = "$2a$10$PBlknZ8TbfB9QGzjvEU1g.Z5Nw9p4ldw2w4vSc/VJismDrVrO9X7G"  # Replace with your actual API key
os.environ["PANDASAI_API_KEY"] = PANDASAI_API_KEY

st.title("Data Analysis with Speech Input")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
st.write(uploaded_file)
file_extension = uploaded_file.name.split('.')[-1].lower()
if file_extension in ['xlsx', 'xls']:
            data = pd.read_excel(uploaded_file)
            st.write(data.head())
user_query = st.text_input("Enter your query:", "show top 10 Amount by Customer")
st.write(user_query)
agent = Agent(data)
result = agent.chat(user_query)
st.write(result)


