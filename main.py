import streamlit as st
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCFPALEVIiwvWSREvVdBOzNd1VeyqQWt9o")

# Set up the models
text_generation_model = genai.GenerativeModel(
    model_name="gemini-pro-text",
    generation_config={"temperature": 0.4, "top_p": 1, "top_k": 32, "max_output_tokens": 4096},
)

image_generation_model = genai.GenerativeModel(
    model_name="gemini-pro-vision",
    generation_config={"temperature": 0.4, "top_p": 1, "top_k": 32, "max_output_tokens": 4096},
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ],
)

# Define input prompt globally
input_prompt = """
               As an expert specializing in assessing the suitability of fruits and foods for individuals with diabetes, your task involves analyzing input text or images featuring various food items. Your first objective is to identify the type of fruit or food present. Subsequently, you must determine the glycemic index of the identified item. Based on this glycemic index, provide recommendations on whether individuals with diabetes can include the detected food in their diet. If the food is deemed suitable, specify the recommended quantity for consumption. Use English and Arabic languages for the response.
               """

def generate_gemini_text_response(text_input):
    prompt_parts = [input_prompt, text_input]
    try:
        response = text_generation_model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        st.error(f"Error generating text response: {e}")
        return None

def generate_gemini_image_response(image_input):
    image_prompt = input_image_setup(image_input)
    if image_prompt:
        prompt_parts = [input_prompt, image_prompt[0]]
        try:
            response = image_generation_model.generate_content(prompt_parts)
            return response.text
        except Exception as e:
            st.error(f"Error generating image response: {e}")
    return None

def input_image_setup(uploaded_file):
    if not uploaded_file:
        st.error("No file uploaded.")
        return None

    try:
        # Read the content of the uploaded file as bytes
        image_parts = [
            {"mime_type": "image/jpeg", "data": uploaded_file.read()}
        ]
        return image_parts
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        return None

# Display header
st.set_page_config(
    page_title="ُEDA AI Chat",
    page_icon="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png",
    layout="wide",
)

st.title("EDA AI Chat")

st.markdown('''
<img src="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png" width="250" height="100">''', unsafe_allow_html=True)

st.markdown('''
Powered by Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20"> Streamlit <img src="https://global.discourse-cdn.com/business7/uploads/streamlit/original/2X/f/f0d0d26db1f2d99da8472951c60e5a1b782eb6fe.png" width="22" height="22"> Python <img src= "https://i.ibb.co/wwCs096/nn-1-removebg-preview-removebg-preview.png" width="22" height="22">''', unsafe_allow_html=True)

# Input section
input_type = st.radio("Select Input Type:", ["Text Input", "Image Upload"])

if input_type == "Text Input":
    text_input = st.text_area("Enter text:")
    if st.button("Generate Response"):
        response = generate_gemini_text_response(text_input)
        if response:
            st.success("Response generated successfully!")
            st.write(response)

elif input_type == "Image Upload":
    uploaded_file = st.file_uploader(label="Upload an image of your food", type=["jpg", "jpeg", "png"])
    if uploaded_file and st.button("Generate Response"):
        response = generate_gemini_image_response(uploaded_file)
        if response:
            st.success("Response generated successfully!")
            st.write(response)
