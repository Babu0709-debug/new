import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text
import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

def main():
    st.title("Microphone Access Demo")
    st.write("Click the button below to start recording from your microphone.")

    webrtc_ctx = webrtc_streamer(
        key="microphone",
        mode=WebRtcMode.SENDRECV,  # Use WebRtcMode for microphone access
        audio_processor_factory=AudioProcessorBase,
        async_processing=True,
    )

if __name__ == "__main__":
    main()

st.write(speech_to_text(language='en'))
