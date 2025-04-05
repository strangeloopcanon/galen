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
    Version with minimal validation to avoid breaking existing queries.
    """
    print(f"The SQL query is: {sql_query}")
    try:
        # Connect to the databases
        conn, cursor = connect_sqlite()
        
        # Execute the query directly - don't try to validate or modify it
        cursor.execute(sql_query)
        
        # Fetch results
        rows_fetched = cursor.fetchall()
        
        # If we have results, create a DataFrame
        if rows_fetched:
            # Get column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]
            
            # Create DataFrame from results
            result_df = pd.DataFrame(rows_fetched, columns=column_names)
            
            # Print status for debugging
            print(f"Query successful: {len(rows_fetched)} rows returned with columns: {column_names}")
        else:
            # No results but query was valid
            print("Query executed successfully but returned no data.")
            result_df = None
        
        # Close the cursor
        cursor.close()
        return result_df
        
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def log_query_results(sql_query, result_df, log_filename):
    """
    Log the executed query and its results to a CSV file.
    """
    log_dir = os.path.dirname(log_filename)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_data = pd.DataFrame({'Query': [sql_query], 'Result': [result_df.to_string(index=False)]})
    log_data.to_csv(log_filename, mode='a', header=not os.path.exists(log_filename), index=False)

def main(sql_query, filepath = log_filename):
    """
    Process the SQL query: execute and log the results.
    Now always returns a DataFrame, whether the query succeeds or fails.
    """
    print(f"SQL query is: {sql_query}")
    
    # Basic validation
    if not sql_query or not isinstance(sql_query, str):
        print("Invalid query: empty or not a string")
        return pd.DataFrame({'Error': ['Invalid query provided'], 
                             'Details': ['Query must be a non-empty string']})
    
    # Format the query for better display
    formatted_query = sql_query.strip()
    
    # First try a test query to verify database connection
    try:
        test_conn, test_cursor = connect_sqlite()
        test_cursor.execute("SELECT 1")
        test_cursor.close()
        test_conn.close()
        print("Database connection test successful")
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return pd.DataFrame({'Error': ['Database connection failed'], 
                             'Details': [str(e)]})
    
    # Execute the user's query
    try:
        # Execute query
        result_df = execute_query(formatted_query)
        
        # If query executed but returned no results
        if result_df is None:
            # Try a direct query to see if it works
            try:
                conn, cursor = connect_sqlite()
                print(f"Trying direct database query: {formatted_query}")
                cursor.execute(formatted_query)
                rows = cursor.fetchall()
                
                if rows:
                    # We got results
                    cols = [desc[0] for desc in cursor.description]
                    result_df = pd.DataFrame(rows, columns=cols)
                    print(f"Direct query successful: {len(rows)} rows returned")
                else:
                    # No results from a valid query
                    print("Query returned no rows")
                    result_df = pd.DataFrame({'Message': ['Query executed successfully but returned no data'],
                                              'Query': [formatted_query]})
                
                cursor.close()
                conn.close()
            except Exception as direct_error:
                # Even direct query failed
                print(f"Direct query failed: {direct_error}")
                result_df = pd.DataFrame({'Error': ['SQL query execution failed'], 
                                          'Details': [str(direct_error)],
                                          'Query': [formatted_query]})
        
        # If we have a valid DataFrame, log it
        if isinstance(result_df, pd.DataFrame) and not "Error" in result_df.columns:
            try:
                log_query_results(formatted_query, result_df, filepath)
                print(f"Query results logged to {filepath}")
            except Exception as log_error:
                print(f"Warning: Failed to log query results: {log_error}")
        
        return result_df
    
    except Exception as e:
        # Catch-all error handler
        print(f"Error executing query: {e}")
        return pd.DataFrame({'Error': ['SQL execution error'], 
                             'Details': [str(e)],
                             'Query': [formatted_query]})

if __name__ == '__main__':
    sql_query = input("Please enter your SQL query: \n")
    result = main(sql_query)
    if isinstance(result, pd.DataFrame):
        print(result)
    else:
        print(result)
