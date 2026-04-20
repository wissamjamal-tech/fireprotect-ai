import streamlit as st
from PIL import Image

st.title("🔥 FIREX AI System")
st.write("Smart Firefighting Design Assistant")

uploaded_file = st.file_uploader("Upload Drawing", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Drawing", use_column_width=True)

system_type = st.selectbox("Select System Type", ["Sprinkler System"])

if st.button("🚀 Generate Design"):
    if uploaded_file:
        st.success("Processing...")

        # Fake logic (next step we upgrade it)
        st.subheader("📊 Results")

        st.write("Estimated Sprinklers: 45")
        st.write("Coverage area: Approx. 180 sqm")
        st.write("NFPA spacing applied: 3m x 3m")

        st.success("BOQ generated successfully ✅")
    else:
        st.error("Please upload a drawing first")
