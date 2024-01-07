import streamlit as st
from PIL import Image
import io
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCFPALEVIiwvWSREvVdBOzNd1VeyqQWt9o")

# Set up the model
generation_config = {
    "temperature": 0.4,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 4096,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

model = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Function to handle file upload and model response
def generate_gemini_response(image_bytes):
    image_prompt = input_image_setup(image_bytes)
    prompt_parts = [input_prompt, image_prompt[0]]

    # Generate response in English
    response_en = model.generate_content(prompt_parts)

    # Generate response in Arabic
    response_ar = model.generate_content(prompt_parts, lang="ar")

    return response_en.text, response_ar.text

def input_image_setup(image_bytes):
    image_parts = [{"mime_type": "image/jpeg", "data": image_bytes}]
    return image_parts

# Display header
st.set_page_config(
    page_title="ُEDA AI Chat",
    page_icon="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png",
    layout="wide",
)
st.markdown('''
<img src="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png" width="250" height="100">''', unsafe_allow_html=True)
st.markdown('''
Powered by Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20"> Streamlit <img src="https://global.discourse-cdn.com/business7/uploads/streamlit/original/2X/f/f0d0d26db1f2d99da8472951c60e5a1b782eb6fe.png" width="22" height="22"> Python <img src="https://png2.cleanpng.com/sh/38d322d41e2d6d5738e129190b8c33a7/L0KzQYq3VsI0N5Ruf5H0aYP2gLBuTgB6fJl0hp9sb33zhcXskr1qa5Dzi595cnBqgrL0jflvb15xedDwdXHqdX7smPVkfaVmRadtMHazcbKAg8c5bpM4RqI9MUS7Q4e4UcU3OWM7TqoANUi0R4W1kP5o/kisspng-python-computer-icons-programming-language-executa-5d0f0aa7c78fb3.0414836115612668558174.png" width="22" height="22">''', unsafe_allow_html=True)

# File upload and response display
uploaded_file = st.file_uploader(label="Upload an image of your food", type=["jpg", "jpeg", "png"])

if uploaded_file:
    try:
        # Convert PIL Image to bytes
        image_bytes = uploaded_file.read()
        response_en, response_ar = generate_gemini_response(image_bytes)
        st.text("Uploaded File: " + uploaded_file.name)

        if lang == 'English':
            st.text("Generated Response:")
            st.write(response_en)
        else:
            st.text("الاستجابة الناتجة:")
            st.write(response_ar)
    except Exception as e:
        st.error(f"Error processing image: {e}")
