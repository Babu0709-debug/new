import os
import pandas as pd
import streamlit as st
from pandasai import Agent
from pandasai.helpers.cache import Cache
from streamlit_mic_recorder import speech_to_text

# Set the API key
PANDASAI_API_KEY = "$2a$10$PBlknZ8TbfB9QGzjvEU1g.Z5Nw9p4ldw2w4vSc/VJismDrVrO9X7G"
os.environ["PANDASAI_API_KEY"] = PANDASAI_API_KEY

# Function to initialize PandasAI Agent
def initialize_agent(data_file):
    # Load the data
    data = pd.read_excel(data_file)
    
    # Clear the existing cache
    Cache().clear()
    
    # Create the PandasAI Agent
    agent = Agent(data)
    
    return agent

# Streamlit app
def main():
    st.title('Data Analysis with Speech Input')
    
    # File upload and initialization
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file)
        
        # Initialize PandasAI Agent with uploaded data
        agent = initialize_agent(uploaded_file)
        
        try:
            # Speech to text input
            query = speech_to_text(language='en')
            
            # Perform query with PandasAI Agent
            result = agent.chat(query)
            
            # Display result
            st.write("User Query:", query)
            st.write("PandasAI Response:", result)
        
        except Exception as e:
            st.error(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
