"""Check database status and ensure it's accessible"""
import sqlite3
import os
import time

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database', 'predictions.db')

print("="*80)
print("Database Status Check")
print("="*80)
print(f"\nDatabase path: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    file_size = os.path.getsize(db_path)
    print(f"File size: {file_size} bytes")
    
    # Check for lock files
    wal_file = db_path + '-wal'
    shm_file = db_path + '-shm'
    print(f"\nWAL file exists: {os.path.exists(wal_file)}")
    print(f"SHM file exists: {os.path.exists(shm_file)}")
    
    try:
        # Try to connect with exclusive lock
        print("\nAttempting to connect to database...")
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        
        # Check journal mode
        cursor.execute('PRAGMA journal_mode')
        journal_mode = cursor.fetchone()[0]
        print(f"Journal mode: {journal_mode}")
        
        # Force checkpoint if WAL mode
        if journal_mode == 'wal':
            print("Database is in WAL mode. Running checkpoint...")
            cursor.execute('PRAGMA wal_checkpoint(TRUNCATE)')
            conn.commit()
        
        # Count records
        cursor.execute('SELECT COUNT(*) FROM predictions')
        count = cursor.fetchone()[0]
        print(f"\nTotal records in database: {count}")
        
        if count > 0:
            cursor.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT 5')
            rows = cursor.fetchall()
            print("\nLast 5 records:")
            print("-"*80)
            for row in rows:
                print(f"ID: {row[0]}, Temp: {row[1]}, Humidity: {row[2]}, Rainfall: {row[5]:.2f}mm, Time: {row[6]}")
        
        cursor.close()
        conn.close()
        print("\n[SUCCESS] Database connection closed successfully")
        print("\n" + "="*80)
        print("INSTRUCTIONS FOR DB BROWSER:")
        print("="*80)
        print("1. Make sure Flask app is STOPPED (close the terminal)")
        print("2. Open DB Browser for SQLite")
        print("3. Open this file:", db_path)
        print("4. Click 'Browse Data' tab")
        print("5. Select table: 'predictions'")
        print("6. You should see", count, "records")
        print("="*80)
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print("\n[ERROR] Database is locked!")
            print("The Flask app is likely still running.")
            print("\nSolution:")
            print("1. Stop the Flask app (close the terminal running 'python app.py')")
            print("2. Wait a few seconds")
            print("3. Run this script again")
        else:
            print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")
else:
    print("\n❌ Database file not found!")

