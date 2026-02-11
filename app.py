from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import joblib
import pandas as pd
import os
import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

app = Flask(__name__)
app.secret_key = 'consomne_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

model = joblib.load('model_consomne.pkl')

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())
    
with app.app_context():
    db.create_all()

@app.route('/')
def gatekeeper():
    return render_template('gatekeeper.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('is_employed') == 'yes':
        session['is_allowed'] = True
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/app')
def main_app():
    if not session.get('is_allowed'):
        return redirect(url_for('gatekeeper'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('is_allowed'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'})

    try:
        data = request.json
        
        columns_order = [
            'Age', 'Sleep Duration', 'Physical Activity Level', 'Stress Level', 
            'BMI Category', 'Heart Rate', 'Daily Steps', 'Sleep Disorder', 
            'Systolic', 'Diastolic', 'Gender_Male', 'Occupation_Healthcare', 
            'Occupation_Professional Services', 'Occupation_Sales & Business', 
            'Occupation_Tech & Engineering'
        ]
        
        input_row = {col: 0 for col in columns_order}

        input_row['Age'] = float(data.get('Age', 0))
        input_row['Sleep Duration'] = float(data.get('Sleep Duration', 0))
        input_row['Physical Activity Level'] = float(data.get('Physical Activity Level', 0))
        input_row['Stress Level'] = float(data.get('Stress Level', 0))
        input_row['BMI Category'] = float(data.get('BMI Category', 0))
        input_row['Heart Rate'] = float(data.get('Heart Rate', 0))
        input_row['Daily Steps'] = float(data.get('Daily Steps', 0))
        input_row['Sleep Disorder'] = float(data.get('Sleep Disorder', 0))
        input_row['Systolic'] = float(data.get('Systolic', 0))
        input_row['Diastolic'] = float(data.get('Diastolic', 0))
        input_row['Gender_Male'] = True if int(data.get('Gender')) == 1 else False

        occ_val = int(data.get('Occupation'))
        input_row['Occupation_Healthcare'] = False
        input_row['Occupation_Professional Services'] = False
        input_row['Occupation_Sales & Business'] = False
        input_row['Occupation_Tech & Engineering'] = False

        if occ_val in [1, 5]: # Doctor, Nurse
            input_row['Occupation_Healthcare'] = True
        elif occ_val in [0, 3, 4, 9]: # Accountant, Lawyer, Manager, Teacher
            input_row['Occupation_Professional Services'] = True
        elif occ_val in [6]: # Salesperson
            input_row['Occupation_Sales & Business'] = True
        elif occ_val in [2, 7, 8]: # Engineer, Scientist, Software Engineer
            input_row['Occupation_Tech & Engineering'] = True

        input_df = pd.DataFrame([input_row], columns=columns_order)
        
        prediction = model.predict(input_df)[0]
        score = round(float(prediction), 1)
        
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
            'prediction': score,
            'recommendations': recommendations
        })

    except Exception as e:
        print(f"Error detail: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/feedback', methods=['POST'])
def feedback():
    if not session.get('is_allowed'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'})

    try:
        data = request.json
        rating = data.get('rating')
        comment = data.get('comment')
        # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        new_feedback = Feedback(
            rating=rating,
            comment=comment,
        )
        db.session.add(new_feedback)
        db.session.commit()

        print(f"Feedback saved to Database: {rating} stars")
        return jsonify({'status': 'success'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Failed to save feedback: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('gatekeeper'))

if __name__ == '__main__':
    app.run(debug=False)