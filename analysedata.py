import logging
import queue
import threading
import time
import urllib.request
import os
from pathlib import Path
from collections import deque
from typing import List

import av
import numpy as np
import pydub
import streamlit as st
from twilio.rest import Client

from streamlit_webrtc import WebRtcMode, webrtc_streamer

import pandas as pd
from pandasai import Agent  # Ensure this import is correct

# Set the PandasAI API key
os.environ["PANDASAI_API_KEY"] = "$2a$10$bfv.IeS9MdkG6k7MPDUbr.QzdIs7G2TXd49VKY9jtb1pkWN./46xO"

HERE = Path(__file__).parent
logger = logging.getLogger(__name__)

# Function to download a file from a URL
def download_file(url, download_to: Path, expected_size=None):
    if download_to.exists():
        if expected_size:
            if download_to.stat().st_size == expected_size:
                return
        else:
            st.info(f"{url} is already downloaded.")
            if not st.button("Download again?"):
                return

    download_to.parent.mkdir(parents=True, exist_ok=True)
    weights_warning, progress_bar = None, None
    try:
        weights_warning = st.warning("Downloading %s..." % url)
        progress_bar = st.progress(0)
        with open(download_to, "wb") as output_file:
            with urllib.request.urlopen(url) as response:
                length = int(response.info()["Content-Length"])
                counter = 0.0
                MEGABYTES = 2.0 ** 20.0
                while True:
                    data = response.read(8192)
                    if not data:
                        break
                    counter += len(data)
                    output_file.write(data)
                    weights_warning.warning(
                        "Downloading %s... (%6.2f/%6.2f MB)"
                        % (url, counter / MEGABYTES, length / MEGABYTES)
                    )
                    progress_bar.progress(min(counter / length, 1.0))
    finally:
        if weights_warning is not None:
            weights_warning.empty()
        if progress_bar is not None:
            progress_bar.empty()

@st.cache_data
def get_ice_servers():
    try:
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    except KeyError:
        logger.warning("Twilio credentials are not set. Fallback to a free STUN server from Google.")
        return [{"urls": ["stun:stun.l.google.com:19302"]}]

    client = Client(account_sid, auth_token)
    token = client.tokens.create()
    return token.ice_servers

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

        # Add the speech-to-text functionality
        self.speech_to_text()

    def speech_to_text(self):
        webrtc_ctx = webrtc_streamer(
            key="speech-to-text",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            rtc_configuration={"iceServers": get_ice_servers()},
            media_stream_constraints={"video": False, "audio": True},
        )

        status_indicator = st.empty()

        if not webrtc_ctx.state.playing:
            return

        status_indicator.write("Loading...")
        text_output = st.empty()
        stream = None

        while True:
            if webrtc_ctx.audio_receiver:
                if stream is None:
                    from deepspeech import Model

                    MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm"
                    LANG_MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"
                    MODEL_LOCAL_PATH = HERE / "models/deepspeech-0.9.3-models.pbmm"
                    LANG_MODEL_LOCAL_PATH = HERE / "models/deepspeech-0.9.3-models.scorer"

                    download_file(MODEL_URL, MODEL_LOCAL_PATH, expected_size=188915987)
                    download_file(LANG_MODEL_URL, LANG_MODEL_LOCAL_PATH, expected_size=953363776)

                    lm_alpha = 0.931289039105002
                    lm_beta = 1.1834137581510284
                    beam = 100

                    model = Model(str(MODEL_LOCAL_PATH))
                    model.enableExternalScorer(str(LANG_MODEL_LOCAL_PATH))
                    model.setScorerAlphaBeta(lm_alpha, lm_beta)
                    model.setBeamWidth(beam)

                    stream = model.createStream()

                    status_indicator.write("Model loaded.")

                sound_chunk = pydub.AudioSegment.empty()
                try:
                    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                except queue.Empty:
                    time.sleep(0.1)
                    status_indicator.write("No frame arrived.")
                    continue

                status_indicator.write("Running. Say something!")

                for audio_frame in audio_frames:
                    sound = pydub.AudioSegment(
                        data=audio_frame.to_ndarray().tobytes(),
                        sample_width=audio_frame.format.bytes,
                        frame_rate=audio_frame.sample_rate,
                        channels=len(audio_frame.layout.channels),
                    )
                    sound_chunk += sound

                if len(sound_chunk) > 0:
                    sound_chunk = sound_chunk.set_channels(1).set_frame_rate(model.sampleRate())
                    buffer = np.array(sound_chunk.get_array_of_samples())
                    stream.feedAudioContent(buffer)
                    text = stream.intermediateDecode()
                    text_output.markdown(f"**Text:** {text}")
            else:
                status_indicator.write("AudioReceiver is not set. Abort.")
                break

    def run(self):
        st.title("Talk with Data")
        self.upload_file()
        self.chat_query()

if __name__ == "__main__":
    app = StreamlitApp()
    app.run()
