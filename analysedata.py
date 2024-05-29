import streamlit as st
import pandas as pd
import os
from pandasai import Agent  # Ensure this import is correct

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$bfv.IeS9MdkG6k7MPDUbr.QzdIs7G2TXd49VKY9jtb1pkWN./46xO"

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
                st.dataframe(self.df)
            except Exception as e:
                st.error(f"Error loading file: {e}")

    def speech_to_text(self):
        # HTML and JavaScript for speech recognition
        speech_recognition_js = """
        <script>
        function startRecognition() {
            var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            recognition.start();

            recognition.onresult = function(event) {
                var transcript = event.results[0][0].transcript;
                document.getElementById('recognizedText').value = transcript;
                document.getElementById('speechForm').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
            };

            recognition.onspeechend = function() {
                recognition.stop();
            };

            recognition.onerror = function(event) {
                console.error('Error occurred in recognition: ' + event.error);
            };
        }
        </script>
        <form id="speechForm" method="post" onsubmit="handleSubmit(event)">
            <input type="hidden" id="recognizedText" name="recognizedText">
            <button type="button" onclick="startRecognition()">Start Speech Recognition</button>
        </form>
        <script>
        function handleSubmit(event) {
            event.preventDefault();
            const recognizedText = document.getElementById('recognizedText').value;
            const streamlitInput = Streamlit.setComponentValue(recognizedText);
        }
        </script>
        """

        st.markdown(speech_recognition_js, unsafe_allow_html=True)

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
        st.write("## Query the Data")

        query = st.text_input("Enter your query:")

        if st.button("Submit Text Query"):
            self.process_query(query)

        if st.button("Start Recording"):
            self.speech_to_text()
            if 'recognizedText' in st.session_state:
                query = st.session_state['recognizedText']
                self.process_query(query)

    def run(self):
        st.title("Talk with Data")
        self.upload_file()
        self.chat_query()

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()