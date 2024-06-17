import os
import pandas as pd
import streamlit as st
from pandasai import Agent
from pandasai.helpers.cache import Cache
from streamlit_mic_recorder import mic_recorder, speech_to_text

# Set the API key
PANDASAI_API_KEY = "$2a$10$PBlknZ8TbfB9QGzjvEU1g.Z5Nw9p4ldw2w4vSc/VJismDrVrO9X7G"
os.environ["PANDASAI_API_KEY"] = PANDASAI_API_KEY

# Function to generate a dummy DataFrame
def generate_dummy_data():
    data = {
        'State': ['California', 'Texas', 'New York', 'Florida', 'Illinois', 'Pennsylvania', 'Ohio', 'Georgia', 'North Carolina', 'Michigan'],
        'Sales': [15000, 12000, 18000, 9000, 13500, 11000, 9500, 14500, 13000, 12500]
    }
    df = pd.DataFrame(data)
    return df

# Function to initialize PandasAI Agent
def initialize_agent(data):
    # Clear the existing cache
    Cache().clear()
    
    # Create the PandasAI Agent
    agent = Agent(data)
    
    return agent

# Streamlit app
def main():
    st.title('Data Analysis with Speech Input')
    
    # Generate dummy DataFrame
    dummy_data = generate_dummy_data()
    
    # Initialize PandasAI Agent with dummy data
    agent = initialize_agent(dummy_data)
    
    try:
        # Speech to text input
        query = speech_to_text(language='en')
        
        if query:
            # Perform query with PandasAI Agent
            result = agent.chat(query)
            
            # Display result
            st.write("User Query:", query)
            st.write("PandasAI Response:")
            st.write(result)  # Display the result from PandasAI
        else:
            st.warning("No speech input detected. Please try again.")
    
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
