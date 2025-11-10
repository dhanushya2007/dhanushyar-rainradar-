"""Check database in extracted project"""
import sqlite3
import os

db_path = 'database/predictions.db'
abs_path = os.path.abspath(db_path)

print("="*80)
print("Checking Extracted Database")
print("="*80)
print(f"\nDatabase path: {abs_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    print(f"\nTotal records: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM predictions ORDER BY id")
        rows = cursor.fetchall()
        print("\nAll records in database:")
        print("-"*80)
        for row in rows:
            print(f"ID: {row[0]}")
            print(f"  Temperature: {row[1]}°C")
            print(f"  Humidity: {row[2]}%")
            print(f"  Wind Speed: {row[3]} km/h")
            print(f"  Pressure: {row[4]} hPa")
            print(f"  Predicted Rainfall: {row[5]:.2f} mm")
            print(f"  Timestamp: {row[6]}")
            print("-"*80)
    
    conn.close()
else:
    print("\nDatabase file not found!")

