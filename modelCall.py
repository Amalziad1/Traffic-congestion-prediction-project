from flask import Flask, jsonify, request
import joblib  
import numpy as np

app = Flask(__name__)

model = joblib.load('model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    
    inputs = [
        data.get('weather_conditions', 0),
        data.get('road_type', 0),
        data.get('vehicle_type', 0),
        data.get('temperature', 0),
        data.get('humidity', 0),
        data.get('wind_speed', 0),
        data.get('precipitation', 0),
        data.get('population_density', 0)
    ]
    
    prediction = model.predict(inputs)
    return jsonify({'prediction': prediction.tolist()})

if __name__ == '__main__':
    app.run(debug=True)
