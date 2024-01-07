import streamlit as st
from pathlib import Path
from PIL import Image
import google.generativeai as genai

# Configure the API key
genai.configure(api_key="AIzaSyCFPALEVIiwvWSREvVdBOzNd1VeyqQWt9o")

@st.cache_resource
def load_image_model() -> genai.GenerativeModel:
    """
    The function `load_image_model()` returns an instance of the `genai.GenerativeModel` class initialized with the model name
    'gemini-pro-vision'.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro-vision')
    return model

@st.cache_resource
def load_text_model() -> genai.GenerativeModel:
    """
    The function `load_text_model()` returns an instance of the `genai.GenerativeModel` class initialized with the model name
    'gemini-pro'.
    :return: an instance of the `genai.GenerativeModel` class.
    """
    model = genai.GenerativeModel('gemini-pro')
    return model

# Set up the models
image_generation_model = load_image_model()
text_generation_model = load_text_model()

# Define input prompt globally
input_prompt = """
               As an expert specializing in assessing the suitability of fruits and foods for individuals with diabetes, your task involves analyzing input text or images featuring various food items. Your first objective is to identify the type of fruit or food present. Subsequently, you must determine the glycemic index of the identified item. Based on this glycemic index, provide recommendations on whether individuals with diabetes can include the detected food in their diet. If the food is deemed suitable, specify the recommended quantity for consumption. Use English and Arabic languages for the response.
               """

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

def generate_gemini_image_response(uploaded_file):
    image_prompt = input_image_setup(uploaded_file)
    if image_prompt:
        prompt_parts = [input_prompt, image_prompt[0]]
        
        try:
            response = image_generation_model.generate_content(prompt_parts)
            return response.text
        except Exception as e:
            st.error(f"Error generating image response: {e}")
            return None

    return None

def generate_gemini_text_response(text_input, lang="en"):
    text_prompt = f"{input_prompt}\n{text_input}"
    try:
        response = text_generation_model.generate_content([text_prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating text response: {e}")
        return None

st.title("EDA AI Chat")

st.markdown('''
<img src="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png" width="250" height="100">''', unsafe_allow_html=True)

st.markdown('''
Powered by Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20"> Streamlit <img src="https://global.discourse-cdn.com/business7/uploads/streamlit/original/2X/f/f0d0d26db1f2d99da8472951c60e5a1b782eb6fe.png" width="22" height="22"> Python <img src= "https://i.ibb.co/wwCs096/nn-1-removebg-preview-removebg-preview.png" width="22" height="22">''', unsafe_allow_html=True)

# Input section
st.subheader("Text Input")
text_input = st.text_input("Enter text:")
if st.button("Generate Text Response"):
    text_response = generate_gemini_text_response(text_input)
    if text_response:
        st.success("Text Response generated successfully!")
        st.write(text_response)

st.subheader("Image Input")
uploaded_image = st.file_uploader("Upload an image of your food", type=["jpg", "jpeg", "png"])
if uploaded_image:
    if st.button("Generate Image Response"):
        image_response = generate_gemini_image_response(uploaded_image)
        if image_response:
            st.success("Image Response generated successfully!")
            st.write(image_response)
