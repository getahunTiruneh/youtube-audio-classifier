# app.py
import streamlit as st
import pandas as pd
from classifier.utils import process_urls

st.set_page_config(
    page_title="YouTube Audio Classifier",
    layout="wide",
    page_icon="🎧"
)

st.title("🎧 YouTube Audio Classifier: Music or Speech")
st.markdown(
    """
    Upload a CSV file containing YouTube URLs, and this app will analyze each video to determine whether it’s **music**, **speech**, or both.
    """
)

# File Upload
uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Uploaded `{uploaded_file.name}` ({len(df)} rows)")

    url_column = st.selectbox("🔗 Select the column containing YouTube URLs:", df.columns)

    if st.button("🚀 Classify Videos"):
        urls = df[url_column].dropna().unique().tolist()
        with st.spinner("Processing videos... This may take a while ⏳"):
            result_df = process_urls(urls)
        
        st.success("🎯 Classification Complete!")
        st.dataframe(result_df)

        # Download
        st.download_button(
            label="📥 Download Classified CSV",
            data=result_df.to_csv(index=False),
            file_name="classified_videos.csv",
            mime="text/csv"
        )
else:
    st.info("👈 Upload a CSV file to get started.")
