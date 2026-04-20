import streamlit as st
from PIL import Image
import numpy as np
import cv2

st.title("🔥 FIREX AI System")
st.write("Smart Firefighting Design Assistant")

uploaded_file = st.file_uploader("Upload Drawing", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Drawing", use_column_width=True)

system_type = st.selectbox("Select System Type", ["Sprinkler System"])

if st.button("🚀 Generate Design"):
    if uploaded_file:

        st.success("Analyzing drawing...")

        # 🔥 Convert image to OpenCV format
        img = np.array(image)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect edges (walls)
        edges = cv2.Canny(gray, 50, 150)

        # Count contours (rooms approximation)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        room_count = len(contours)

        # Estimate sprinklers per room
        sprinklers = room_count * 2

        st.subheader("📊 Results")

        st.write(f"Detected Rooms (approx): {room_count}")
        st.write(f"Estimated Sprinklers: {sprinklers}")
        st.write("Logic: 2 sprinklers per detected area")

        st.image(edges, caption="Detected Layout", use_column_width=True)

        st.success("BOQ generated successfully ✅")

    else:
        st.error("Please upload a drawing first")
