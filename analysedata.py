import queue
import time
import os
import numpy as np
import pydub
import streamlit as st
from pathlib import Path
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from deepspeech import Model

HERE = Path(__file__).parent

MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm"
SCORER_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"
MODEL_LOCAL_PATH = HERE / "deepspeech-0.9.3-models.pbmm"
SCORER_LOCAL_PATH = HERE / "deepspeech-0.9.3-models.scorer"

# Download the model and scorer if not already present
@st.cache_resource
def download_file(url, dest_path):
    if not dest_path.exists():
        with st.spinner(f"Downloading {url}..."):
            os.system(f"wget {url} -O {dest_path}")

download_file(MODEL_URL, MODEL_LOCAL_PATH)
download_file(SCORER_URL, SCORER_LOCAL_PATH)

# Load the DeepSpeech model
@st.cache_resource
def load_model():
    model = Model(str(MODEL_LOCAL_PATH))
    model.enableExternalScorer(str(SCORER_LOCAL_PATH))
    model.setScorerAlphaBeta(0.931289039105002, 1.1834137581510284)
    model.setBeamWidth(100)
    return model

model = load_model()

st.header("Real-Time Speech-to-Text")
st.write("Speak into your microphone, and the app will transcribe your speech in real time.")

def audio_callback(audio_frame):
    global stream
    if stream is None:
        stream = model.createStream()
    sound = pydub.AudioSegment(
        data=audio_frame.to_ndarray().tobytes(),
        sample_width=audio_frame.format.bytes,
        frame_rate=audio_frame.sample_rate,
        channels=len(audio_frame.layout.channels),
    )
    sound = sound.set_channels(1).set_frame_rate(model.sampleRate())
    buffer = np.array(sound.get_array_of_samples())
    stream.feedAudioContent(buffer)
    text = stream.intermediateDecode()
    text_output.markdown(f"**Text:** {text}")

webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDONLY,
    audio_receiver_size=1024,
    media_stream_constraints={"video": False, "audio": True},
    audio_frame_callback=audio_callback,
)

stream = None
text_output = st.empty()
status_indicator = st.empty()

if not webrtc_ctx.state.playing:
    status_indicator.write("Waiting for input...")
else:
    status_indicator.write("Running. Say something!")
