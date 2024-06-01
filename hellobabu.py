import streamlit as st
import pandas as pd
import os
import av
import cv2
import numpy as np
import queue
from pathlib import Path
from typing import List, NamedTuple
from pandasai import Agent
import speech_recognition as sr
import requests
from streamlit_webrtc import WebRtcMode, webrtc_streamer, AudioProcessorBase

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$MHuoFeCBDOCs.FEqhIMqHuwcZLeb61BQwFRx085ugjCgz4NKxxe9S"

class StreamlitApp:
    def __init__(self):
        self.df = None
        self.recognizer = sr.Recognizer()

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

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        audio_data = frame.to_ndarray()
        audio = sr.AudioData(audio_data.tobytes(), frame.sample_rate, frame.channels)
        try:
            text = self.recognizer.recognize_google(audio)
            st.success(f"You said: {text}")
        except sr.UnknownValueError:
            st.error("Google Speech Recognition could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results from Google Speech Recognition service; {e}")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        return frame

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
        st.write("## Analyze the Data")
        
        query = st.text_input("Enter your query:")
        
        if st.button("Submit Text Query"):
            self.process_query(query)
        
        if st.button("Start to talk"):
            query = self.recv()
            self.process_query(query)
            #pass  # We'll handle microphone input in the WebRTC streamer

    def run(self):
        st.set_page_config(page_title="FP&A", page_icon="💻")
        st.title("FP&A")
        self.upload_file()
        self.chat_query()

        # Add the WebRTC streamer here with only audio access
        webrtc_ctx = webrtc_streamer(
            key="object-detection",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration={
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}],  # Default STUN server
            },
            audio_frame_callback=self.recv,
            media_stream_constraints={"audio": True},
            async_processing=True,
        )

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
