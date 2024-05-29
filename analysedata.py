import streamlit as st
import pyaudio
import speech_recognition as sr

def recognize_speech_from_microphone():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        st.write("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        st.write("Listening...")
        audio = recognizer.listen(source)

    try:
        st.write("Recognizing speech...")
        text = recognizer.recognize_google(audio)
        st.write("You said: " + text)
    except sr.UnknownValueError:
        st.write("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        st.write("Could not request results from Google Speech Recognition service; {0}".format(e))

def main():
    st.title("Speech-to-Text App")
    st.write("Click the button below and start speaking")
    if st.button("Start Recording"):
        recognize_speech_from_microphone()

if __name__ == "__main__":
    main()
