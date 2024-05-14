import os
import json
import inspect
import pandas as pd

def read_json(file_path):
    """Read JSON file from the given path and return the data."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_schema_and_table_list(folder_path):
    """Get the schema for all the tables and the table list."""
    schema_file_path = os.path.join(folder_path, 'combined_schema.json')
    all_schema = read_json(schema_file_path)

    tables_list = []
    for row in all_schema:
        for key in row:
            tables_list.append(key)

    return all_schema, tables_list

def extract_SQL(query):
    """Run SQL code."""
    from run_sql import main
    if isinstance(query, list):
        query = query[0]  # Convert list to string if needed
    df = main(query)  # (query, log_path)
    print(f"extract_SQL: Type of df returned: {type(df)}")
    print(f"extract_SQL: Content of df returned:\n{df}")

    df = main(query)  # (query, log_path)
    return df

def visualise(df):
    """Visualise the dataframe."""
    from run_visualise import visualize
    chart = visualize(df)
    return chart

def execute_function_call(response):
    # Determine the caller file
    stack = inspect.stack()
    caller_file = stack[1].filename
    
    # Debugging: Print the caller file
    print("Called from:", caller_file)

    # Process based on the caller
    if 'process_openai.py' in caller_file:
        # Handle the response structure for process_openai.py
        try:
            tool_call = response.choices[0].message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
        except AttributeError as e:
            print("Error accessing tool_calls:", e)
            print("Response structure:", response)
            return None

        if function_name == "extract_SQL":
            query = arguments["query"]
            result = extract_SQL(query)
        elif function_name == "visualise":
            code = arguments["vis_code"]
            result = visualise(code)
        else:
            result = f"Error: function {function_name} does not exist"
    
    elif 'process_groq.py' in caller_file:
        # Directly handle the SQL extraction and visualization for process_groq.py
        try:
            sql_query = response
            result = extract_SQL(sql_query)
            if result is not None:
                result = visualise(result)
        except (AttributeError, KeyError) as e:
            print("Error processing response:", e)
            print("Response structure:", response)
            return None
    
    else:
        print("Unknown caller file")
        return None
    
    return result
