#!/usr/bin/env python3
import csv
import sqlite3
import sys
import os

def create_table_from_csv(db_name, csv_file):
    # Connect to SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Read CSV file
    with open(csv_file, 'r') as f:
        csv_reader = csv.reader(f)
        # Get headers
        headers = next(csv_reader)
        
        # Create table name from CSV filename (remove extension)
        table_name = os.path.splitext(os.path.basename(csv_file))[0]
        
        # Create SQL for table creation
        columns = [f'"{header}" TEXT' for header in headers]
        create_table_sql = f'CREATE TABLE {table_name} ({", ".join(columns)})'
        
        # Create table
        cursor.execute(create_table_sql)
        
        # Insert data
        insert_sql = f'INSERT INTO {table_name} VALUES ({",".join(["?" for _ in headers])})'
        cursor.executemany(insert_sql, csv_reader)
        
        # Commit changes and close connection
        conn.commit()
        conn.close()

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 csv_to_sqlite.py <database_name> <csv_file>")
        sys.exit(1)
        
    db_name = sys.argv[1]
    csv_file = sys.argv[2]
    
    try:
        create_table_from_csv(db_name, csv_file)
        print(f"Successfully created table from {csv_file} in {db_name}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
