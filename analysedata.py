import streamlit as st
import pandas as pd
import os
from pandasai import Agent  # Ensure this import is correct
import speech_recognition as sr

os.environ["PANDASAI_API_KEY"] = "$2a$10$bfv.IeS9MdkG6k7MPDUbr.QzdIs7G2TXd49VKY9jtb1pkWN./46xO"

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
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Please say something...")
            audio = recognizer.listen(source)
        
        try:
            query = recognizer.recognize_google(audio)
            st.success(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand the audio.")
            return ""
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

    def process_query(self, query):
        if query:
            if self.df is not None:
                agent = Agent(self.df)
                result = agent.chat(query)  # Ensure this method exists and works as expected
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
