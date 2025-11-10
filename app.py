# """
# Flask Backend Application for RainRadar
# Handles routing, predictions, and database operations
# """

# from flask import Flask, render_template, request, jsonify, send_file
# import joblib
# import numpy as np
# import sqlite3
# import os
# from datetime import datetime
# import pandas as pd
# import json

# app = Flask(__name__)

# # Database configuration
# # Use absolute path to ensure database is always found
# base_dir = os.path.dirname(os.path.abspath(__file__))
# DB_PATH = os.path.join(base_dir, 'database', 'predictions.db')

# # Initialize database
# def init_db():
#     """Initialize the SQLite database"""
#     db_dir = 'database'
#     if not os.path.exists(db_dir):
#         os.makedirs(db_dir)
    
#     print(f"Database path: {DB_PATH}")
#     # Use timeout and check_same_thread=False for better compatibility
#     conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
#     cursor = conn.cursor()
    
#     # Set journal mode to DELETE for better compatibility with DB Browser
#     cursor.execute('PRAGMA journal_mode=DELETE')
    
#     cursor.execute('''
#         CREATE TABLE IF NOT EXISTS predictions (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             temperature REAL NOT NULL,
#             humidity REAL NOT NULL,
#             wind_speed REAL NOT NULL,
#             pressure REAL NOT NULL,
#             predicted_rainfall REAL NOT NULL,
#             timestamp TEXT NOT NULL
#         )
#     ''')
    
#     conn.commit()
#     conn.close()
#     print("Database initialized successfully!")

# # Load ML model
# def load_model():
#     """Load the trained ML model"""
#     # Get the base directory of the application
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     model_path = os.path.join(base_dir, 'model', 'rainfall_model.joblib')
    
#     if not os.path.exists(model_path):
#         raise FileNotFoundError(f"Model not found at {model_path}. Please run train_model.py first.")
    
#     try:
#         model = joblib.load(model_path)
#         print(f"Model loaded successfully from: {model_path}")
#         return model
#     except Exception as e:
#         print(f"Error loading model file: {e}")
#         raise

# # Initialize model
# model = None
# try:
#     model = load_model()
#     print("="*50)
#     print("Model initialized and ready for predictions!")
#     print("="*50)
# except FileNotFoundError as e:
#     print(f"\n{'='*50}")
#     print("WARNING: Model not found!")
#     print(f"{'='*50}")
#     print(f"Error: {e}")
#     print("\nTo fix this, run: python train_model.py")
#     print("="*50 + "\n")
#     model = None
# except Exception as e:
#     print(f"\n{'='*50}")
#     print("ERROR: Failed to load model!")
#     print(f"{'='*50}")
#     print(f"Error details: {e}")
#     print("\nPlease check:")
#     print("1. Model file exists: model/rainfall_model.joblib")
#     print("2. Dependencies are installed: pip install -r requirements.txt")
#     print("3. Try retraining: python train_model.py")
#     print("="*50 + "\n")
#     model = None

# # Routes
# @app.route('/')
# def index():
#     """Home page"""
#     return render_template('index.html')

# @app.route('/predict')
# def predict():
#     """Prediction page"""
#     return render_template('predict.html')

# @app.route('/history')
# def history():
#     """History page"""
#     return render_template('history.html')

# @app.route('/about')
# def about():
#     """About page"""
#     return render_template('about.html')

# @app.route('/results')
# def results():
#     """Results page"""
#     return render_template('results.html')

# @app.route('/api/predict', methods=['POST'])
# def api_predict():
#     """API endpoint for making predictions"""
#     global model
    
#     # Try to reload model if it's None but file exists
#     if model is None:
#         base_dir = os.path.dirname(os.path.abspath(__file__))
#         model_path = os.path.join(base_dir, 'model', 'rainfall_model.joblib')
#         if os.path.exists(model_path):
#             try:
#                 model = load_model()
#                 print("Model reloaded successfully!")
#             except Exception as e:
#                 print(f"Failed to reload model: {e}")
    
#     try:
#         if model is None:
#             return jsonify({
#                 'error': 'Model not loaded. Please train the model first by running: python train_model.py'
#             }), 500
        
#         # Get input data
#         data = request.get_json()
        
#         # Validate inputs
#         required_fields = ['temperature', 'humidity', 'wind_speed', 'pressure', 'past_rainfall']
#         for field in required_fields:
#             if field not in data:
#                 return jsonify({'error': f'Missing required field: {field}'}), 400
        
#         # Extract features
#         temperature = float(data['temperature'])
#         humidity = float(data['humidity'])
#         wind_speed = float(data['wind_speed'])
#         pressure = float(data['pressure'])
#         past_rainfall = float(data['past_rainfall'])
        
#         # Validate ranges
#         if not (-50 <= temperature <= 50):
#             return jsonify({'error': 'Temperature must be between -50 and 50°C'}), 400
#         if not (0 <= humidity <= 100):
#             return jsonify({'error': 'Humidity must be between 0 and 100%'}), 400
#         if not (0 <= wind_speed <= 200):
#             return jsonify({'error': 'Wind speed must be between 0 and 200 km/h'}), 400
#         if not (800 <= pressure <= 1200):
#             return jsonify({'error': 'Pressure must be between 800 and 1200 hPa'}), 400
#         if not (0 <= past_rainfall <= 500):
#             return jsonify({'error': 'Past rainfall must be between 0 and 500 mm'}), 400
        
#         # Prepare feature array
#         features = np.array([[temperature, humidity, wind_speed, pressure, past_rainfall]])
        
#         # Make prediction
#         prediction = model.predict(features)[0]
#         prediction = max(0, prediction)  # Ensure non-negative
        
#         # Calculate confidence (simplified - based on feature ranges)
#         # In a real scenario, you might use prediction intervals or model uncertainty
#         confidence = min(95, max(60, 100 - abs(prediction) * 0.5))
        
#         # Save to database
#         try:
#             # Use timeout and ensure proper connection handling
#             conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
#             cursor = conn.cursor()
#             timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
#             cursor.execute('''
#                 INSERT INTO predictions 
#                 (temperature, humidity, wind_speed, pressure, predicted_rainfall, timestamp)
#                 VALUES (?, ?, ?, ?, ?, ?)
#             ''', (temperature, humidity, wind_speed, pressure, prediction, timestamp))
            
#             conn.commit()
#             prediction_id = cursor.lastrowid
#             cursor.close()
#             conn.close()
#             print(f"Prediction saved to database with ID: {prediction_id}")
#         except Exception as db_error:
#             print(f"Database error while saving prediction: {db_error}")
#             # Continue even if database save fails
#             prediction_id = None
        
#         # Generate insights
#         insights = generate_insights(temperature, humidity, wind_speed, pressure, prediction)
        
#         return jsonify({
#             'success': True,
#             'prediction': round(prediction, 2),
#             'confidence': round(confidence, 1),
#             'insights': insights,
#             'id': prediction_id,
#             'timestamp': timestamp
#         })
    
#     except ValueError as e:
#         return jsonify({'error': f'Invalid input: {str(e)}'}), 400
#     except Exception as e:
#         return jsonify({'error': f'Prediction error: {str(e)}'}), 500

# def generate_insights(temp, humidity, wind_speed, pressure, rainfall):
#     """Generate insights based on prediction"""
#     insights = []
    
#     if rainfall > 10:
#         insights.append("Heavy rainfall expected. Take necessary precautions.")
#     elif rainfall > 5:
#         insights.append("Moderate rainfall predicted. Carry an umbrella.")
#     elif rainfall > 0.5:
#         insights.append("Light rainfall expected.")
#     else:
#         insights.append("No significant rainfall predicted.")
    
#     if humidity > 80:
#         insights.append("High humidity levels increase rainfall probability.")
    
#     if pressure < 1000:
#         insights.append("Low pressure indicates potential storm conditions.")
    
#     if wind_speed > 50:
#         insights.append("High wind speed may accompany the rainfall.")
    
#     return insights

# @app.route('/api/history', methods=['GET'])
# def api_history():
#     """API endpoint to get prediction history"""
#     try:
#         print(f"Fetching history from database: {DB_PATH}")
#         conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
#         cursor = conn.cursor()
        
#         # Get all predictions
#         cursor.execute('''
#             SELECT id, temperature, humidity, wind_speed, pressure, 
#                    predicted_rainfall, timestamp
#             FROM predictions
#             ORDER BY timestamp DESC
#             LIMIT 100
#         ''')
        
#         rows = cursor.fetchall()
#         print(f"Found {len(rows)} predictions in database")
        
#         # Convert to list of dictionaries
#         predictions = []
#         for row in rows:
#             predictions.append({
#                 'id': row[0],
#                 'temperature': row[1],
#                 'humidity': row[2],
#                 'wind_speed': row[3],
#                 'pressure': row[4],
#                 'predicted_rainfall': row[5],
#                 'timestamp': row[6]
#             })
        
#         # Close connection immediately after fetching data
#         cursor.close()
#         conn.close()
        
#         return jsonify({'success': True, 'predictions': predictions})
    
#     except Exception as e:
#         return jsonify({'error': f'Database error: {str(e)}'}), 500

# @app.route('/api/stats', methods=['GET'])
# def api_stats():
#     """API endpoint to get statistics for charts"""
#     try:
#         print(f"Fetching stats from database: {DB_PATH}")
#         conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
#         cursor = conn.cursor()
        
#         # Get all predictions
#         cursor.execute('''
#             SELECT predicted_rainfall, timestamp
#             FROM predictions
#             ORDER BY timestamp ASC
#         ''')
        
#         rows = cursor.fetchall()
        
#         # Prepare data for charts
#         timestamps = [row[1] for row in rows]
#         rainfall_values = [row[0] for row in rows]
        
#         # Calculate statistics
#         if rainfall_values:
#             avg_rainfall = np.mean(rainfall_values)
#             max_rainfall = np.max(rainfall_values)
#             min_rainfall = np.min(rainfall_values)
#             total_predictions = len(rainfall_values)
#         else:
#             avg_rainfall = max_rainfall = min_rainfall = 0
#             total_predictions = 0
        
#         # Close connection immediately after fetching data
#         cursor.close()
#         conn.close()
        
#         return jsonify({
#             'success': True,
#             'timestamps': timestamps,
#             'rainfall_values': rainfall_values,
#             'statistics': {
#                 'average': round(avg_rainfall, 2),
#                 'maximum': round(max_rainfall, 2),
#                 'minimum': round(min_rainfall, 2),
#                 'total': total_predictions
#             }
#         })
    
#     except Exception as e:
#         return jsonify({'error': f'Database error: {str(e)}'}), 500

# @app.route('/api/download', methods=['GET'])
# def api_download():
#     """API endpoint to download predictions as CSV"""
#     try:
#         conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
#         df = pd.read_sql_query('''
#             SELECT id, temperature, humidity, wind_speed, pressure, 
#                    predicted_rainfall, timestamp
#             FROM predictions
#             ORDER BY timestamp DESC
#         ''', conn)
#         conn.close()
        
#         # Save to CSV
#         csv_path = os.path.join(base_dir, 'database', 'predictions_export.csv')
#         df.to_csv(csv_path, index=False)
        
#         return send_file(csv_path, as_attachment=True, download_name='predictions.csv')
    
#     except Exception as e:
#         return jsonify({'error': f'Download error: {str(e)}'}), 500

# if __name__ == '__main__':
#     # Initialize database
#     init_db()
    
#     # Run Flask app
#     print("\n" + "="*50)
#     print("RainRadar Application Starting...")
#     print("="*50)
#     print(f"Database: {DB_PATH}")
#     print(f"Model: {'Loaded' if model else 'Not loaded - run train_model.py first'}")
#     print("="*50)
#     print("\nOpen your browser and navigate to: http://localhost:5000")
#     print("\nPress Ctrl+C to stop the server\n")
    
#     app.run(debug=True, host='0.0.0.0', port=5000)

"""
Flask Backend Application for RainRadar
Handles routing, predictions, and database operations
"""

from flask import Flask, render_template, request, jsonify, send_file
import joblib
import numpy as np
import sqlite3
import os
from datetime import datetime
import pandas as pd

app = Flask(__name__)

# ------------------------------
# Database Configuration
# ------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_PATH = os.path.join(DB_DIR, 'predictions.db')

def init_db():
    """Initialize the SQLite database"""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        print(f"Created database directory at {DB_DIR}")

    print(f"Using database file: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            wind_speed REAL NOT NULL,
            pressure REAL NOT NULL,
            predicted_rainfall REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_db_connection():
    """Return a new database connection"""
    conn = sqlite3.connect(DB_PATH, timeout=10.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def save_prediction(temperature, humidity, wind_speed, pressure, predicted_rainfall):
    """Save a prediction to the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO predictions 
            (temperature, humidity, wind_speed, pressure, predicted_rainfall, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (temperature, humidity, wind_speed, pressure, predicted_rainfall, timestamp))

        conn.commit()
        prediction_id = cursor.lastrowid
        cursor.close()
        conn.close()

        print(f"Saved prediction ID {prediction_id} to DB: {DB_PATH}")
        return prediction_id, timestamp
    except Exception as e:
        print(f"Database error: {e}")
        return None, None

def fetch_history(limit=100):
    """Fetch prediction history"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []

# ------------------------------
# Load ML Model
# ------------------------------
MODEL_PATH = os.path.join(BASE_DIR, 'model', 'rainfall_model.joblib')

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run train_model.py first.")
    model = joblib.load(MODEL_PATH)
    print(f"Model loaded from {MODEL_PATH}")
    return model

try:
    model = load_model()
except Exception as e:
    print(f"Warning: Failed to load model: {e}")
    model = None

# ------------------------------
# Helper: Generate Insights
# ------------------------------
def generate_insights(temp, humidity, wind_speed, pressure, rainfall):
    insights = []
    if rainfall > 10:
        insights.append("Heavy rainfall expected. Take necessary precautions.")
    elif rainfall > 5:
        insights.append("Moderate rainfall predicted. Carry an umbrella.")
    elif rainfall > 0.5:
        insights.append("Light rainfall expected.")
    else:
        insights.append("No significant rainfall predicted.")

    if humidity > 80:
        insights.append("High humidity levels increase rainfall probability.")
    if pressure < 1000:
        insights.append("Low pressure indicates potential storm conditions.")
    if wind_speed > 50:
        insights.append("High wind speed may accompany the rainfall.")
    return insights

# ------------------------------
# Flask Routes
# ------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/predict', methods=['POST'])
def api_predict():
    global model
    if model is None:
        return jsonify({'error': 'Model not loaded. Run train_model.py first.'}), 500

    data = request.get_json()
    required_fields = ['temperature', 'humidity', 'wind_speed', 'pressure', 'past_rainfall']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Extract features
    try:
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        wind_speed = float(data['wind_speed'])
        pressure = float(data['pressure'])
        past_rainfall = float(data['past_rainfall'])

        features = np.array([[temperature, humidity, wind_speed, pressure, past_rainfall]])
        prediction = max(0, model.predict(features)[0])

        confidence = min(95, max(60, 100 - abs(prediction) * 0.5))

        # Save to DB
        prediction_id, timestamp = save_prediction(temperature, humidity, wind_speed, pressure, prediction)
        insights = generate_insights(temperature, humidity, wind_speed, pressure, prediction)

        return jsonify({
            'success': True,
            'prediction': round(prediction, 2),
            'confidence': round(confidence, 1),
            'insights': insights,
            'id': prediction_id,
            'timestamp': timestamp
        })
    except Exception as e:
        return jsonify({'error': f'Prediction error: {e}'}), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    predictions = fetch_history()
    return jsonify({'success': True, 'predictions': predictions})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT predicted_rainfall, timestamp FROM predictions ORDER BY timestamp ASC')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        timestamps = [row['timestamp'] for row in rows]
        rainfall_values = [row['predicted_rainfall'] for row in rows]

        stats = {
            'average': round(np.mean(rainfall_values), 2) if rainfall_values else 0,
            'maximum': round(np.max(rainfall_values), 2) if rainfall_values else 0,
            'minimum': round(np.min(rainfall_values), 2) if rainfall_values else 0,
            'total': len(rainfall_values)
        }

        return jsonify({'success': True, 'timestamps': timestamps, 'rainfall_values': rainfall_values, 'statistics': stats})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def api_download():
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM predictions ORDER BY timestamp DESC', conn)
        conn.close()

        csv_path = os.path.join(DB_DIR, 'predictions_export.csv')
        df.to_csv(csv_path, index=False)

        return send_file(csv_path, as_attachment=True, download_name='predictions.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ------------------------------
# Run Flask App
# ------------------------------
if __name__ == '__main__':
    init_db()
    print("\nRainRadar Application Starting...")
    print(f"Database: {DB_PATH}")
    print(f"Model: {'Loaded' if model else 'Not loaded - run train_model.py first'}")
    print("Open your browser: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
