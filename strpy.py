import streamlit as st
import pymssql
import pandas as pd
from io import BytesIO

st.title('SQL Query Result to Excel Export')

# User inputs
server = st.text_input('Enter SQL Server Name:', '')
database = st.text_input('Enter Database Name:', '')
query = st.text_area('Enter SQL Query:', '')

def fetch_data(server, database, query):
    try:
        # Establish connection to the database using pymssql (Windows Authentication)
        conn = pymssql.connect(server=server, database=database)  # No need for username/password for Windows Auth
        cursor = conn.cursor()
        
        # Execute the query
        cursor.execute(query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        # Convert rows to DataFrame
        df = pd.DataFrame(rows, columns=columns)
        return df
    except pymssql.Error as e:
        st.error(f"Database error occurred: {e}")
        return None
    except Exception as ex:
        st.error(f"An unexpected error occurred: {ex}")
        return None
    finally:
        # Ensure resources are released
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

# Run query when the user presses the 'Run Query' button
if st.button('Run Query'):
    if server and database and query:
        df = fetch_data(server, database, query)
        
        if df is not None and not df.empty:
            st.write("Query executed successfully. Here are the top 5 results:")
            st.dataframe(df.head(5))  # Display top 5 rows

            # Save the data to an Excel file
            excel_file = BytesIO()
            with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Query Results')
            excel_file.seek(0)

            # Create a download button for the Excel file
            st.download_button(
                label="Download Excel file",
                data=excel_file,
                file_name="query_results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("No data returned from the query.")
    else:
        st.warning("Please enter all the required details (Server, Database, Query).")
