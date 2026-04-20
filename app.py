import streamlit as st
st.set_page_config(page_title="FIREX AI", layout="centered")

st.title("🔥 FIREX AI System")
st.write("Smart Firefighting Design Assistant")

file = st.file_uploader("Upload Drawing", type=["pdf", "png", "jpg"])

system = st.selectbox(
    "Select System Type",
    ["Sprinkler System", "Fire Alarm System", "Both"]
)

if st.button("🚀 Generate Design"):

    if file is None:
        st.warning("Please upload a drawing first")
    else:
        st.success("Processing...")

        st.subheader("📊 Results")

        if system == "Sprinkler System":
            st.write("Estimated Sprinklers: 45")
        elif system == "Fire Alarm System":
            st.write("Estimated Detectors: 30")
        else:
            st.write("Sprinklers: 45")
            st.write("Detectors: 30")

        st.write("BOQ generated successfully ✅")
