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

        # Debug: Print the audio_dict to see what is returned
        st.write("Audio dict:", audio_dict)

        # Check if audio_dict is not None and contains 'audio_data'
        if audio_dict is None:
            st.error("mic_recorder returned None. Please ensure your microphone is working and try again.")
        elif 'audio_data' not in audio_dict:
            st.error("No audio data found in the recording. Please try recording your query again.")
        else:
            audio_bytes = audio_dict['audio_data']

            # Save audio bytes to a temporary file
            audio_file_path = "temp_audio.wav"
            with open(audio_file_path, "wb") as f:
                f.write(audio_bytes)

            # Recognize speech using SpeechRecognition
            recognizer = sr.Recognizer()
            try:
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
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")
            except sr.UnknownValueError:
                st.error("Google Speech Recognition could not understand the audio")
            except Exception as e:
                st.error(f"An error occurred while processing the audio file: {e}")

        # Fallback method: Upload an audio file manually
        st.write("Or upload a WAV file with your query:")
        uploaded_audio_file = st.file_uploader("Upload an audio file", type=["wav"])
        if uploaded_audio_file:
            with open("uploaded_audio.wav", "wb") as f:
                f.write(uploaded_audio_file.getbuffer())
            try:
                with sr.AudioFile("uploaded_audio.wav") as source:
                    audio_data = recognizer.record(source)
                    query = recognizer.recognize_google(audio_data)
                    st.write(f"Your query: {query}")

                    # Use PandasAI to analyze the query
                    agent = Agent(df)
                    result = agent.chat(query)
                    st.write("Result:")
                    st.write(result)
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")
            except sr.UnknownValueError:
                st.error("Google Speech Recognition could not understand the audio")
            except Exception as e:
                st.error(f"An error occurred while processing the audio file: {e}")

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload a CSV or Excel file to proceed.")
