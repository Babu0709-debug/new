import streamlit as st
import pandas as pd
import os
from pandasai import Agent
import sounddevice as sd
import numpy as np
import tempfile
import whisper

# Set up environment variable for pandasai API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$jtX1xbqADs4395M3DE9ZcuCx/15PDyWCIe40oLHgyZqEVtvH5lEeG"

def analyze_data(df):
    summary = df.describe()
    return summary

def query_data(df, query):
    if query.lower().startswith('describe '):
        column_name = query.split(' ')[1]
        if column_name in df.columns:
            return df[column_name].describe()
        else:
            return f"Column '{column_name}' not found in the dataframe."
    else:
        return

class StreamlitApp:
    def __init__(self):
        self.df = None
        self.whisper_model = whisper.load_model("base")

    def upload_file(self):
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            if file_extension == 'csv':
                self.df = pd.read_csv(uploaded_file)
            elif file_extension in ['xlsx', 'xls']:
                self.df = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file type!")
                return

            st.success("Dataframe loaded successfully!")
            st.dataframe(self.df)

    def speech_to_text(self):
        st.info("Please say something...")

        # Record audio using sounddevice
        duration = 5  # seconds
        fs = 44100  # Sample rate
        st.info("Recording...")
        audio_data = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # Wait until recording is finished
        audio_data = np.squeeze(audio_data)

        # Save audio to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            temp_audio_file_name = temp_audio_file.name
            sd.write(temp_audio_file_name, audio_data, fs)
        
        # Use whisper model to transcribe audio
        result = self.whisper_model.transcribe(temp_audio_file_name)
        query = result["text"]

        st.success(f"You said: {query}")
        return query

    def process_query(self, query):
        if query:
            if self.df is not None:
                agent = Agent(self.df)
                result = agent.chat(query)
                st.write(result)
            else:
                st.error("Please upload a file first!")
        else:
            st.error("No query provided.")

    def chat_query(self):
        st.write("## Query the Data")

        query = st.text_input("Enter your query:")

        if st.button("Submit Text Query"):
            self.process_query(query)

        if st.button("Start Recording"):
            query = self.speech_to_text()
            self.process_query(query)

    def run(self):
        st.title("Talk with Data")
        self.upload_file()
        self.chat_query()

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
