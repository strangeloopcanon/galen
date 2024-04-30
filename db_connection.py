import os
import sqlite3
import glob

def connect_sqlite():
    """
    Connect to a primary database and attach additional databases found in the directory.
    Returns the connection and cursor of the primary database, with other databases attached.
    """
    db_directory = "db/"
    db_files = glob.glob(os.path.join(db_directory, "*.db"))
    
    if not db_files:
        raise Exception("No database files found in the directory.")
    # Connect to an in-memory database as primary
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Attach other databases
    for db_file in db_files[0:]:  # Skip the first file as it's already the primary
        db_name = os.path.splitext(os.path.basename(db_file))[0]  # Get the base name without extension
        print(f"ATTACH DATABASE '{db_file}' AS {db_name}")
        cursor.execute(f"ATTACH DATABASE '{db_file}' AS {db_name}")

    return conn, cursor

if __name__ == "__main__":
    conn, cursor = connect_sqlite()
    conn.close()
