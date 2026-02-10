from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import joblib
import pandas as pd
import os
import csv
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'consomne_secret_key' # Bebas ganti apa saja

# 1. LOAD MODEL (Tanpa Scaler)
model = joblib.load('model_consomne.pkl')

@app.route('/')
def gatekeeper():
    return render_template('gatekeeper.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    if data.get('is_employed') == 'yes':
        session['is_allowed'] = True  # Memberikan izin akses
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/app')
def main_app():
    # Proteksi: Jika belum verifikasi di gatekeeper, tendang balik ke awal
    if not session.get('is_allowed'):
        return redirect(url_for('gatekeeper'))
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('is_allowed'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'})

    try:
        data = request.json
        
        # 1. URUTAN KOLOM HARUS PERSIS SEPERTI X_TRAIN KAMU
        columns_order = [
            'Age', 'Sleep Duration', 'Physical Activity Level', 'Stress Level', 
            'BMI Category', 'Heart Rate', 'Daily Steps', 'Sleep Disorder', 
            'Systolic', 'Diastolic', 'Gender_Male', 'Occupation_Healthcare', 
            'Occupation_Professional Services', 'Occupation_Sales & Business', 
            'Occupation_Tech & Engineering'
        ]
        
        # 2. Inisialisasi baris baru dengan nilai default (False untuk boolean, 0 untuk angka)
        input_row = {col: 0 for col in columns_order}

        # 3. Isi fitur numerik dasar
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

        # 4. LOGIKA ONE-HOT (Mapping dari Dropdown HTML ke Kolom Boolean)
        
        # Gender: Di HTML Male=1, Female=0. Model butuh Gender_Male (True/False)
        input_row['Gender_Male'] = True if int(data.get('Gender')) == 1 else False

        # Occupation Mapping (Berdasarkan value di index.html kamu)
        occ_val = int(data.get('Occupation'))
        # Reset semua occupation ke False dulu
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

        # 5. Konversi ke DataFrame
        input_df = pd.DataFrame([input_row], columns=columns_order)
        
        # 6. Jalankan Prediksi
        prediction = model.predict(input_df)[0]
        score = round(float(prediction), 1)
        
        # Logika rekomendasi (sama seperti sebelumnya)
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

# Tambahkan route feedback agar tombol feedback di HTML kamu tidak error
@app.route('/feedback', methods=['POST'])
def feedback():
    if not session.get('is_allowed'):
        return jsonify({'status': 'error', 'message': 'Unauthorized'})

    try:
        data = request.json
        rating = data.get('rating')
        comment = data.get('comment')
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Tentukan nama file CSV
        file_path = 'user_feedback.csv'
        file_exists = os.path.isfile(file_path)

        # Simpan ke CSV
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Jika file baru, buat header-nya dulu
            if not file_exists:
                writer.writerow(['Timestamp', 'Rating', 'Comment'])
            
            # Tulis data feedback
            writer.writerow([timestamp, rating, comment])

        print(f"Feedback saved to CSV: {rating} stars")
        return jsonify({'status': 'success'})
    
    except Exception as e:
        print(f"Failed to save feedback: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('gatekeeper'))

if __name__ == '__main__':
    app.run(debug=True)