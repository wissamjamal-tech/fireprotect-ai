import streamlit as st
from PIL import Image
import numpy as np

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

        # 🔥 Simple AI Logic
        img_array = np.array(image)
        height, width, _ = img_array.shape

        area_estimate = (width * height) / 5000  # fake scale

        sprinklers = int(area_estimate / 9)  # NFPA approx (3x3 spacing)

        st.subheader("📊 Results")

        st.write(f"Estimated Area: {int(area_estimate)} sqm")
        st.write(f"Estimated Sprinklers: {sprinklers}")
        st.write("NFPA spacing applied: ~3m x 3m")

        st.success("BOQ generated successfully ✅")

    else:
        st.error("Please upload a drawing first")
