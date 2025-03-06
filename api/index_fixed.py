from flask import Flask, request, jsonify
import re
import sqlite3
import os
import csv

app = Flask(__name__)

# Create in-memory database from CSV files
def create_in_memory_db():
    try:
        # Get the directory containing the CSV files
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f'Base directory: {base_dir}')
        
        # Create an in-memory database
        conn = sqlite3.connect(':memory:')
        print('Created in-memory database')
        
        # Convert both CSV files to SQLite
        csv_files = ['zip_county.csv', 'county_health_rankings.csv']
        for csv_file in csv_files:
            csv_path = os.path.join(base_dir, csv_file)
            print(f'Processing {csv_file}...')
            
            # Check if file exists
            if not os.path.exists(csv_path):
                error_msg = f'Required CSV file not found: {csv_path}'
                print(f'Error: {error_msg}')
                raise FileNotFoundError(error_msg)
            
            # Read and process the CSV file
            with open(csv_path, 'r') as f:
                csv_reader = csv.reader(f)
                headers = next(csv_reader)
                print(f'Found {len(headers)} columns in {csv_file}')
                
                # Create table name from CSV filename (remove extension)
                table_name = os.path.splitext(os.path.basename(csv_file))[0]
                
                # Create SQL for table creation
                columns = [f'"{header}" TEXT' for header in headers]
                create_table_sql = f'CREATE TABLE {table_name} ({", ".join(columns)})'
                
                # Create table
                conn.execute(create_table_sql)
                print(f'Created table {table_name}')
                
                # Insert data
                insert_sql = f'INSERT INTO {table_name} VALUES ({",".join(["?" for _ in headers])})'
                conn.executemany(insert_sql, csv_reader)
                conn.commit()
                
                # Verify data
                cursor = conn.cursor()
                cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
                count = cursor.fetchone()[0]
                print(f'Successfully loaded {count} rows into {table_name}')
        
        # Final verification of tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f'Tables in database: {[t[0] for t in tables]}')
        
        return conn
    except Exception as e:
        print(f'Error creating in-memory database: {str(e)}')
        raise

VALID_MEASURES = [
    'Violent crime rate',
    'Unemployment',
    'Children in poverty',
    'Diabetic screening',
    'Mammography screening',
    'Preventable hospital stays',
    'Uninsured',
    'Sexually transmitted infections',
    'Physical inactivity',
    'Adult obesity',
    'Premature Death',
    'Daily fine particulate matter'
]

def get_county_data(zip_code, measure_name, conn):
    try:
        cursor = conn.cursor()
        
        # First check if the zip code exists
        cursor.execute('SELECT COUNT(*) FROM zip_county WHERE "﻿zip" = ?', (zip_code,))
        zip_count = cursor.fetchone()[0]
        print(f'Found {zip_count} entries for ZIP code {zip_code}')
        if zip_count == 0:
            return None
            
        # Then check if the measure exists for any county
        cursor.execute('SELECT COUNT(*) FROM county_health_rankings WHERE Measure_name = ?', (measure_name,))
        measure_count = cursor.fetchone()[0]
        print(f'Found {measure_count} entries for measure {measure_name}')
        if measure_count == 0:
            return None
    
        # Get the county health data
        cursor.execute("""
            SELECT zc.county, zc.county_state, zc.state_abbreviation, chr.*
            FROM zip_county zc
            JOIN county_health_rankings chr
            ON chr.County = zc.county
            AND chr.State = zc.state_abbreviation
            WHERE "﻿zip" = ?
            AND chr.Measure_name = ?
            ORDER BY chr.Year_span
        """, (zip_code, measure_name))
        
        columns = [desc[0].lower() for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        print(f'Query returned {len(results)} results')
        
        return results if results else None
        
    except sqlite3.Error as e:
        print(f'Database error: {str(e)}')
        raise

@app.route('/')
def home():
    return jsonify({'message': 'County Health Data API. Use /county_data endpoint with POST requests.'})

@app.route('/county_data', methods=['POST'])
def county_data():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400
        
    data = request.get_json()
    print(f'Received request: {data}')
    
    # Check for teapot easter egg
    if data.get('coffee') == 'teapot':
        return '', 418
    
    # Validate required fields
    zip_code = data.get('zip')
    measure_name = data.get('measure_name')
    
    if not zip_code or not measure_name:
        return jsonify({'error': 'Both zip and measure_name are required'}), 400
        
    # Validate zip code format
    if not re.match(r'^\d{5}$', zip_code):
        return jsonify({'error': 'ZIP code must be 5 digits'}), 400
        
    # Validate measure name
    if measure_name not in VALID_MEASURES:
        return jsonify({'error': 'Invalid measure_name'}), 400
    
    try:
        # Create database and load data
        conn = create_in_memory_db()
        print(f'Successfully created database')
        
        # Get the data
        results = get_county_data(zip_code, measure_name, conn)
        
        # Close the connection
        conn.close()
        
        if not results:
            print(f'No data found for zip={zip_code}, measure={measure_name}')
            return jsonify({'error': 'No data found for the given zip and measure_name'}), 404
            
        print(f'Returning {len(results)} results')
        return jsonify(results)
        
    except FileNotFoundError as e:
        print(f'Database file not found: {str(e)}')
        return jsonify({'error': 'Database configuration error'}), 500
    except sqlite3.Error as e:
        print(f'Database error: {str(e)}')
        return jsonify({'error': 'Database error'}), 500
    except Exception as e:
        print(f'Error processing request: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
