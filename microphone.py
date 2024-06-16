import streamlit as st
import pandas as pd
import os
from pandasai import Agent  # Ensure this import is correct
import speech_recognition as sr

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$MHuoFeCBDOCs.FEqhIMqHuwcZLeb61BQwFRx085ugjCgz4NKxxe9S"

def analyze_data(df):
    return df.describe()

def query_data(df, query):
    if query.lower().startswith('describe '):
        column_name = query.split(' ')[1]
        if column_name in df.columns:
            return df[column_name].describe()
        else:
            return f"Column '{column_name}' not found in the dataframe."
    else:
        return "Invalid query."

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

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        try:
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
            except Exception as e:
                st.error(f"An error occurred: {e}")
                return ""
        except OSError as e:
            st.error("No Default Input Device Available.")
            st.warning("Please ensure that your device has a working microphone and that your browser has permission to access it. Here are some tips:")
            st.write("""
            - **Check Device Settings:** Ensure your microphone is enabled and working. Test it with another application to verify.
            - **Browser Permissions:** Make sure your browser has permission to access the microphone. You can usually find this in the browser's settings under privacy or permissions.
            - **Use a Supported Browser:** Use browsers like Chrome or Firefox, which have robust support for microphone access.
            - **External Microphone:** If you are using an external microphone, ensure it is properly connected.
            """)
            return ""
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return ""

    def process_query(self, query):
        if query:
            if self.df is not None:
                agent = Agent(self.df)
                try:
                    result = agent.chat(query)
                    st.write(result)
                except Exception as e:
                    st.error(f"Error processing query: {e}")
            else:
                st.error("Please upload a file first!")
        else:
            st.error("No query provided.")

    def chat_query(self):
        st.write("## Analyse the Data")

        query = st.text_input("Enter your query:")

        if st.button("Submit Text Query"):
            self.process_query(query)

        if st.button("Start to talk"):
            query = self.speech_to_text()
            self.process_query(query)

    def run(self):
        st.set_page_config(page_title="FP&A", page_icon="💻")
        st.title("FP&A")
        self.upload_file()
        self.chat_query()

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()