import streamlit as st
import speech_recognition as sr

def recognize_speech_from_microphone():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        st.write("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)
        st.write("Listening for your speech...")
        audio = recognizer.listen(source)

    try:
        st.write("Recognizing speech...")
        text = recognizer.recognize_google(audio)
        st.write(f"You said: {text}")
    except sr.UnknownValueError:
        st.write("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        st.write(f"Could not request results from Google Speech Recognition service; {e}")

def main():
    st.title("Speech to Text with Streamlit")
    st.write("Click the button and start speaking")

    if st.button("Start Recording"):
        recognize_speech_from_microphone()

if __name__ == "__main__":
    main()
