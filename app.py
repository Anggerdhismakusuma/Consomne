from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import joblib
import pandas as pd
import os

app = Flask(__name__)
app_secret_key = 'consomne_secret_key'

model = joblib.load('model_consomne.pkl')

@app.route('/')
def gatekeeper():
    return render_template('gatekeeper.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('is_employeed') == 'yes':
        session['is_allowed'] = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Akses khusus orang yang sudah bekerja.'})

@app.route('/app')
def main_app():
    if not session.get('is_allowed'):
        return redirect(url_for('gatekeeper'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        input_data = pd.DataFrame([data])
        prediction = model.predict(input_data)[0]
        recommendations = []
        if data['Stress Level'] > 6:
            recommendations.append("Your stress levels are high. Consider 10 minutes of meditation before bed.")
        if data['Sleep Duration'] < 7:
            recommendations.append("You are sleeping less than 7 hours. Try to go to bed 30 minutes earlier.")
        if data['Daily Steps'] < 5000:
            recommendations.append("Physical activity is low. Increasing daily steps can improve sleep quality.")
        if not recommendations:
            recommendations.append("Your health habits are excellent! Keep it up.")
        
        return jsonify({
            'status': 'success',
            'prediction': round(float(prediction), 2),
            'recommendation': recommendations
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)