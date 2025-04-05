import os
import sqlite3
import glob

def connect_sqlite():
    """
    Connect to a primary database and attach additional databases found in the directory.
    Returns the connection and cursor of the primary database, with other databases attached.
    """
    db_directory = "db/"
    
    # Absolute path check
    current_dir = os.getcwd()
    absolute_db_path = os.path.join(current_dir, db_directory)
    print(f"Looking for databases in: {absolute_db_path}")
    
    # Check if directory exists
    if not os.path.exists(absolute_db_path):
        print(f"ERROR: Database directory not found at {absolute_db_path}")
        
    # List all files in the directory
    try:
        all_files = os.listdir(absolute_db_path)
        print(f"All files in directory: {all_files}")
    except Exception as e:
        print(f"Error listing directory: {e}")
    
    # Use glob to find db files
    db_files = glob.glob(os.path.join(db_directory, "*.db"))
    print(f"Found {len(db_files)} database files: {db_files}")
    
    if not db_files:
        raise Exception(f"No database files found in {absolute_db_path}")
    
    # Connect to an in-memory database as primary
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Attach other databases
    for db_file in db_files:
        db_name = os.path.splitext(os.path.basename(db_file))[0]  # Get the base name without extension
        print(f"ATTACH DATABASE '{db_file}' AS {db_name}")
        try:
            cursor.execute(f"ATTACH DATABASE '{db_file}' AS {db_name}")
            print(f"Successfully attached {db_name}")
        except Exception as e:
            print(f"Error attaching {db_file}: {e}")

    # Verify databases are attached
    try:
        cursor.execute("PRAGMA database_list;")
        attached_dbs = cursor.fetchall()
        print(f"Attached databases: {attached_dbs}")
    except Exception as e:
        print(f"Error checking attached databases: {e}")

    return conn, cursor

if __name__ == "__main__":
    conn, cursor = connect_sqlite()
    conn.close()
