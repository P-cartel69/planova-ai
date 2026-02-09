import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv
import requests
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ---------------- LOAD ENV ----------------
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
WEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")

st.set_page_config(page_title="PLANOVA AI", page_icon="🌍", layout="wide")

st.title("🌍 PLANOVA AI")
st.subheader("Intelligent AI Travel Planning Platform")

# ---------------- SESSION STATE ----------------
if "history" not in st.session_state:
    st.session_state.history = []

if "selected_trip" not in st.session_state:
    st.session_state.selected_trip = None

# ---------------- INPUT SECTION ----------------
col1, col2, col3 = st.columns(3)

with col1:
    destination = st.text_input("📍 Destination")
    days = st.number_input("🗓 Days", 1, 30, 3)

with col2:
    people = st.number_input("👥 Number of People", 1, 20, 2)
    style = st.selectbox("🌟 Travel Style", ["Budget", "Luxury", "Adventure", "Family"])

with col3:
    budget = st.number_input("💰 Total Budget (₹)", min_value=1000, value=100000)

interests = st.multiselect(
    "🎯 Interests",
    ["Food", "Adventure", "History", "Nature",
     "Nightlife", "Shopping", "Photography", "Relaxation"]
)

# ---------------- WEATHER FUNCTION ----------------
def get_weather(city):
    if not WEATHER_KEY:
        return None
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_KEY}&units=metric"
        data = requests.get(url).json()
        if data.get("main"):
            return {
                "temp": data["main"]["temp"],
                "desc": data["weather"][0]["description"]
            }
    except:
        return None

# ---------------- UNSPLASH MULTI IMAGE WITH CACHE ----------------
@st.cache_data(show_spinner=False)
def get_destination_images(place):
    if not UNSPLASH_KEY:
        return []

    try:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": place,
            "client_id": UNSPLASH_KEY,
            "per_page": 4,
            "orientation": "landscape"
        }

        response = requests.get(url, params=params).json()

        if "results" in response and len(response["results"]) > 0:
            return [img["urls"]["regular"] for img in response["results"]]

        return []
    except:
        return []

# ---------------- HOTEL LOGIC ----------------
def hotel_recommendation(style):
    if style == "Luxury":
        return "5-star premium hotels or boutique luxury stays."
    elif style == "Budget":
        return "Affordable hotels, hostels, or Airbnb stays."
    elif style == "Adventure":
        return "Eco-lodges or adventure camps."
    else:
        return "Family-friendly hotels with spacious rooms."

# ---------------- SAFE PDF GENERATION ----------------
def clean_text(text):
    return re.sub(r'<.*?>', '', text)

def create_pdf(content):
    file_path = "travel_plan.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()
    elements = []

    clean_content = clean_text(content)

    for line in clean_content.split("\n"):
        if line.strip():
            elements.append(Paragraph(line, styles["Normal"]))
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    return file_path

# ---------------- GENERATE PLAN ----------------
if st.button("🚀 Generate Advanced Travel Plan"):

    if destination:

        per_person = budget / people
        weather = get_weather(destination)
        hotel_type = hotel_recommendation(style)

        prompt = f"""
        You are a professional AI travel strategist.

        Destination: {destination}
        Days: {days}
        Total Budget: ₹{budget}
        Number of People: {people}
        Per Person Budget: ₹{per_person}
        Travel Style: {style}
        Interests: {interests}

        Provide:
        - Optimized itinerary
        - Realistic cost breakdown
        - Per-person expenses
        - Accommodation recommendation: {hotel_type}
        - Weather-aware suggestions: {weather}
        - Smart money-saving tips
        - Packing checklist
        """

        with st.spinner("🧠 Generating intelligent travel plan..."):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.6
            )

        result = response.choices[0].message.content

        trip_data = {
            "destination": destination,
            "days": days,
            "people": people,
            "budget": budget,
            "plan": result
        }

        st.session_state.history.append(trip_data)
        st.session_state.selected_trip = trip_data

# ---------------- DISPLAY SELECTED TRIP ----------------
if st.session_state.selected_trip:

    trip = st.session_state.selected_trip

    images = get_destination_images(trip["destination"])
    weather = get_weather(trip["destination"])

    # Image Gallery
    if images:
        st.markdown("### 📸 Destination Gallery")
        cols = st.columns(2)
        for i, img in enumerate(images):
            with cols[i % 2]:
                st.image(img, use_container_width=True)

    # Weather
    if weather:
        st.info(f"🌦 {trip['destination']} Weather: {weather['temp']}°C | {weather['desc']}")

    # Map
    st.markdown("### 🗺 Location Map")
    map_url = f"https://www.google.com/maps?q={trip['destination']}&output=embed"
    st.components.v1.iframe(map_url, height=400)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📌 Travel Plan", "💰 Budget Summary", "📦 Export"])

    with tab1:
        st.markdown(trip["plan"])

    with tab2:
        st.success(
            f"👥 {trip['people']} Travelers | ₹{trip['budget']} Total | ₹{int(trip['budget']/trip['people'])} Per Person"
        )

    with tab3:
        pdf = create_pdf(trip["plan"])
        with open(pdf, "rb") as f:
            st.download_button("📥 Download PDF", f, "PLANOVA_AI_Travel_Plan.pdf")

# ---------------- SIDEBAR HISTORY ----------------
st.sidebar.title("📜 Trip History")

if st.session_state.history:
    for i, trip in enumerate(st.session_state.history):
        with st.sidebar.expander(f"📍 {trip['destination']}"):
            st.write(f"🗓 Days: {trip['days']}")
            st.write(f"👥 People: {trip['people']}")
            st.write(f"💰 Budget: ₹{trip['budget']}")

            if st.button("View Trip", key=f"view_{i}"):
                st.session_state.selected_trip = trip
else:
    st.sidebar.write("No trips generated yet.")
