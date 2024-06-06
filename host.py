import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$BvCK6YxJ2CH1SB1UFYCwr.JtZUXsRwUd4uiRpEL8pgU.9zGD7sRd2"  # Replace with your actual API key

# Streamlit app header
st.title("CSV/Excel File Analysis with Voice Query")

# Upload file section
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

# Process the uploaded file
if uploaded_file:
    try:
        # Determine the file type and read it accordingly
        file_extension = uploaded_file.name.split('.')[-1].lower()
        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
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
            # Convert audio to text
            query = speech_to_text(language='en')
            st.write(f"Recognized query: {query}")

            # Use PandasAI to analyze the query
            if query:
                agent = Agent(df)
                result = agent.chat(query)
                st.write("Result:")
                st.write(result)
            else:
                st.write("Could not recognize any speech. Please try again.")
                
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.write("Please upload a CSV or Excel file.")
