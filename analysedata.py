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
        # JavaScript code for speech recognition
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
                const streamlitMessage = transcript;
                const message = {
                    isStreamlitMessage: true,
                    streamlitMessage: streamlitMessage,
                };
                window.parent.postMessage(message, "*");
            };

            recognition.onspeechend = function() {
                recognition.stop();
            };

            recognition.onerror = function(event) {
                console.error('Error occurred in recognition: ' + event.error);
            };
        }

        window.addEventListener("message", (event) => {
            const data = event.data;
            if (data.isStreamlitMessage) {
                const recognizedTextElement = document.getElementById("recognizedText");
                recognizedTextElement.value = data.streamlitMessage;
                const speechForm = document.getElementById("speechForm");
                speechForm.submit();
            }
        });
        </script>
        """

        # HTML form to capture speech recognition result
        html_code = """
        <form id="speechForm" method="post">
            <input type="hidden" id="recognizedText" name="recognizedText">
        </form>
        <button onclick="startRecognition()">Start Speech Recognition</button>
        """

        # Render the HTML and JavaScript in Streamlit
        st.markdown(html_code + speech_recognition_js, unsafe_allow_html=True)

        # Capture the form submission using Streamlit's session state
        if st.session_state.get('recognizedText'):
            return st.session_state['recognizedText']
        else:
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