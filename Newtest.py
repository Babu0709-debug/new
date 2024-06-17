import streamlit as st
import pandas as pd
import os
from streamlit_mic_recorder import mic_recorder, speech_to_text
from pandasai import Agent
from pandasai import SmartDataframe
import speech_recognition as sr

# Set the API key
PANDASAI_API_KEY = "$2a$10$PBlknZ8TbfB9QGzjvEU1g.Z5Nw9p4ldw2w4vSc/VJismDrVrO9X7G"
os.environ["PANDASAI_API_KEY"] = PANDASAI_API_KEY

st.title("Data Analysis with Speech Input")

uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        file_extension = uploaded_file.name.split('.')[-1].lower()

        if file_extension == 'csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['xlsx', 'xls']:
            df = pd.read_excel(uploaded_file)
        else:
            st.write("Unsupported file format")
        
        #df = SmartDataframe(data)
        st.dataframe(df.head())

        # Debug: Check the SmartDataframe initialization
        st.write(f"SmartDataframe type: {type(df)}")

        try:
            query = speech_to_text(language='en')
            if query:
                st.write(f"Recognized query: {query}")
                
                # Debug: Check the type and content of the recognized query
                st.write(f"Query type: {type(query)}")
                st.write(f"Query content: {query}")

                agent = Agent(df)
                
                # Debug: Check the Agent initialization
                st.write(f"Agent type: {type(agent)}")

                result = agent.chat(query)
                
                # Debug: Check the result returned from the agent
                st.write(f"Result type: {type(result)}")
                st.write(f"Result content: {result}")

                st.write(result)
            else:
                st.write("Could not recognize any speech. Please try again.")
        except Exception as e:
            st.write(f"Speech-to-text conversion failed: {e}")

    except Exception as e:
        st.write(f"Error processing the uploaded file: {e}")
else:
    st.write("Please upload a CSV or Excel file.")
