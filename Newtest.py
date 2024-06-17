import streamlit as st
import pandas as pd
import os
from pandasai import Agent
from pandasai import SmartDataframe

# Set the API key
PANDASAI_API_KEY = "$2a$10$PBlknZ8TbfB9QGzjvEU1g.Z5Nw9p4ldw2w4vSc/VJismDrVrO9X7G"
os.environ["PANDASAI_API_KEY"] = PANDASAI_API_KEY

st.title("Data Analysis with pandasai SmartDataframe")

# Create a sample dataframe
df = pd.DataFrame({
    "country": [
        "United States", "United Kingdom", "France", "Germany", "Italy", "Spain", "Canada", "Australia", "Japan", "China"],
    "gdp": [
        19294482071552, 2891615567872, 2411255037952, 3435817336832, 1745433788416, 1181205135360, 1607402389504, 1490967855104, 4380756541440, 14631844184064
    ],
})

df = SmartDataframe(df)
st.dataframe(df)

# Query input
query = st.text_input("Enter your query", "Which are the countries with GDP greater than 3000000000000?")

if query:
    try:
        agent = Agent(df)
        result = df.chat(query)
        st.write(f"Query: {query}")
        st.write("Result:")
        st.write(result)
    except Exception as e:
        st.write(f"Error: {e}")
