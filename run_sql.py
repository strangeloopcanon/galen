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
    try:
        conn, cursor = connect_sqlite()
        cursor.execute(sql_query)
        rows_fetched = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        result_df = pd.DataFrame(rows_fetched, columns=column_names)
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
    Process the SQL query: validate, execute, and log the results.
    """
    print(f"SQL query is: {sql_query}")
    result_df = execute_query(sql_query)
    print(f"Results df is: {result_df}")
    if result_df is not None:
        log_query_results(sql_query, result_df, filepath)
        return result_df
    else:
        return "Failed to execute the query."

if __name__ == '__main__':
    sql_query = input("Please enter your SQL query: \n")
    result = main(sql_query)
    if isinstance(result, pd.DataFrame):
        print(result)
    else:
        print(result)
