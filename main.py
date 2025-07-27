from dotenv import load_dotenv
import os
import streamlit as st
from PIL import Image
import base64
import requests
import pandas as pd
from fpdf import FPDF  # Use fpdf2 instead of fpdf
import smtplib
from gtts import gTTS
from tempfile import NamedTemporaryFile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from groq import Groq

# Load environment variables (for local development)
load_dotenv()

# Verify environment variables
print("Email:", repr(os.environ['GMAIL_ADDRESS']))
print("Password:", repr(os.environ['GMAIL_APP_PASSWORD']))
print("Geoapify Key:", repr(os.environ['GEOAPIFY_KEY']))
print("Groq Key:", repr(os.environ['GROQ_API_KEY']))

# Optional: List files in the current directory (only for local testing)

    



if os.getenv('LOCAL_DEV'):
    print("Files in project directory:", os.listdir('.'))

# === Full Working Code with Fixed PDF Generation, Email, Theme Toggle ===

# import streamlit as st
# from PIL import Image
# import base64
# import re
# import requests
# import pandas as pd
# from fpdf import FPDF
# import smtplib
# import os
# from gtts import gTTS
# from tempfile import NamedTemporaryFile
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.base import MIMEBase
# from email import encoders
# from groq import Groq

# -------------------- PDF Class -------------------- #
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_font("Arial", size=14)

    def add_unicode_text(self, text):
        self.multi_cell(0, 10, text)

# -------------------- Setup Groq API -------------------- #
groq_api_key = os.environ['GROQ_API_KEY']
client = Groq(api_key=groq_api_key)

# -------------------- LLM Function -------------------- #
def ask_groq(user_input):
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content

# -------------------- Theme Styling -------------------- #
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

theme = st.session_state.theme
if theme == "dark":
    bg_color = "#121212"
    text_color = "#FFFFFF"
    header_color = "#5B0C86"
    card_color = "#1e1e26"
    input_color = "#2d2d39"
    result_color = "#2A2A2D"
    border_color = "#ff00ff"
    button_color = "#ffffff"
    button_text = "#6a1b9a"
    placeholder_color = "#AAAAAA"
    shadow = "0 4px 6px rgba(0, 0, 0, 0.1)"
else:
    bg_color = "#f5f5f5"
    text_color = "#000000"
    header_color = "#e1bee7"
    result_color = "#f7eeee"
    card_color = "#ffffff"
    input_color = "#fdfdfd"
    border_color = "#ba68c8"
    button_color = "#ce93d8"
    button_text = "#000000"
    placeholder_color = "#000000"
    shadow = "0 4px 6px rgba(0, 0, 0, 0.1)"

# -------------------- Utility -------------------- #
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# -------------------- UI & Styling -------------------- #
st.set_page_config(page_title="HealthCare AI Assistant", page_icon="🩺", layout="wide")

logo_base64 = get_base64_image("logo.png") if os.path.exists("logo.png") else ""
gif_base64 = get_base64_image("Online Doctor.gif") if os.path.exists("Online Doctor.gif") else ""

toggle_label = "🌞 Light Mode" if theme == "dark" else "🌙 Dark Mode"

st.markdown(f"""
    <style>
        html, body, [data-testid="stAppViewContainer"], .main, .block-container {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        .block-container {{ padding-top: 6rem !important; }}
        #MainMenu, footer, header {{ visibility: hidden; }}
        .custom-header {{
            position: fixed; top: 0; left: 0; right: 0; height: 60px;
            background-color: {header_color}; color: {text_color};
            padding: 0 2rem; z-index: 9999;
            display: flex; align-items: center; justify-content: space-between;
        }}
        .custom-header-title {{ font-size: 1.4rem; font-weight: bold; }}
        .stButton>button, .stDownloadButton>button {{
            background-color: {button_color} !important;
            color: {button_text} !important;
            font-weight: bold; border: none; padding: 8px 16px;
            border-radius: 6px; box-shadow: {shadow};
            transition: all 0.3s ease-in-out;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{
            transform: scale(1.05);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.25);
        }}
        .result-container {{
            background-color: {result_color};
            padding: 15px; border-radius: 10px; margin-top: 10px;
            box-shadow: 0px 4px 16px rgba(0, 0, 0, 0.2);
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="custom-header">
        <div class="custom-header-title">🩺 HealthCare AI Assistant</div>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button(toggle_label):
        st.session_state.theme = "light" if theme == "dark" else "dark"
        st.rerun()

# Doctor GIF
if gif_base64:
    st.markdown(f"""
        <div style="text-align:center; margin-top:20px;">
            <img src="data:image/gif;base64,{gif_base64}" style="max-width:280px;"/>
        </div>
    """, unsafe_allow_html=True)

# Main Card
st.markdown(f"<div style='background-color:{card_color}; color:{text_color}; padding:2rem; border-radius:20px;'>", unsafe_allow_html=True)
st.subheader("Enter Symptoms or Health Concern")

symptoms = st.text_area("Describe your issue", placeholder="e.g. skin rash, fatigue, fever...", height=150)
if st.button("Analyze Symptoms"):
    if not symptoms.strip():
        st.warning("⚠️ Please describe your symptoms.")
    else:
        llm_response = ask_groq(symptoms)
        st.session_state.llm_response = llm_response
        st.session_state.pdf_generated = False
        st.success("✅ Analysis Complete!")

if "llm_response" in st.session_state:
    st.markdown(f"""
        <div class="result-container">
            <p><strong>AI Response:</strong> {st.session_state.llm_response}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("📝 Generate PDF"):
        try:
            pdf = PDF()
            pdf.add_unicode_text(st.session_state.llm_response)
            pdf_path = "report.pdf"
            pdf.output(pdf_path)
            st.session_state.pdf_generated = True
            st.session_state.pdf_path = pdf_path
            st.success("✅ PDF generated successfully!")
        except Exception as e:
            st.error(f"❌ Failed to generate PDF: {e}")

if st.session_state.get("pdf_generated", False):
    with open(st.session_state.pdf_path, "rb") as f:
        st.download_button("⬇️ Download PDF", f, file_name="healthcare_report.pdf", mime="application/pdf")

    email = st.text_input("📧 Enter Email to Send PDF", placeholder="you@example.com")
    if st.button("📤 Send PDF to Email") and email.strip():
        try:
            with open(st.session_state.pdf_path, 'rb') as f:
                pdf_binary_data = f.read()

            sender_email = os.environ['GMAIL_ADDRESS']
            app_password = os.environ['GMAIL_APP_PASSWORD']

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email.strip()
            msg['Subject'] = "Your Healthcare Report"
            msg.attach(MIMEText("Attached is your AI-generated healthcare report.", 'plain'))

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(pdf_binary_data)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename=healthcare_report.pdf')
            msg.attach(part)

            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender_email, app_password)
            server.sendmail(sender_email, email.strip(), msg.as_string())
            server.quit()
            st.success(f"✅ PDF sent to {email.strip()} successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")

st.markdown("</div>", unsafe_allow_html=True)

# -------------------- Hospital APIs -------------------- #
def geocode_address(address, api_key):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            lat = data["features"][0]["properties"]["lat"]
            lon = data["features"][0]["properties"]["lon"]
            return lat, lon
    return None, None

def find_nearby_hospitals(lat, lon, api_key):
    url = f"https://api.geoapify.com/v2/places?categories=healthcare.hospital&filter=circle:{lon},{lat},35000&limit=10&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def get_route_distance(start_lat, start_lon, end_lat, end_lon, api_key):
    url = f"https://api.geoapify.com/v1/routing?waypoints={start_lat},{start_lon}|{end_lat},{end_lon}&mode=drive&details=route_details&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            return data["features"][0]["properties"]["distance"] / 1000
    return None

def display_hospitals(hospitals, start_lat, start_lon, api_key):
    data = []
    for hospital in hospitals["features"]:
        props = hospital["properties"]
        name = props.get("name", "Unknown")
        address = props.get("formatted", "No address available")
        hospital_lat, hospital_lon = props["lat"], props["lon"]
        route_distance = get_route_distance(start_lat, start_lon, hospital_lat, hospital_lon, api_key)
        data.append({
            "Name": name,
            "Address": address,
            "Driving Distance (km)": route_distance if route_distance else "N/A",
            "Coordinates": f"({hospital_lat}, {hospital_lon})"
        })
    df = pd.DataFrame(data)
    st.subheader("🏥 Nearby Hospitals")
    st.dataframe(df)

# -------------------- Optional: Hospital Finder -------------------- #
st.markdown(f"<div style='background-color:{card_color}; color:{text_color}; padding:1.5rem; border-radius:15px; margin-top:30px;'>", unsafe_allow_html=True)

st.subheader("🏥 Find Nearby Hospitals (Optional)")
api_key = os.environ['GEOAPIFY_KEY']

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    location_input = st.text_input("Enter your city or address:", placeholder="e.g. Mughalpura, Lahore, Pakistan")

with col_h2:
    st.markdown("<div style='margin-top: 26px;'>", unsafe_allow_html=True)
    search_clicked = st.button("🔍 Search Hospitals")
    st.markdown("</div>", unsafe_allow_html=True)


if search_clicked and location_input:
    lat, lon = geocode_address(location_input, api_key)
    if lat and lon:
        hospitals = find_nearby_hospitals(lat, lon, api_key)
        if hospitals and hospitals.get("features"):
            display_hospitals(hospitals, lat, lon, api_key)
        else:
            st.warning("⚠️ No hospitals found or API error.")
    else:
        st.error("❌ Invalid address or geocoding failed.")

st.markdown("</div>", unsafe_allow_html=True)


# Footer
st.markdown(f"""
    <p style='text-align:center;color:{text_color};margin-top:40px;'>
        © 2025 <strong>Team HealthGenix</strong>
    </p>
""", unsafe_allow_html=True)
