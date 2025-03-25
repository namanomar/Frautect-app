import streamlit as st
import re
import time
from pipeline import detect_fraud

# Extract App ID from Google Play Store URL
def extract_app_id(play_store_url):
    match = re.search(r"id=([a-zA-Z0-9._-]+)", play_store_url)
    return match.group(1) if match else None

# Streamlit App UI
def main():
    st.set_page_config(page_title="Frautecl ", layout="centered")

    # Header with an Image
    st.image("https://www.gstatic.com/android/market_images/web/play_prism_hlock_2x.png", width=120)
    st.title("🔍 Google Play Store Fraud Detection")
    st.markdown("### Detect fraudulent apps using AI-powered analysis.")

    # Input Field
    play_store_url = st.text_input("📌 Enter the Google Play Store URL:")

    # Button to trigger fraud detection
    if st.button("🚀 Check Fraud"):
        if not play_store_url:
            st.error("❌ Please enter a Google Play Store URL.")
            return

        app_id = extract_app_id(play_store_url)
        if not app_id:
            st.error("❌ Invalid Google Play Store URL. Please check the link.")
            return
        

        # Run fraud detection
        result = detect_fraud(app_id)

        # Display Results with a Success/Warning/Error Indicator
        st.subheader("✅ Fraud Detection Result")

        if result["type"] == "fraud":
            st.error(f"🚨 This app is **FRAUDULENT!**\n\n🔍 **Reason:** {result['reason']}")
        elif result["type"] == "suspected":
            st.warning(f"⚠️ This app is **SUSPECTED of fraud!**\n\n🔍 **Reason:** {result['reason']}")
        else:
            st.success(f"✅ This app is **GENUINE!**\n\n🔍 **Reason:** {result['reason']}")

if __name__ == "__main__":
    main()
