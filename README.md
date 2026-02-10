# Consommé AI: Professional Sleep Quality Predictor 🌙

Consommé AI is a machine learning-based web application designed to analyze and predict sleep quality specifically for working professionals. By leveraging the power of the **Random Forest Regressor**, this tool provides insights into how lifestyle factors affect rest.

## 🚀 Features
- **Professional Gatekeeper:** A dedicated access portal ensuring the tool is used by its target audience.
- **AI-Powered Analysis:** Predictive modeling using an optimized Random Forest algorithm.
- **Instant Recommendations:** Personalized feedback based on the predicted sleep quality score.
- **Responsive Interface:** A modern, glassmorphism-inspired UI for a seamless user experience.

## 🛠️ Tech Stack
- **Machine Learning:** Python, Scikit-Learn, Pandas, Joblib.
- **Backend:** Flask (Python).
- **Frontend:** HTML5, CSS3 (Custom Glassmorphism), JavaScript (Fetch API).
- **Deployment Ready:** Optimized for local and cloud hosting.

## 📊 Dataset & Model
The model was trained on professional sleep health data, undergoing rigorous hyperparameter tuning via `GridSearchCV` to achieve optimal R² performance. 
*Note: This project focuses on features such as Sleep Duration, Occupation, and Physical Activity levels.*

## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/consomme-ai.git](https://github.com/yourusername/consomme-ai.git)
   cd consomme-ai

2. **Setup Virtual Enivronment**
   ```bash
   python -m venv venv

   # Activate on Windows:
   venv\Scripts\activate
   
   # Activate on Mac/Linux:
   source venv/bin/activate

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

4. **Run Appliccation**
   ```bash
   python app.py

### Visit (http://127.0.0.1:5000) in your browser