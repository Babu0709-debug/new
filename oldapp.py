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

# File uploader for CSV or Excel files
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format")
            st.stop()

        st.dataframe(df.head())

        # Recording and recognizing speech
        try:
            st.write("Click 'Record' to start recording your query.")
            if st.button('Record'):
                audio_bytes = mic_recorder()
                if audio_bytes:
                    recognizer = sr.Recognizer()
                    audio = sr.AudioFile(audio_bytes)

                    with audio as source:
                        audio_data = recognizer.record(source)

                    try:
                        query = recognizer.recognize_google(audio_data)
                        st.write(f"Recognized query: {query}")

                        agent = Agent(df)
                        result = agent.chat(query)
                        st.write(result)

                    except sr.UnknownValueError:
                        st.error("Could not understand the audio.")
                    except sr.RequestError as e:
                        st.error(f"Could not request results from Google Speech Recognition service; {e}")
                else:
                    st.warning("No audio recorded. Please try again.")
        except Exception as e:
            st.error(f"Speech-to-text conversion failed: {e}")

    except Exception as e:
        st.error(f"Error processing the uploaded file: {e}")
else:
    st.info("Please upload a CSV or Excel file.")