import streamlit as st
import pandas as pd
import base64
import os
import matplotlib.pyplot as plt
import mysql.connector
import hashlib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import random
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from xgboost import XGBClassifier
from sklearn.ensemble import GradientBoostingClassifier
from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import LSTM, Dense # type: ignore
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
import time
from sklearn.preprocessing import LabelEncoder


# MySQL connection setup
# Create connection to database
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",      # Update with your DB host
        user="root",          # Your MySQL username
        password="harisatyam", # Your MySQL password
        database="sys"        # Your MySQL database name
    )
    return conn

# Hash the password
def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


# MySQL connection setup
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",  # Update with your DB host
        user="root",  # Your MySQL username
        password="harisatyam",  # Your MySQL password
        database="sys"  # Your MySQL database name
    )
    return conn


# Check if username exists in the database
def check_user_exists(username):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


# Insert new user into the database
def insert_user(username, password):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        conn.close()
        st.success("User successfully added.")
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")


# Verify user credentials during login
def verify_user_credentials(username, password):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_password = result[0]
            if stored_password == password:  # Compare plaintext passwords
                return True
        return False
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        return False
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return False

# Login function
def login():
    st.title("Crop Recommendation System")
    #st.subheader("A road map to farmers")
    st.title("Login")
    st.write("Enter your credentials")
    
    # Initialize error state
    if 'show_error' not in st.session_state:
        st.session_state.show_error = False

    # Add custom CSS for the popup message
    st.markdown("""
        <style>
        .error-popup {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: #fff;
            padding: 20px 30px;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            animation: fadeIn 0.3s ease-in-out;
            border-left: 5px solid #ff4b4b;
            text-align: center;
        }
        .error-popup h3 {
            color: #ff4b4b;
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }
        .error-popup p {
            color: #666;
            margin: 0;
        }
        .close-button {
            position: absolute;
            top: 10px;
            right: 10px;
            border: none;
            background: none;
            font-size: 18px;
            cursor: pointer;
            color: #666;
            padding: 5px;
            line-height: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            transition: all 0.2s;
        }
        .close-button:hover {
            background-color: #f0f0f0;
            color: #ff4b4b;
        }
        @keyframes fadeIn {
            from {opacity: 0; transform: translate(-50%, -60%);}
            to {opacity: 1; transform: translate(-50%, -50%);}
        }
        </style>
    """, unsafe_allow_html=True)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # Create two columns for buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Login", key="login_button", use_container_width=True):
            if verify_user_credentials(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.page = 'dashboard'
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.session_state.show_error = True
                st.rerun()

    with col2:
        if st.button("Go to Signup", key="goto_signup_button", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()

    # Show error popup if needed
    if st.session_state.show_error:
        st.markdown("""
            <div class="error-popup">
                <button class="close-button" onclick="document.querySelector('.error-popup').style.display='none'; window.streamlitRerun();">×</button>
                <h3>❌ Login Failed</h3>
                <p>Invalid username or password.<br>Please try again.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Add JavaScript to handle the close button click
        st.markdown("""
            <script>
                function streamlitRerun() {
                    const elements = window.parent.document.getElementsByTagName('iframe');
                    for (const element of elements) {
                        if (element.srcdoc.indexOf('streamlitRerun') > 0) {
                            element.dispatchEvent(new Event('streamlitRerun'));
                            break;
                        }
                    }
                }
            </script>
        """, unsafe_allow_html=True)
        
        # Reset error state after 3 seconds
        time.sleep(3)
        st.session_state.show_error = False
        st.rerun()

# Signup function
def signup():
    st.title("Sign Up")
    new_username = st.text_input("Choose a username")
    new_password = st.text_input("Choose a password", type="password")
    confirm_password = st.text_input("Confirm password", type="password")

    # Create two columns for buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Sign Up", key="signup_button", use_container_width=True):
            if new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                if check_user_exists(new_username):
                    st.error("Username already exists")
                else:
                    insert_user(new_username, new_password)  # Password will be hashed in insert_user
                    st.success("Account created successfully! Please log in.")
                    st.session_state.page = "login"
                    st.rerun()

    with col2:
        if st.button("Go to Login", key="goto_login_button", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


# Login function
# def login():
#     st.title("Login")
#     st.write("Enter your credentials")
#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")
#
#     if st.button("Login"):
#         if verify_user_credentials(username, password):
#             st.session_state.logged_in = True
#             st.session_state.username = username
#             st.session_state.page = 'dashboard'
#             st.success("Logged in successfully!")
#             st.experimental_rerun()
#         else:
#             st.error("Invalid username or password")
#
#     if st.button("Go to Signup"):
#         st.session_state.page = "signup"
#         st.experimental_rerun()

def add_bg_style():
    bg_style = """
    <style>
    .stApp {
        background-color: #f9f9f9;
        font-family: 'Arial', sans-serif;
        padding: 0;
    }
    .block-container {
        padding: 2rem;
        max-width: 100%;
        margin: 0 auto;
    }
    .stImage img {
        width: 100%;       /* Make the image take up full width of its container */
        max-width: 600px;   /* Limit the maximum size of the image */
        height: auto;       /* Maintain aspect ratio */
        display: block;
        margin-left: auto;  /* Center the image horizontally */
        margin-right: auto;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        font-size: 18px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    </style>
    """
    st.markdown(bg_style, unsafe_allow_html=True)



    # Add title with custom styling


# Function to display crop details
def display_crop_details(crop_name):
    add_bg_style()

    # Modern header with icon and gradient
    st.markdown(f"""
        <div style='background: linear-gradient(45deg, #1ed761, #4CAF50);
                    padding: 2rem;
                    border-radius: 15px;
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
            <h1 style='color: white; text-align: center; margin: 0;'>
                🌱 {crop_name.capitalize()} Details
            </h1>
        </div>
    """, unsafe_allow_html=True)

    # Get crop details
    crop_details = get_crop_details(crop_name.lower())  # Your existing crop details dictionary

    if crop_details:
        # Create three columns for layout
        col1, col2, col3 = st.columns([1.5, 0.5, 1])

        with col1:
            # Image card with shadow and rounded corners
            st.markdown("""
                <style>
                .crop-image {
                    border-radius: 15px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    transition: transform 0.3s ease;
                }
                .crop-image:hover {
                    transform: scale(1.02);
                }
                </style>
            """, unsafe_allow_html=True)
            st.image(crop_details['image_url'], 
                    caption=f"{crop_name.capitalize()} Plant",
                    use_column_width=True)

        with col2:
            # Enhanced quick facts card
            st.markdown(f"""
                <div style='background: white;
                            padding: 1.5rem;
                            border-radius: 15px;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);'>
                    <h3 style='color: #2c3e50; margin-bottom: 1rem;'>Quick Facts</h3>
                    <p><strong>Scientific Name:</strong><br/>
                       <em>{crop_details['scientific_name']}</em></p>
                    <p><strong>Season:</strong><br/>
                       {crop_details['season']}</p>
                    <p><strong>Growing Period:</strong><br/>
                       {crop_details['seasonal_months']}</p>
                </div>
            """, unsafe_allow_html=True)

        # Add a new section for detailed information
        st.markdown("""
            <div style='margin-top: 2rem;'>
                <h3 style='color: #2c3e50;'>Crop Information</h3>
            </div>
        """, unsafe_allow_html=True)

        # Create three columns for detailed info
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
                <div style='background: white;
                            padding: 1rem;
                            border-radius: 10px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                    <h4 style='color: #2c3e50;'>Seasonal Details</h4>
                    <ul style='list-style-type: none; padding-left: 0;'>
                        <li>🌱 <strong>Sowing:</strong> {}</li>
                        <li>🌾 <strong>Harvesting:</strong> {}</li>
                    </ul>
                </div>
            """.format(
                crop_details['seasonal_months'].split('to')[0].strip(),
                crop_details['seasonal_months'].split('to')[1].strip()
            ), unsafe_allow_html=True)

        # Interactive tabs for detailed information
        tabs = st.tabs(["📊 Growth Patterns", "🌡️ Climate", "💧 Water Requirements", "🧪 Soil Analysis"])
        
        with tabs[0]:
            # Growth pattern visualization
            fig = go.Figure()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            
            fig.add_trace(go.Scatter(
                x=months,
                y=crop_details['temperature_pattern'],
                name='Temperature',
                line=dict(color='#FF9999', width=3),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title="Growth Pattern Over Time",
                xaxis_title="Month",
                yaxis_title="Growth Rate",
                template="plotly_white",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tabs[1]:
            # Climate requirements
            col1, col2 = st.columns(2)
            with col1:
                # Temperature gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=crop_details['temperature_pattern'][0],
                    title={'text': "Optimal Temperature (°C)"},
                    gauge={'axis': {'range': [0, 50]},
                           'bar': {'color': "#FF9999"},
                           'steps': [
                               {'range': [0, 20], 'color': "lightgray"},
                               {'range': [20, 30], 'color': "gray"}]}))
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Humidity gauge
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=crop_details['rainfall_pattern'][0],
                    title={'text': "Required Rainfall (mm)"},
                    gauge={'axis': {'range': [0, 300]},
                           'bar': {'color': "#66B2FF"},
                           'steps': [
                               {'range': [0, 100], 'color': "lightgray"},
                               {'range': [100, 200], 'color': "gray"}]}))
                st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            # Water requirements visualization
            fig = px.area(
                x=months,
                y=crop_details['rainfall_pattern'],
                title="Monthly Water Requirements",
                labels={'x': 'Month', 'y': 'Rainfall (mm)'}
            )
            fig.update_traces(fill='tozeroy', line_color='#66B2FF')
            st.plotly_chart(fig, use_container_width=True)

        with tabs[3]:
            # Soil requirements
            col1, col2, col3 = st.columns(3)
            minerals = crop_details['minerals']
            
            for i, mineral in enumerate(minerals):
                with eval(f'col{(i%3)+1}'):
                    st.markdown(f"""
                        <div style='background: white;
                                    padding: 1rem;
                                    border-radius: 10px;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                                    text-align: center;'>
                            <h3 style='color: #2c3e50;'>{mineral}</h3>
                            <p style='color: #7f8c8d;'>Essential Nutrient</p>
                        </div>
                    """, unsafe_allow_html=True)

        # Download section
        st.markdown("""
            <div style='background: #f8f9fa;
                        padding: 1.5rem;
                        border-radius: 15px;
                        margin-top: 2rem;
                        text-align: center;'>
                <h3 style='color: #2c3e50;'>Download Resources</h3>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Download image button
            with open(crop_details['image_url'], "rb") as file:
                btn = st.download_button(
                    label="📸 Download Image",
                    data=file,
                    file_name=f"{crop_name.lower()}.jpg",
                    mime="image/jpeg"
                )
        
        with col2:
            # Download info button (you'll need to create this PDF)
            st.button("📑 Download Crop Guide", 
                     help="Download detailed growing instructions")

    else:
        st.warning(f"No details found for {crop_name}")

    # Floating back button with animation
    st.markdown("""
        <style>
        .floating-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            text-decoration: none;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }
        .floating-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🔙 Back to Dashboard", key="back_button"):
        st.session_state['page'] = 'dashboard'
        st.rerun()


# Crop recommendation dashboard function
def crop_recommendation_dashboard():
    # Define target_mapper at the start
    target_mapper = {
        'rice': 0, 'maize': 1, 'chickpea': 2, 'kidneybeans': 3, 'pigeonpeas': 4,
        'mothbeans': 5, 'mungbean': 6, 'blackgram': 7, 'lentil': 8, 'pomegranate': 9,
        'banana': 10, 'mango': 11, 'grapes': 12, 'watermelon': 13, 'muskmelon': 14,
        'apple': 15, 'orange': 16, 'papaya': 17, 'coconut': 18, 'cotton': 19,
        'jute': 20, 'coffee': 21
    }

    # Initialize model_results if not in session state
    if 'model_results' not in st.session_state:
        st.session_state.model_results = {}

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #2c3e50;
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .feature-container {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        .prediction-container {
            background-color: #f8f9fa;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # Main header with gradient background
    st.markdown('<h1 class="main-header">🌾 Crop Recommendation System</h1>', unsafe_allow_html=True)

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col2:
        st.markdown('<div class="feature-container">', unsafe_allow_html=True)
        st.subheader(" Input Parameters")
        
        # Add input parameters with more intuitive ranges and visual feedback
        N = st.slider('Nitrogen (N) Content', 0.0, 140.0, 50.55,
                     help="Nitrogen content in soil (mg/kg)")
        P = st.slider('Phosphorus (P) Content', 5.0, 145.0, 53.36,
                     help="Phosphorus content in soil (mg/kg)")
        K = st.slider('Potassium (K) Content', 5.0, 205.0, 48.14,
                     help="Potassium content in soil (mg/kg)")
        temperature = st.slider('Temperature (°C)', 8.82, 43.67, 25.61,
                              help="Average temperature in Celsius")
        humidity = st.slider('Humidity (%)', 14.25, 99.98, 71.48,
                           help="Relative humidity in percentage")
        ph = st.slider('Soil pH', 3.50, 9.00, 6.5,
                      help="pH level of the soil")
        rainfall = st.slider('Rainfall (mm)', 20.21, 298.56, 103.46,
                           help="Annual rainfall in millimeters")
        
        # Create input_df right after collecting all inputs
        data = {'N': N, 'P': P, 'K': K, 'temperature': temperature,
                'humidity': humidity, 'ph': ph, 'rainfall': rainfall}
        input_df = pd.DataFrame(data, index=[0])
        st.markdown('</div>', unsafe_allow_html=True)

    with col1:
        # Modified tabs for crop recommendation
        st.markdown('<div class="feature-container">', unsafe_allow_html=True)
        tabs = st.tabs(["🌱 Models Analysis", "🌿 Climate Impact", "🌾 Crop Patterns"])
        
        df = pd.read_csv('https://raw.githubusercontent.com/aakashr02/Crop-Recommendation/refs/heads/main/data/Crop_recommendation.csv')
        
        # After loading df = pd.read_csv(...)
        X = df.drop(columns='label')
        y = df['label'].map(target_mapper)

        # Split data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Scale the features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        with tabs[0]:
            # Crop Recommendations Tab
            st.markdown("""
                <div style='background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #4361ee;'>
                    <h2 style='color: #4361ee; margin: 0;'>🤖 Machine Learning Model Comparison</h2>
                    <p style='color: #666; margin-top: 10px;'>Select models to analyze your crop data and get intelligent recommendations.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Model cards with vertical layout
            st.markdown("""
                <style>
                .model-card {
                    background-color: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    margin-bottom: 15px;
                }
                .accuracy-badge {
                    background-color: #f0f8f0;
                    padding: 8px 12px;
                    border-radius: 6px;
                    margin-top: 8px;
                    text-align: center;
                    border-left: 3px solid #4CAF50;
                    display: inline-block;
                }
                .accuracy-value {
                    color: #4CAF50;
                    font-size: 1.1em;
                    font-weight: bold;
                }
                </style>
            """, unsafe_allow_html=True)

            # Random Forest Section
            st.markdown("<div class='model-card'>", unsafe_allow_html=True)
            st.subheader("🌲 Random Forest")
            if st.button("Train Model", key="rf_button", use_container_width=True):
                with st.spinner('Training...'):
                    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
                    rf_model.fit(X_train, y_train)
                    rf_pred = rf_model.predict(X_test)
                    rf_accuracy = accuracy_score(y_test, rf_pred)
                    st.session_state.model_results['Random Forest'] = {
                        'accuracy': rf_accuracy,
                        'predictions': rf_model.predict_proba(input_df)[0]
                    }
                    st.markdown(f"""
                        <div class='accuracy-badge'>
                            Accuracy: <span class='accuracy-value'>{rf_accuracy:.2%}</span>
                        </div>
                    """, unsafe_allow_html=True)
            elif 'Random Forest' in st.session_state.model_results:
                st.markdown(f"""
                    <div class='accuracy-badge'>
                        Accuracy: <span class='accuracy-value'>{st.session_state.model_results['Random Forest']['accuracy']:.2%}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # XGBoost Section
            st.markdown("<div class='model-card'>", unsafe_allow_html=True)
            st.subheader("🚀 XGBoost")
            if st.button("Train Model", key="xgb_button", use_container_width=True):
                with st.spinner('Training...'):
                    xgb_model = XGBClassifier(random_state=42)
                    xgb_model.fit(X_train, y_train)
                    xgb_pred = xgb_model.predict(X_test)
                    xgb_accuracy = accuracy_score(y_test, xgb_pred)
                    st.session_state.model_results['XGBoost'] = {
                        'accuracy': xgb_accuracy,
                        'predictions': xgb_model.predict_proba(input_df)[0]
                    }
                    st.markdown(f"""
                        <div class='accuracy-badge'>
                            Accuracy: <span class='accuracy-value'>{xgb_accuracy:.2%}</span>
                        </div>
                    """, unsafe_allow_html=True)
            elif 'XGBoost' in st.session_state.model_results:
                st.markdown(f"""
                    <div class='accuracy-badge'>
                        Accuracy: <span class='accuracy-value'>{st.session_state.model_results['XGBoost']['accuracy']:.2%}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Gradient Boosting Section
            st.markdown("<div class='model-card'>", unsafe_allow_html=True)
            st.subheader("📈 Gradient Boosting")
            if st.button("Train Model", key="gb_button", use_container_width=True):
                with st.spinner('Training...'):
                    gb_model = GradientBoostingClassifier(random_state=42)
                    gb_model.fit(X_train, y_train)
                    gb_pred = gb_model.predict(X_test)
                    gb_accuracy = accuracy_score(y_test, gb_pred)
                    st.session_state.model_results['Gradient Boosting'] = {
                        'accuracy': gb_accuracy,
                        'predictions': gb_model.predict_proba(input_df)[0]
                    }
                    st.markdown(f"""
                        <div class='accuracy-badge'>
                            Accuracy: <span class='accuracy-value'>{gb_accuracy:.2%}</span>
                        </div>
                    """, unsafe_allow_html=True)
            elif 'Gradient Boosting' in st.session_state.model_results:
                st.markdown(f"""
                    <div class='accuracy-badge'>
                        Accuracy: <span class='accuracy-value'>{st.session_state.model_results['Gradient Boosting']['accuracy']:.2%}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # LSTM Section
            st.markdown("<div class='model-card'>", unsafe_allow_html=True)
            st.subheader("🧠 LSTM")
            if st.button("Train Model", key="lstm_button", use_container_width=True):
                with st.spinner('Training...'):
                    input_lstm = scaler.transform(input_df).reshape((1, 1, X_train_scaled.shape[1]))
                    X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], 1, X_train_scaled.shape[1]))
                    X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], 1, X_test_scaled.shape[1]))
                    lstm_model = create_lstm_model((1, X_train_scaled.shape[1]))
                    lstm_model.fit(X_train_lstm, y_train, epochs=50, batch_size=32, verbose=0)
                    lstm_accuracy = lstm_model.evaluate(X_test_lstm, y_test)[1]
                    st.session_state.model_results['LSTM'] = {
                        'accuracy': lstm_accuracy,
                        'predictions': lstm_model.predict(input_lstm)[0]
                    }
                    st.markdown(f"""
                        <div class='accuracy-badge'>
                            Accuracy: <span class='accuracy-value'>{lstm_accuracy:.2%}</span>
                        </div>
                    """, unsafe_allow_html=True)
            elif 'LSTM' in st.session_state.model_results:
                st.markdown(f"""
                    <div class='accuracy-badge'>
                        Accuracy: <span class='accuracy-value'>{st.session_state.model_results['LSTM']['accuracy']:.2%}</span>
                    </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Compare Models Section
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔍 Compare All Models", key="compare_models"):
                if not st.session_state.model_results:
                    st.warning("⚠️ Please train at least one model first!")
                else:
                    st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                            <h3 style='color: #1e88e5;'>📊 Model Comparison Results</h3>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Create accuracy comparison chart
                    accuracy_df = pd.DataFrame({
                        'Model': list(st.session_state.model_results.keys()),
                        'Accuracy': [results['accuracy'] for results in st.session_state.model_results.values()]
                    })
                    
                    # Interactive comparison chart
                    fig = px.bar(accuracy_df,
                                x='Model',
                                y='Accuracy',
                                color='Accuracy',
                                color_continuous_scale='viridis',
                                title='Model Performance Comparison')
                    
                    fig.update_layout(
                        plot_bgcolor='white',
                        yaxis_tickformat='.2%',
                        hovermode='x unified',
                        hoverlabel=dict(bgcolor='white'),
                        showlegend=False,
                        xaxis_title="Model Type",
                        yaxis_title="Accuracy Score",
                        title_x=0.5,
                        title_font_size=20
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Best Model Card
                    best_model = accuracy_df.loc[accuracy_df['Accuracy'].idxmax()]
                    st.markdown(f"""
                        <div style='background-color: #e3f2fd; padding: 20px; border-radius: 10px; text-align: center;'>
                            <h2 style='color: #1e88e5;'>🏆 Best Performing Model</h2>
                            <h3>{best_model['Model']}</h3>
                            <h4 style='color: #2e7d32;'>Accuracy: {best_model['Accuracy']:.2%}</h4>
                        </div>
                    """, unsafe_allow_html=True)

        with tabs[1]:
            # Climate Impact Tab
            st.subheader("Environmental Conditions")
            
            # Create a combined line chart for temperature and humidity
            fig = go.Figure()
            
            # Add temperature line
            fig.add_trace(go.Scatter(
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                y=[temperature-2, temperature, temperature+2, temperature+1, temperature-1, temperature],
                name='Temperature (°C)',
                line=dict(color='#FF9999')
            ))
            
            # Add humidity line
            fig.add_trace(go.Scatter(
                x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                y=[humidity-5, humidity, humidity+5, humidity-3, humidity+2, humidity],
                name='Humidity (%)',
                line=dict(color='#66B2FF')
            ))
            
            fig.update_layout(
                title="Temperature and Humidity Trends",
                xaxis_title="Month",
                yaxis_title="Value",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

        with tabs[2]:
            # Crop Patterns Tab
            st.markdown("""
                <div style='background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #4361ee;'>
                    <h3 style='color: #2c3e50; margin: 0;'>🌾 Crop Patterns</h3>
                </div>
            """, unsafe_allow_html=True)

            # Create expandable sections for different cropping patterns
            with st.expander("🔄 Types of Cropping Patterns"):
                st.markdown("""
                ### Common Cropping Patterns
                
                1. **Monocropping**
                   - Growing the same crop on the same land year after year
                   - Example: Rice-Rice or Wheat-Wheat
                   - *Caution: Can lead to soil degradation*
                
                2. **Crop Rotation**
                   - Growing different crops in sequence on the same field
                   - Example: Rice-Wheat-Pulses
                   - *Benefits: Improves soil health and breaks pest cycles*
                
                3. **Mixed Cropping**
                   - Growing two or more crops simultaneously in the same field
                   - Example: Wheat + Mustard or Groundnut + Sunflower
                   - *Benefits: Better resource utilization and risk management*
                
                4. **Intercropping**
                   - Growing two or more crops in a specific pattern
                   - Example: Sorghum + Pigeonpea (3:1 ratio)
                   - *Benefits: Maximizes land use and provides insurance against crop failure*
                
                5. **Relay Cropping**
                   - Planting a second crop before harvesting the first
                   - Example: Sowing wheat in standing cotton
                   - *Benefits: Saves time and extends growing season*
                """)

            with st.expander("🗓️ Seasonal Cropping Guide"):
                st.markdown("""
                ### Major Cropping Seasons

                #### 1. Kharif Season (Monsoon)
                - **Duration**: June to October
                - **Crops**: Rice, Maize, Sorghum, Cotton, Soybean
                - **Requirements**: Heavy rainfall, high temperature
                
                #### 2. Rabi Season (Winter)
                - **Duration**: October to March
                - **Crops**: Wheat, Chickpea, Mustard, Peas
                - **Requirements**: Moderate temperature, less water
                
                #### 3. Zaid Season (Summer)
                - **Duration**: March to June
                - **Crops**: Watermelon, Cucumber, Vegetables
                - **Requirements**: High temperature, irrigation facilities
                """)

            with st.expander("🌱 Sustainable Farming Practices"):
                st.markdown("""
                ### Sustainable Agricultural Methods

                1. **Conservation Agriculture**
                   - Minimum tillage
                   - Permanent soil cover
                   - Crop diversification
                
                2. **Integrated Farming**
                   - Combines crops with livestock/aquaculture
                   - Recycling of farm resources
                   - Reduced external inputs
                
                3. **Organic Farming**
                   - Natural fertilizers and pesticides
                   - Crop rotation and green manuring
                   - Biological pest control
                
                4. **Precision Agriculture**
                   - GPS-guided operations
                   - Variable rate technology
                   - Soil and crop monitoring
                """)

            with st.expander("💧 Water Management"):
                st.markdown("""
                ### Water Conservation Techniques

                1. **Irrigation Methods**
                   - Drip irrigation (90% efficiency)
                   - Sprinkler systems (75% efficiency)
                   - Surface irrigation (60% efficiency)
                
                2. **Water Conservation Practices**
                   - Mulching
                   - Rainwater harvesting
                   - Drought-resistant varieties
                   - Soil moisture conservation
                
                3. **Smart Irrigation Scheduling**
                   - Based on crop water requirements
                   - Weather monitoring
                   - Soil moisture sensors
                """)

            with st.expander("🌡️ Climate-Smart Agriculture"):
                st.markdown("""
                ### Climate Adaptation Strategies

                1. **Weather-Resilient Practices**
                   - Heat-tolerant varieties
                   - Early warning systems
                   - Protected cultivation
                
                2. **Carbon Farming**
                   - Reduced tillage
                   - Cover crops
                   - Agroforestry
                
                3. **Risk Management**
                   - Crop insurance
                   - Diversification
                   - Weather forecasting
                """)

            # Add a practical tips section
            st.markdown("""
                <div style='background-color: #e8f4ea; padding: 20px; border-radius: 10px; margin-top: 20px;'>
                    <h4 style='color: #2c3e50;'>💡 Quick Tips for Successful Cropping</h4>
                    <ul style='color: #2c3e50;'>
                        <li>Always test your soil before deciding on crops</li>
                        <li>Follow local agricultural calendars</li>
                        <li>Maintain proper spacing between plants</li>
                        <li>Practice integrated pest management</li>
                        <li>Keep records of farming activities</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

    # Prediction section with enhanced visualization
    data = {'N': N, 'P': P, 'K': K, 'temperature': temperature,
            'humidity': humidity, 'ph': ph, 'rainfall': rainfall}
    input_df = pd.DataFrame(data, index=[0])

    X = df.drop(columns='label')
    target_mapper = {
        'rice': 0, 'maize': 1, 'chickpea': 2, 'kidneybeans': 3, 'pigeonpeas': 4,
        'mothbeans': 5, 'mungbean': 6, 'blackgram': 7, 'lentil': 8, 'pomegranate': 9,
        'banana': 10, 'mango': 11, 'grapes': 12, 'watermelon': 13, 'muskmelon': 14,
        'apple': 15, 'orange': 16, 'papaya': 17, 'coconut': 18, 'cotton': 19,
        'jute': 20, 'coffee': 21
    }

    y = df['label'].map(target_mapper)
    clf = RandomForestClassifier()
    clf.fit(X, y)

    prediction = clf.predict(input_df)
    prediction_proba = clf.predict_proba(input_df)

    # Enhanced prediction display with visualization
    st.markdown('<div class="prediction-container">', unsafe_allow_html=True)
    st.subheader("🎯 Crop Recommendations")
    
    # Get top 5 recommendations for visualization
    proba_df = pd.DataFrame({
        'Crop': list(target_mapper.keys()),
        'Probability': prediction_proba[0]
    }).sort_values('Probability', ascending=False).head(5)

    # Create a horizontal bar chart for top recommendations
    fig = px.bar(proba_df,
                 x='Probability',
                 y='Crop',
                 orientation='h',
                 title='Top 5 Recommended Crops',
                 color='Probability',
                 color_continuous_scale='Viridis')
    
    fig.update_layout(
        xaxis_title="Success Probability",
        yaxis_title="Crop",
        showlegend=False,
        yaxis={'categoryorder':'total ascending'}
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Display top recommendation with action button
    recommended_crop = proba_df.iloc[0]['Crop']
    st.markdown(f"""
        <div style='text-align: center; padding: 1.5rem; background-color: white; 
        border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 1rem;'>
        <h3>Top Recommendation</h3>
        <h2>{recommended_crop.title()}</h2>
        <p>Success Probability: {proba_df.iloc[0]['Probability']:.1%}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button(f"📋 View {recommended_crop.title()} Details",
                 key='view_details',
                 help=f"Click to see detailed information about {recommended_crop}"):
        st.session_state['page'] = 'crop_details'
        st.session_state['recommended_crop'] = recommended_crop
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def add_bg_from_local(image_file):
    try:
        with open(image_file, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
            return f"data:image/jpeg;base64,{encoded_string}"
    except FileNotFoundError:
        st.error(f"Background image not found: {image_file}")
        return ""
    except Exception as e:
        st.error(f"Error loading background image: {str(e)}")
        return ""

def create_lstm_model(input_shape):
    model = Sequential([
        LSTM(64, input_shape=input_shape),
        Dense(32, activation='relu'),
        Dense(22, activation='softmax')  # 22 classes for different crops
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

def get_crop_details(crop_name):
    base_path = "/Users/harisatyam/Documents/Work/images"
    
    crop_database = {
        'rice': {
            'image_url': f"{base_path}/rice1.jpg",
            'scientific_name': 'Oryza sativa',
            'season': 'Kharif',
            'seasonal_months': 'June to November',
            'temperature_pattern': [25, 27, 28, 26, 24, 23],
            'rainfall_pattern': [150, 200, 180, 160, 140, 120],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'maize': {
            'image_url': f"{base_path}/maize1.jpg",
            'scientific_name': 'Zea mays',
            'season': 'Kharif',
            'seasonal_months': 'June to October',
            'temperature_pattern': [24, 26, 28, 27, 25, 23],
            'rainfall_pattern': [100, 120, 140, 130, 110, 90],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'chickpea': {
            'image_url': f"{base_path}/chickpea1.jpg",
            'scientific_name': 'Cicer arietinum',
            'season': 'Rabi',
            'seasonal_months': 'October to March',
            'temperature_pattern': [20, 22, 24, 23, 21, 19],
            'rainfall_pattern': [40, 50, 60, 55, 45, 35],
            'minerals': ['Phosphorus', 'Sulfur', 'Zinc']
        },
        'kidneybeans': {
            'image_url': f"{base_path}/kidneybeans1.jpg",
            'scientific_name': 'Phaseolus vulgaris',
            'season': 'Kharif',
            'seasonal_months': 'June to September',
            'temperature_pattern': [23, 25, 27, 26, 24, 22],
            'rainfall_pattern': [90, 110, 130, 120, 100, 80],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'pigeonpeas': {
            'image_url': f"{base_path}/pigeonpeas1.jpg",
            'scientific_name': 'Cajanus cajan',
            'season': 'Kharif',
            'seasonal_months': 'June to March',
            'temperature_pattern': [25, 27, 29, 28, 26, 24],
            'rainfall_pattern': [120, 140, 160, 150, 130, 110],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'mothbeans': {
            'image_url': f"{base_path}/mothbeans1.jpg",
            'scientific_name': 'Vigna aconitifolia',
            'season': 'Kharif',
            'seasonal_months': 'July to October',
            'temperature_pattern': [26, 28, 30, 29, 27, 25],
            'rainfall_pattern': [80, 100, 120, 110, 90, 70],
            'minerals': ['Nitrogen', 'Phosphorus', 'Zinc']
        },
        'mungbean': {
            'image_url': f"{base_path}/mungbean1.jpg",
            'scientific_name': 'Vigna radiata',
            'season': 'Kharif',
            'seasonal_months': 'July to September',
            'temperature_pattern': [24, 26, 28, 27, 25, 23],
            'rainfall_pattern': [70, 90, 110, 100, 80, 60],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'blackgram': {
            'image_url': f"{base_path}/blackgram1.jpg",
            'scientific_name': 'Vigna mungo',
            'season': 'Kharif',
            'seasonal_months': 'June to September',
            'temperature_pattern': [25, 27, 29, 28, 26, 24],
            'rainfall_pattern': [100, 120, 140, 130, 110, 90],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'lentil': {
            'image_url': f"{base_path}/lentil1.jpg",
            'scientific_name': 'Lens culinaris',
            'season': 'Rabi',
            'seasonal_months': 'October to March',
            'temperature_pattern': [18, 20, 22, 21, 19, 17],
            'rainfall_pattern': [30, 40, 50, 45, 35, 25],
            'minerals': ['Phosphorus', 'Potassium', 'Zinc']
        },
        'pomegranate': {
            'image_url': f"{base_path}/pomegranate1.jpg",
            'scientific_name': 'Punica granatum',
            'season': 'Perennial',
            'seasonal_months': 'February to March',
            'temperature_pattern': [22, 24, 26, 25, 23, 21],
            'rainfall_pattern': [60, 80, 100, 90, 70, 50],
            'minerals': ['Nitrogen', 'Potassium', 'Iron']
        },
        'banana': {
            'image_url': f"{base_path}/banana1.jpg",
            'scientific_name': 'Musa acuminata',
            'season': 'Perennial',
            'seasonal_months': 'June to September',
            'temperature_pattern': [24, 26, 28, 27, 25, 23],
            'rainfall_pattern': [150, 170, 190, 180, 160, 140],
            'minerals': ['Nitrogen', 'Potassium', 'Magnesium']
        },
        'mango': {
            'image_url': f"{base_path}/mango1.jpg",
            'scientific_name': 'Mangifera indica',
            'season': 'Perennial',
            'seasonal_months': 'April to July',
            'temperature_pattern': [26, 28, 30, 29, 27, 25],
            'rainfall_pattern': [100, 120, 140, 130, 110, 90],
            'minerals': ['Nitrogen', 'Potassium', 'Zinc']
        },
        'grapes': {
            'image_url': f"{base_path}/grapes1.jpg",
            'scientific_name': 'Vitis vinifera',
            'season': 'Perennial',
            'seasonal_months': 'January to March',
            'temperature_pattern': [23, 25, 27, 26, 24, 22],
            'rainfall_pattern': [70, 90, 110, 100, 80, 60],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'watermelon': {
            'image_url': f"{base_path}/watermelon1.jpg",
            'scientific_name': 'Citrullus lanatus',
            'season': 'Kharif',
            'seasonal_months': 'March to June',
            'temperature_pattern': [25, 27, 29, 28, 26, 24],
            'rainfall_pattern': [80, 100, 120, 110, 90, 70],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'muskmelon': {
            'image_url': f"{base_path}/muskmelon1.jpg",
            'scientific_name': 'Cucumis melo',
            'season': 'Kharif',
            'seasonal_months': 'March to June',
            'temperature_pattern': [24, 26, 28, 27, 25, 23],
            'rainfall_pattern': [70, 90, 110, 100, 80, 60],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'apple': {
            'image_url': f"{base_path}/apple1.jpg",
            'scientific_name': 'Malus domestica',
            'season': 'Perennial',
            'seasonal_months': 'July to October',
            'temperature_pattern': [18, 20, 22, 21, 19, 17],
            'rainfall_pattern': [80, 100, 120, 110, 90, 70],
            'minerals': ['Nitrogen', 'Calcium', 'Boron']
        },
        'orange': {
            'image_url': f"{base_path}/orange1.jpg",
            'scientific_name': 'Citrus × sinensis',
            'season': 'Perennial',
            'seasonal_months': 'November to March',
            'temperature_pattern': [22, 24, 26, 25, 23, 21],
            'rainfall_pattern': [90, 110, 130, 120, 100, 80],
            'minerals': ['Nitrogen', 'Phosphorus', 'Zinc']
        },
        'papaya': {
            'image_url': f"{base_path}/papaya1.jpg",
            'scientific_name': 'Carica papaya',
            'season': 'Perennial',
            'seasonal_months': 'July to March',
            'temperature_pattern': [25, 27, 29, 28, 26, 24],
            'rainfall_pattern': [120, 140, 160, 150, 130, 110],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'coconut': {
            'image_url': f"{base_path}/coconut1.jpg",
            'scientific_name': 'Cocos nucifera',
            'season': 'Perennial',
            'seasonal_months': 'May to September',
            'temperature_pattern': [26, 28, 30, 29, 27, 25],
            'rainfall_pattern': [180, 200, 220, 210, 190, 170],
            'minerals': ['Nitrogen', 'Potassium', 'Chlorine']
        },
        'cotton': {
            'image_url': f"{base_path}/cotton1.jpg",
            'scientific_name': 'Gossypium hirsutum',
            'season': 'Kharif',
            'seasonal_months': 'March to September',
            'temperature_pattern': [25, 27, 29, 28, 26, 24],
            'rainfall_pattern': [100, 120, 140, 130, 110, 90],
            'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
        },
        'jute': {
            'image_url': f"{base_path}/jute1.jpg",
            'scientific_name': 'Corchorus capsularis',
            'season': 'Kharif',
            'seasonal_months': 'March to June',
            'temperature_pattern': [27, 29, 31, 30, 28, 26],
            'rainfall_pattern': [150, 170, 190, 180, 160, 140],
            'minerals': ['Nitrogen', 'Potassium', 'Sulfur']
        },
        'coffee': {
            'image_url': f"{base_path}/coffee1.jpg",
            'scientific_name': 'Coffea arabica',
            'season': 'Perennial',
            'seasonal_months': 'October to March',
            'temperature_pattern': [20, 22, 24, 23, 21, 19],
            'rainfall_pattern': [160, 180, 200, 190, 170, 150],
            'minerals': ['Nitrogen', 'Phosphorus', 'Magnesium']
        }
    }

    # Default crop details if crop not found
    default_details = {
        'image_url': f"{base_path}/default.jpg",
        'season': 'Year-round',
        'temperature_pattern': [22, 24, 26, 25, 23, 21],
        'rainfall_pattern': [80, 100, 120, 110, 90, 70],
        'minerals': ['Nitrogen', 'Phosphorus', 'Potassium']
    }

    return crop_database.get(crop_name, default_details)

# Main function
def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    current_dir = os.path.dirname(os.path.abspath(__file__))
    background_image_path = os.path.join(current_dir, 'bg_2.jpg')


    if not st.session_state['logged_in']:
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("{add_bg_from_local(background_image_path)}");
                background-size: cover;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.session_state['page'] == 'login':
            login()
        elif st.session_state['page'] == 'signup':
            signup()
    else:
        st.markdown(
            """
            <style>
            .stApp {
                background-image: none;
                background-color: white;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.session_state['page'] == 'dashboard':
            crop_recommendation_dashboard()
        elif st.session_state['page'] == 'crop_details':
            display_crop_details(st.session_state['recommended_crop'])


if __name__ == "__main__":
    main()