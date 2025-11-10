"""Verify database is accessible and show exact location for DB Browser"""
import sqlite3
import os

# Get database path (same as app.py)
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database', 'predictions.db')

print("="*80)
print("Database Verification for DB Browser")
print("="*80)
print(f"\nEXACT DATABASE FILE LOCATION:")
print(f"{db_path}")
print(f"\nCopy this path and open it in DB Browser for SQLite")
print("-"*80)

if not os.path.exists(db_path):
    print("\n[ERROR] Database file not found at the above location!")
    exit(1)

try:
    conn = sqlite3.connect(db_path, timeout=10.0)
    cursor = conn.cursor()
    
    # Check table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
    if not cursor.fetchone():
        print("\n[ERROR] Table 'predictions' does not exist!")
        conn.close()
        exit(1)
    
    # Count records
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    print(f"\nTotal Records in Database: {total}")
    
    if total > 0:
        # Get sample data
        cursor.execute("SELECT * FROM predictions LIMIT 3")
        rows = cursor.fetchall()
        print("\nSample Data (First 3 records):")
        print("-"*80)
        for row in rows:
            print(f"ID: {row[0]}, Temp: {row[1]}, Humidity: {row[2]}, Rainfall: {row[5]}, Time: {row[6]}")
        
        print("\n" + "="*80)
        print("INSTRUCTIONS FOR DB BROWSER:")
        print("="*80)
        print("1. Open DB Browser for SQLite")
        print("2. Click 'Open Database'")
        print("3. Navigate to or paste this exact path:")
        print(f"   {db_path}")
        print("4. Click on 'Browse Data' tab")
        print("5. Select table: 'predictions'")
        print("6. You should see", total, "records")
        print("\nIf data doesn't show:")
        print("- Make sure Flask app is NOT running (close it first)")
        print("- Click 'Refresh' button in DB Browser")
        print("- Try closing and reopening the database file")
    else:
        print("\nDatabase is empty. Make a prediction first.")
    
    conn.close()
    print("\n" + "="*80)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    exit(1)

