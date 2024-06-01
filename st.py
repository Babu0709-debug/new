import streamlit as st
import pandas as pd
import os
from pandasai import Agent
import speech_recognition as sr
from flask import Flask, request, jsonify
from threading import Thread
from werkzeug.serving import run_simple
import base64
import io

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$MHuoFeCBDOCs.FEqhIMqHuwcZLeb61BQwFRx085ugjCgz4NKxxe9S"

app = Flask(__name__)

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
            st.write('<script>startRecording();</script>', unsafe_allow_html=True)

    def run(self):
        st.set_page_config(page_title="FP&A", page_icon="💻")
        st.title("FP&A")
        self.upload_file()
        self.chat_query()

# Flask route to handle audio data
@app.route('/upload', methods=['POST'])
def upload_audio():
    data = request.json
    audio_data = base64.b64decode(data['audio'].split(',')[1])
    recognizer = sr.Recognizer()
    audio_file = io.BytesIO(audio_data)
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio)
        return jsonify({"message": f"Transcription: {text}"})
    except sr.UnknownValueError:
        return jsonify({"message": "Could not understand audio"})
    except sr.RequestError:
        return jsonify({"message": "Could not request results"})

# Run Flask server in a separate thread
def run_flask():
    run_simple('0.0.0.0', 5000, app)

thread = Thread(target=run_flask)
thread.start()

# JavaScript code to capture audio
st.markdown("""
<script>
  async function startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    let chunks = [];
    mediaRecorder.ondataavailable = event => chunks.push(event.data);
    mediaRecorder.onstop = async () => {
      const blob = new Blob(chunks, { 'type' : 'audio/webm; codecs=opus' });
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = function() {
        const base64data = reader.result;
        fetch('/upload', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ audio: base64data })
        }).then(response => response.json()).then(data => {
          alert(data.message);
        });
      }
    };
    mediaRecorder.start();
    setTimeout(() => mediaRecorder.stop(), 5000); // Record for 5 seconds
  }
</script>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()