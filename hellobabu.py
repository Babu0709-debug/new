import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent
import speech_recognition as sr 

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
            
    def run(self):
        st.set_page_config(page_title="FP&A", page_icon="💻")
        st.title("FP&A")
        self.upload_file()
        
        self.speech_input = speech_to_text(language='en')
        st.write(f"Speech Input: {self.speech_input}")
        
        if self.speech_input:
            if self.df is not None:
                try:
                    agent = Agent(self.df)  # Define agent here
                    result = agent.chat(self.speech_input)
                    st.write(result)
                except Exception as e:
                    st.error(f"Error processing speech input with Agent: {e}")
            else:
                st.error("Please upload a DataFrame first.")
        else:
            st.info("Please provide a speech input.")

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
