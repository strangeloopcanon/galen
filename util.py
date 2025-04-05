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
    """Extract SQL from a query or run one directly."""
    from run_sql import main
    
    # Debugging 
    print(f"extract_SQL: Input query type: {type(query)}")
    if isinstance(query, list) and query:
        print(f"extract_SQL: Query list content: {query}")
    elif isinstance(query, str):
        print(f"extract_SQL: Query string content: {query[:100]}")
    else:
        print(f"extract_SQL: Query is {query}")
    
    # Handle list input - convert to string
    if isinstance(query, list):
        if not query:  # Empty list
            return "Empty query list provided"
        query = query[0]  # Convert list to string if needed
    
    # Check if query is SQL or not
    if not query.strip().upper().startswith("SELECT"):
        # This is a natural language query - forward to process_openai
        print(f"extract_SQL: Query is not SQL, forwarding to process_openai: {query}")
        from process_openai import main as process_query
        return process_query([{'role': 'user', 'content': query}])
    
    # For SQL queries
    print(f"extract_SQL: Executing SQL query: {query}")
    try:
        df = main(query)
        
        # Print debug information
        print(f"extract_SQL: Type of df returned: {type(df)}")
        if isinstance(df, pd.DataFrame):
            print(f"extract_SQL: DataFrame shape: {df.shape}")
            print(f"extract_SQL: DataFrame head:\n{df.head()}")
        else:
            print(f"extract_SQL: Non-DataFrame result: {df}")
        
        return df
        
    except Exception as e:
        print(f"extract_SQL ERROR: SQL query execution failed: {e}")
        
        # Check if it's a table name issue in the query
        error_str = str(e).lower()
        if "no such table" in error_str:
            # Extract the incorrect table name
            import re
            match = re.search(r"no such table:\s*(\w+)", error_str)
            if match:
                bad_table = match.group(1)
                print(f"extract_SQL: Detected invalid table name: {bad_table}")
                
                # Fix the query by replacing the bad table with the appropriate one
                if "gene" in bad_table or "dependency" in bad_table:
                    fixed_query = query.replace(bad_table, "DepMap")
                    print(f"extract_SQL: Fixed query: {fixed_query}")
                    
                    # Try again with the fixed query
                    try:
                        print("extract_SQL: Retrying with fixed query...")
                        df = main(fixed_query)
                        if isinstance(df, pd.DataFrame):
                            print(f"extract_SQL: Query successful after fixing table name! Shape: {df.shape}")
                            return df
                    except Exception as retry_error:
                        print(f"extract_SQL: Retry failed: {retry_error}")
        
        # If we get here, all attempts have failed
        raise

def visualise(df):
    """
    Simple wrapper for the visualization function.
    Will always try to return a matplotlib figure.
    """
    try:
        # Call the visualize function from run_visualise module
        from run_visualise import visualize
        
        # Print debug info
        print(f"visualise: Calling visualization with dataframe of type: {type(df)}")
        if isinstance(df, pd.DataFrame):
            print(f"visualise: DataFrame shape: {df.shape}")
        
        # Pass the dataframe to visualize and return the result
        return visualize(df)
    except Exception as e:
        # If visualization fails for any reason, create a simple message figure
        print(f"Visualization error in util.py: {e}")
        
        try:
            # Create a basic figure with error message
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, "Visualization Error", fontsize=16, ha='center', va='center')
            ax.text(0.5, 0.4, str(e), fontsize=12, ha='center', va='center', wrap=True)
            ax.axis('off')
            return fig
        except:
            # If even that fails, return None and let the caller handle it
            return None

def execute_function_call(response):
    """Execute function calls from LLM responses."""
    # Determine the caller file
    stack = inspect.stack()
    caller_file = stack[1].filename
    
    # Debugging: Print the caller file
    print("Called from:", caller_file)

    # Process based on the caller
    if 'process_openai.py' in caller_file:
        # Handle the response structure for process_openai.py
        try:
            # Check if there are any tool calls
            if not hasattr(response.choices[0].message, 'tool_calls') or not response.choices[0].message.tool_calls:
                print("No tool calls in the response")
                return None
                
            # Get the first tool call
            tool_call = response.choices[0].message.tool_calls[0]
            
            # Print tool call ID for tracking
            print(f"Processing tool call ID: {tool_call.id}")
            
            # Extract function name and arguments
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
        except (AttributeError, json.JSONDecodeError) as e:
            print("Error processing tool_calls:", e)
            print("Response structure:", response)
            return None

        # Execute the appropriate function based on name
        if function_name == "extract_SQL":
            query = arguments["query"]
            result = extract_SQL(query)
        elif function_name == "visualise":
            code = arguments["vis_code"]
            result = visualise(code)
        elif function_name == "data_analysis":
            code = arguments["code"]
            # Call appropriate function for data analysis
            # This would need to be implemented
            result = f"Data analysis function executed with code: {code[:50]}..."
        elif function_name == "write_report":
            report_request = arguments["report_request"]
            # Call appropriate function for report writing
            # This would need to be implemented
            result = f"Report writing function executed with request: {report_request[:50]}..."
        elif function_name == "qna":
            question = arguments["question"]
            # Call appropriate function for QnA
            # This would need to be implemented
            result = f"QnA function executed with question: {question[:50]}..."
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
        # For other callers, attempt to handle in a reasonable way
        print(f"Warning: Called from unexpected file: {caller_file}")
        try:
            # Try to handle as OpenAI response if it has the right structure
            if hasattr(response, 'choices') and hasattr(response.choices[0].message, 'tool_calls'):
                tool_call = response.choices[0].message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                if function_name == "extract_SQL":
                    query = arguments["query"]
                    result = extract_SQL(query)
                else:
                    result = None
            else:
                # Just try to run it as SQL
                result = extract_SQL(response)
        except Exception as e:
            print(f"Error handling response from unknown caller: {e}")
            result = None
    
    return result