import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder
from pandasai import Agent
import speech_recognition as sr

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$BvCK6YxJ2CH1SB1UFYCwr.JtZUXsRwUd4uiRpEL8pgU.9zGD7sRd2"

# Streamlit app header
st.title("CSV/Excel File Analysis with Voice Query")

# Upload file section
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

# Process the uploaded file
if uploaded_file:
    try:
        # Determine the file type and read it accordingly
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Display the first few rows of the dataframe
        st.dataframe(df.head())

        # Record and convert speech to text
        st.write("Record your query:")
        audio_dict = mic_recorder()

        # Check if audio_dict is not None and contains 'audio_data'
        if audio_dict and 'audio_data' in audio_dict:
            audio_bytes = audio_dict['audio_data']

            recognizer = sr.Recognizer()
            audio_file_path = "temp_audio.wav"

            # Save audio bytes to a temporary file
            with open(audio_file_path, "wb") as f:
                f.write(audio_bytes)

            # Recognize speech using SpeechRecognition
            with sr.AudioFile(audio_file_path) as source:
                audio_data = recognizer.record(source)
                query = recognizer.recognize_google(audio_data)
                st.write(f"Your query: {query}")

                # Use PandasAI to analyze the query
                agent = Agent(df)
                result = agent.chat(query)
                st.write("Result:")
                st.write(result)

            # Clean up temporary audio file
            os.remove(audio_file_path)
        else:
            st.error("No audio data received. Please try recording your query again.")

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV or Excel file to proceed.")
