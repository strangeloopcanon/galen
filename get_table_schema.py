"""
To get the schemas
"""
import os
import glob
import sqlite3
import json
from sqlalchemy import create_engine, MetaData, Table, Column, String
import re
import logging

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)

def combine_schemas(db_files):
    combined_schema = {}

    for db_file in db_files:
        engine = create_engine('sqlite:///' + db_file)
        print(db_file)
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            metadata_obj = MetaData()
            
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()

            # Create a Table object to store schema info
            table_obj = Table(table_name, metadata_obj)

            for column in schema:
                col_name, col_type = column[1], column[2]
                # Add column to the table object
                table_obj.append_column(Column(col_name, String))

            # Serialize table schema
            schema_info = [{"column_name": col.name, "data_type": str(col.type)} for col in table_obj.columns]
            combined_schema[f"{table_name} in {db_file}"] = schema_info

        conn.close()

    return combined_schema

def save_schema_to_json(combined_schema, filename="config/combined_schema.json"):
    with open(filename, "w") as file:
        json.dump(combined_schema, file, indent=4)

# SQL check
def extract_sql(llm_response: str) -> str:
    # If the llm_response contains a markdown code block, with or without the sql tag, extract the sql from it
    print(f"The original llm response is: {llm_response}")
    sql = re.search(r"```sql\n(.*)```", llm_response, re.DOTALL)
    print(f"The SQL query that's extracted is: {sql}")
    if sql:
        log.info(f"Output from LLM: {llm_response} \nExtracted SQL: {sql.group(1)}")
        return sql.group(1)

    sql = re.search(r"```(.*)```", llm_response, re.DOTALL)
    if sql:
        log.info(f"Output from LLM: {llm_response} \nExtracted SQL: {sql.group(1)}")
        return sql.group(1)

    return llm_response

def is_sql_valid(sql: str) -> bool:
    # This is a check to see the SQL is valid and should be run
    # This simple function just checks if the SQL contains a SELECT statement

    if "SELECT" in sql.upper():
        return True
    else:
        return False

if __name__ == '__main__':
    db_directory = "db/"
    db_files = glob.glob(os.path.join(db_directory, "*.db"))
    # db_files = ["db/DepExprDB.db"]
    all_schemas = combine_schemas(db_files)
    save_schema_to_json(all_schemas)
    # Now the schema is saved in 'combined_schema.json'