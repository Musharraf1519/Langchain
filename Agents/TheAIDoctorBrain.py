# TheAIDoctorBrain.py

import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import base64

# --- 1. Setup and Initialization ---
# Load environment variables (OPENAI_API_KEY)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI Client
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    st.error(f"Error initializing OpenAI client. Please ensure OPENAI_API_KEY is set in your .env file. Details: {e}")
    client = None

# --- 2. Core LLM Function: Image Analysis ---

def get_image_analysis(image_path: str, user_prompt: str, model: str = "gpt-4o") -> str:
    """
    Sends the uploaded image and user prompt to the OpenAI multimodal model
    and returns the diagnostic analysis.
    """
    if not client:
        return "❌ Error: OpenAI client is not configured. Cannot process request."

    try:
        # 1. Encode the image to base64
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')

        # 2. Define the System Prompt for specialized behavior
        system_prompt = (
            "You are TheAI Doctor Brain, a highly specialized, expert medical diagnostic assistant. "
            "Your task is to analyze the provided medical image (e.g., X-ray, MRI, CT) and answer "
            "the user's diagnostic question. Structure your response clearly with the following sections: "
            "1. **Image Summary:** Briefly describe the type of image and what it generally shows. "
            "2. **Analysis:** Address the user's question directly, citing potential findings based on "
            "the visual evidence. Use clear medical terminology. "
            "3. **Disclaimer:** Always conclude with a strong reminder that this is an AI analysis and "
            "is not a substitute for a human diagnosis or professional medical advice."
        )

        # 3. Construct the API call with multimodal content
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }}
                ]}
            ],
            temperature=0.0
        )
        
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ An error occurred during API call. Please check your API key, model permissions, and image format. Details: {e}"

# --- 3. Streamlit UI ---

st.set_page_config(page_title="TheAI Doctor Brain 🧠⚕️", layout="wide")
st.title("TheAI Doctor Brain: Multimodal Medical Image Analysis")
st.markdown("Upload a medical image and ask an expert diagnostic question. Powered by **OpenAI's Multimodal LLM (GPT-4o)**.")

# Input Sections
uploaded_file = st.file_uploader("Upload Medical Image (X-ray, MRI, CT Scan, etc.)", type=["png", "jpg", "jpeg"])
st.markdown("---")
user_question = st.text_area(
    "Enter your Diagnostic Question or Analysis Request:",
    placeholder="e.g., 'Does this chest X-ray show signs of pneumonia or atelectasis? What is the finding in the lower right lobe?'",
    height=150
)

# Execution Button
if st.button("🔬 Get AI Diagnosis", type="primary") and client:
    if uploaded_file is None:
        st.error("Please upload a medical image to proceed with the analysis.")
    elif not user_question.strip():
        st.error("Please enter a clear diagnostic question.")
    else:
        # Save the uploaded file temporarily
        with st.spinner("Processing image and generating expert analysis..."):
            temp_file_path = os.path.join("/tmp", uploaded_file.name)
            if not os.path.exists("/tmp"):
                 os.makedirs("/tmp")
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Run the analysis function
            analysis_result = get_image_analysis(temp_file_path, user_question)
            
            # Clean up the temporary file (optional but good practice)
            os.remove(temp_file_path)

        st.markdown("---")
        st.subheader("✅ AI-Powered Diagnostic Report")
        st.markdown(analysis_result)
        
        # Display the uploaded image for reference in the app
        st.sidebar.markdown("## Uploaded Image")
        st.sidebar.image(uploaded_file, caption=uploaded_file.name, width='stretch')

# API Key Warning
if not client:
     st.warning("⚠️ **API Key Missing:** Please ensure your `OPENAI_API_KEY` is set in the project's `.env` file to run the application.")
