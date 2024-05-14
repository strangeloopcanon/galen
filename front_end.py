import os
from openai import OpenAI
import generate_visuals_from_prompt as rdq
import streamlit as st
import matplotlib
matplotlib.use('Agg')

dirname = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(dirname, 'config')
log_path = os.path.join(dirname, 'logs')

final_schema, tables = rdq.get_schema_and_table_list(config_path)
info = rdq.read_json(os.path.join(config_path, 'info.json'))

def extract_SQL(query):
    """run SQL code"""
    from temp1 import main
    df = main(query, log_path)
    print(df)
    return df

# results_df = extract_SQL(resp.sql[0])

def visualise(df):
    """visualise the dataframe"""
    from temp2 import visualize
    chart = visualize(df)
    print(chart)
    return chart

def main():
    openai_client_session = OpenAI(api_key=os.getenv('OPEN_AI_API_KEY'))

    INSTRUCTION = info.get('DB_instructions')
    GPT_MODEL = info.get('GPT_4')
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
            # df_returned = rdq.validate_the_query(openai_client_session, final_schema, tables, user_prompt, INSTRUCTION, GPT_MODEL, log_path)
            df_returned = extract_SQL(user_prompt)
            dataframe_placeholder.write(df_returned)
            # visualization_placeholder.write(rdq.generate_visual_from_df(openai_client_session, user_prompt, user_visual_type_query, VISUAL_INSTRUCTIONS, GPT_MODEL, df_returned))
            visualise(df_returned)

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
