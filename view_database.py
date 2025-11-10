"""View database contents - Simple SQLite viewer"""
import sqlite3
import os
from datetime import datetime

# Get database path
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'database', 'predictions.db')

print("="*80)
print("RainRadar Database Viewer")
print("="*80)
print(f"\nDatabase Location: {db_path}")
print(f"Database Exists: {os.path.exists(db_path)}")
print("-"*80)

if not os.path.exists(db_path):
    print("\n[ERROR] Database file not found!")
    print("Make sure you've made at least one prediction.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
    if not cursor.fetchone():
        print("\n[ERROR] Table 'predictions' does not exist!")
        conn.close()
        exit(1)
    
    # Count total records
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]
    print(f"\nTotal Predictions: {total}")
    
    if total == 0:
        print("\nDatabase is empty. Make a prediction to see data here.")
    else:
        # Get all predictions
        cursor.execute('''
            SELECT id, temperature, humidity, wind_speed, pressure, 
                   predicted_rainfall, timestamp
            FROM predictions
            ORDER BY timestamp DESC
        ''')
        
        rows = cursor.fetchall()
        
        print("\n" + "="*80)
        print("All Predictions (Most Recent First)")
        print("="*80)
        print(f"{'ID':<5} {'Temp':<8} {'Humidity':<10} {'Wind':<8} {'Pressure':<10} {'Rainfall':<12} {'Timestamp':<20}")
        print("-"*80)
        
        for row in rows:
            print(f"{row[0]:<5} {row[1]:<8.1f} {row[2]:<10.1f} {row[3]:<8.1f} {row[4]:<10.1f} {row[5]:<12.2f} {row[6]:<20}")
        
        # Statistics
        cursor.execute("SELECT AVG(predicted_rainfall), MIN(predicted_rainfall), MAX(predicted_rainfall) FROM predictions")
        stats = cursor.fetchone()
        
        print("\n" + "="*80)
        print("Statistics")
        print("="*80)
        print(f"Average Rainfall: {stats[0]:.2f} mm")
        print(f"Minimum Rainfall: {stats[1]:.2f} mm")
        print(f"Maximum Rainfall: {stats[2]:.2f} mm")
    
    conn.close()
    print("\n" + "="*80)
    print(f"Database file location: {db_path}")
    print("You can open this file with any SQLite viewer (DB Browser, SQLiteStudio, etc.)")
    print("="*80)
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    exit(1)

