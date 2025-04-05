import os
import pandas as pd
from db_connection import connect_sqlite

print("----------- DATABASE CONNECTION TEST -------------")
print(f"Current working directory: {os.getcwd()}")

try:
    print("Connecting to database...")
    conn, cursor = connect_sqlite()
    print("Connection successful!")
    
    # Test query 1 - list tables
    print("\nListing all tables:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables found: {tables}")
    
    # Test query 2 - protein links
    print("\nTesting protein_links query:")
    try:
        query = "SELECT protein1, COUNT(*) as frequency FROM protein_links GROUP BY protein1 ORDER BY frequency DESC LIMIT 5"
        print(f"Executing query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        print("Query successful!")
        print(df)
    except Exception as e:
        print(f"Protein links query failed: {e}")
    
    # Test query 3 - depmap
    print("\nTesting DepMap query:")
    try:
        query = "SELECT gene_name, COUNT(*) as count FROM DepMap GROUP BY gene_name ORDER BY count DESC LIMIT 5"
        print(f"Executing query: {query}")
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=cols)
        print("Query successful!")
        print(df)
    except Exception as e:
        print(f"DepMap query failed: {e}")
    
    # Close connection
    conn.close()
    print("\nConnection closed.")
    
except Exception as e:
    print(f"ERROR: {e}")

print("----------- TEST COMPLETE -------------")