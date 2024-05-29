import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import numpy as np
import pydub
from deepspeech import Model
import queue
import os
import urllib.request

# Function to download model files
def download_file(url, download_to):
    if not os.path.exists(download_to):
        with urllib.request.urlopen(url) as response, open(download_to, 'wb') as out_file:
            data = response.read()
            out_file.write(data)

# Download DeepSpeech model and scorer
model_url = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm"
scorer_url = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"
model_local_path = "deepspeech-0.9.3-models.pbmm"
scorer_local_path = "deepspeech-0.9.3-models.scorer"
download_file(model_url, model_local_path)
download_file(scorer_url, scorer_local_path)

# Load DeepSpeech model
model = Model(model_local_path)
model.enableExternalScorer(scorer_local_path)

# WebRTC configuration
RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})

def app_speech_to_text():
    st.header("Real-Time Speech-to-Text")

    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={"video": False, "audio": True},
        audio_receiver_size=1024,
    )

    status_indicator = st.empty()
    text_output = st.empty()
    stream = None
    sound_chunk = pydub.AudioSegment.empty()

    if webrtc_ctx.state.playing:
        status_indicator.write("Model loaded and listening...")
        while True:
            if webrtc_ctx.audio_receiver:
                if stream is None:
                    stream = model.createStream()

                try:
                    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
                except queue.Empty:
                    continue

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

if __name__ == "__main__":
    app_speech_to_text()
