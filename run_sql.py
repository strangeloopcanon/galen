import os
import pandas as pd
import json
from db_connection import connect_sqlite

log_filename = 'logs/query_log.csv'

def read_json(file_path):
    """
    Read JSON file from the given path and return the data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def execute_query(sql_query):
    """
    Execute a provided SQL query using the SQLite connection and return the results as a DataFrame.
    """
    print(f"The SQL query is: {sql_query}")
    try:
        # Connect to the databases
        conn, cursor = connect_sqlite()
        
        # Execute the query
        cursor.execute(sql_query)
        
        # Fetch results
        rows_fetched = cursor.fetchall()
        
        # If we have results, create a DataFrame
        if rows_fetched:
            # Get column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]
            
            # Create DataFrame from results
            result_df = pd.DataFrame(rows_fetched, columns=column_names)
            
            # Convert numeric columns to float for consistent handling
            for col in result_df.columns:
                # Try to convert columns to numeric if they contain numeric values
                try:
                    result_df[col] = pd.to_numeric(result_df[col])
                except:
                    pass  # Keep as is if conversion fails
            
            # Print status for debugging
            print(f"Query successful: {len(rows_fetched)} rows returned with columns: {column_names}")
        else:
            # No results but query was valid
            print("Query executed successfully but returned no data.")
            result_df = pd.DataFrame()
        
        # Close the cursor
        cursor.close()
        return result_df
        
    except Exception as e:
        print(f"Error executing query: {e}")
        # Reraise the exception to propagate the error
        raise

def log_query_results(sql_query, result_df, log_filename):
    """
    Log the executed query and its results to a CSV file.
    """
    try:
        log_dir = os.path.dirname(log_filename)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_data = pd.DataFrame({'Query': [sql_query], 'Result': [result_df.to_string(index=False)]})
        log_data.to_csv(log_filename, mode='a', header=not os.path.exists(log_filename), index=False)
        print(f"Query results logged to {log_filename}")
    except Exception as e:
        print(f"Warning: Failed to log query results: {e}")

def main(sql_query, filepath = log_filename):
    """
    Process the SQL query: execute and log the results.
    Returns a DataFrame or raises an exception.
    """
    print(f"SQL query is: {sql_query}")
    
    # Basic validation
    if not sql_query or not isinstance(sql_query, str):
        raise ValueError("Invalid query: empty or not a string")
    
    # Execute the query
    result_df = execute_query(sql_query)
    
    # Log the results if we have a valid DataFrame
    if result_df is not None and not result_df.empty:
        try:
            log_query_results(sql_query, result_df, filepath)
        except Exception as log_error:
            print(f"Warning: Failed to log query results: {log_error}")
    
    return result_df

if __name__ == '__main__':
    sql_query = input("Please enter your SQL query: \n")
    try:
        result = main(sql_query)
        print(result)
    except Exception as e:
        print(f"Error: {e}")