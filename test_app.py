import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Travel Planner", page_icon="🌍")

st.title("🌍 AI Travel Planner (Groq Powered)")
st.write("Plan your perfect trip in seconds ✨")

destination = st.text_input("Enter Destination")
days = st.number_input("Number of Days", min_value=1, max_value=30, step=1)
budget = st.text_input("Budget (e.g. Rs:1000)")
style = st.selectbox("Travel Style", ["Budget", "Luxury", "Adventure", "Family"])
interests = st.multiselect(
    "🎯 Select Interests",
    ["Food", "Adventure", "History", "Nature", "Nightlife", "Shopping"]
)


if st.button("Generate Travel Plan"):

    if destination and budget:

        prompt = f"""
You are an expert travel planner.

Create a detailed {days}-day travel itinerary for {destination}.

Budget: {budget}
Travel Style: {style}

Traveler interests: {interests}

Format strictly in Markdown:

# ✈️ Trip Overview

## 💰 Budget Breakdown
- Accommodation:
- Food:
- Transport:
- Activities:

## 🗓 Day-wise Itinerary

### Day 1
Morning:
Afternoon:
Evening:

(Repeat for all days)

## 🍜 Must-Try Local Foods
- Item 1
- Item 2
- Item 3

## 🎒 Packing Checklist
- Clothing
- Essentials
- Travel Documents
"""


        with st.spinner("Generating your travel plan... ✈️"):
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

        travel_plan = response.choices[0].message.content
        st.markdown(travel_plan)

    else:
        st.warning("Please enter destination and budget.")


# /*# ---------------- PDF GENERATOR ----------------
# def create_pdf(content):
#     file_path = "travel_plan.pdf"
#     doc = SimpleDocTemplate(file_path)
#     styles = getSampleStyleSheet()
#     elements = []

#     for line in content.split("\n"):
#         elements.append(Paragraph(line, styles["Normal"]))
#         elements.append(Spacer(1, 0.2 * inch))

#     doc.build(elements)
#     return file_path
# */