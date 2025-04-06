import os
import pandas as pd
from openai import OpenAI
import streamlit as st
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from util import read_json, get_schema_and_table_list, execute_function_call, visualise, extract_SQL

# Load environment variables from .env file
load_dotenv()

dirname = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(dirname, 'config')
log_path = os.path.join(dirname, 'logs')

# Initialize schema and info
final_schema, tables = get_schema_and_table_list(config_path)
info = read_json(os.path.join(config_path, 'info.json'))

def main():
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        st.error("OpenAI API key is not set. Please set it in the .env file.")
        st.info("For testing purposes, you can enter a temporary API key below:")
        temp_api_key = st.text_input("OpenAI API Key", type="password")
        if temp_api_key:
            os.environ['OPENAI_API_KEY'] = temp_api_key
            openai_api_key = temp_api_key
        else:
            return

    openai_client = OpenAI(api_key=openai_api_key)

    INSTRUCTION = info.get('DB_instructions')
    GPT_MODEL = info.get('GPT_MODEL')
    VISUAL_INSTRUCTIONS = info.get('Visual_Builder')

    st.title("Galen: Data Analysis for Oncology")

    # Checkboxes for various functionalities
    run_queries = st.checkbox("Run DB queries", value=False)
    ask_research_questions = st.checkbox("Ask questions of your research papers", value=False)
    run_evaluation = st.checkbox("Run an evaluation", value=False)

    # Depending on which checkbox is checked, display corresponding input fields and outputs
    if run_queries:
        col1, col2 = st.columns(2)
        with col1:  # Input column for DB queries
            user_text_query = st.text_input("What are you curious about in the data?", key="db_query")
            user_visual_type_query = st.text_input("How do you want to visualize the data?", key="visual_type")

        with col2:  # Output column for DB queries
            dataframe_placeholder = st.empty()
            visualization_placeholder = st.empty()

        if user_text_query and user_visual_type_query:
            user_prompt = [user_text_query]
            # Using modular extract_SQL and visualise functions
            df_returned = extract_SQL(user_prompt)
            if isinstance(df_returned, pd.DataFrame) and not df_returned.empty:
                dataframe_placeholder.write(df_returned)
                chart = visualise(df_returned)
                visualization_placeholder.pyplot(chart)
            else:
                st.error("No data returned or the data format is incorrect.")

    if ask_research_questions:
        # Input for research paper questions
        with st.container():
            user_research_question = st.text_input("What do you want to know from the research papers?", key="research_query")
            # Placeholder or logic to handle research paper questions goes here

    if run_evaluation:
        # Input for evaluation
        with st.container():
            user_evaluation_input = st.text_input("Please provide input for the evaluation:", key="evaluation_query")
            # Placeholder or logic to handle evaluation goes here

    # Buttons for user interaction
    if st.button("Ask another question"):
        st.experimental_rerun()
    elif st.button("Exit"):
        st.stop()

if __name__ == "__main__":
    main()
