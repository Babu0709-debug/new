import streamlit as st
import pandas as pd
import os
from google.cloud import speech_v1p1beta1 as speech

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$MHuoFeCBDOCs.FEqhIMqHuwcZLeb61BQwFRx085ugjCgz4NKxxe9S" 

class StreamlitApp:
    def __init__(self):
        self.df = None

    def upload_file(self):
        uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])
        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            try:
                if file_extension == 'csv':
                    self.df = pd.read_csv(uploaded_file)
                elif file_extension in ['xlsx', 'xls']:
                    self.df = pd.read_excel(uploaded_file)
                st.success("Dataframe loaded successfully!")
                st.dataframe(self.df.head())
            except Exception as e:
                st.error(f"Error loading file: {e}")

    def speech_to_text(self, language='en-US'):
        client = speech.SpeechClient()

        config = {
            'encoding': speech.RecognitionConfig.AudioEncoding.LINEAR16,
            'sample_rate_hertz': 16000,
            'language_code': language,
        }

        audio = {
            'content': b'',  # Replace with the audio content
        }

        response = client.recognize(config=config, audio=audio)

        if response.results:
            return response.results[0].alternatives[0].transcript
        else:
            return None

    def run(self):
        st.set_page_config(page_title="FP&A", page_icon="💻")
        st.title("FP&A")
        self.upload_file()
        
        # Capture speech input and process it
        if st.button("Start to talk"):
            speech_input = self.speech_to_text(language='en-US')
            st.write(speech_input)
            if speech_input:
                if self.df is not None:
                    # Process speech input using Agent
                    # agent = Agent(self.df)  # Define agent here
                    # result = agent.chat(speech_input)
                    # st.write(result)
                    st.write("Speech input processed successfully.")
                else:
                    st.error("Please upload a file first.")

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
