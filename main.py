import streamlit as st
from PIL import Image
import google.generativeai as genai
import os

# Configure page settings - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ُEDA AI Chat",
    page_icon="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png",
    layout="wide",
)

# **IMPORTANT: Configure the API key - DOUBLE CHECK THIS!**
API_KEY = "AIzaSyDlBv9Br45qcfbzGyr3AlcScyWQo3eSOPU"  # <--- REPLACE WITH YOUR ACTUAL API KEY HERE
if not API_KEY or API_KEY == "YOUR_API_KEY":
    st.error("API key is missing or not configured. Please set your API key in the code.")
    st.stop()
genai.configure(api_key=API_KEY)

# Display header
st.markdown('''
ـــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ<img src="https://www.edaegypt.gov.eg/media/wc3lsydo/group-287.png" width="250" height="100">ــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــــ''', unsafe_allow_html=True)

st.markdown('''
EDA Nutrition Recommendation App using Google AI <img src="https://seeklogo.com/images/G/google-ai-logo-996E85F6FD-seeklogo.com.png" width="20" height="20"> | Streamlit <img src="https://streamlit.io/images/brand/streamlit-mark-color.svg" width="22" height="22"> | Python <img src="https://i.ibb.co/wwCs096/nn-1-removebg-preview-removebg-preview.png" width="22" height="22">''', unsafe_allow_html=True)

# Hardcoded list of newer Gemini models
# These are the models that should be available as of 2025
CURRENT_GEMINI_MODELS = [
    "gemini-1.5-flash",
    "gemini-1.5-pro-vision",
    "gemini-1.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-pro-vision",
    "gemini-2.0-pro"
]

# Function to verify model exists and supports image inputs
def verify_model(model_name):
    try:
        model = genai.GenerativeModel(model_name)
        # If we can create the model without error, return True
        return True
    except Exception as e:
        st.warning(f"Model {model_name} not available: {str(e)}")
        return False

# Model selection
st.subheader("Model Selection")

# Find available models from our hardcoded list
available_models = []
for model_name in CURRENT_GEMINI_MODELS:
    if verify_model(model_name):
        available_models.append(model_name)

if not available_models:
    st.error("No compatible Gemini models found with your API key. Please make sure you have access to Gemini 1.5 or 2.0 models.")
    st.stop()

# Select a model
selected_model_name = st.selectbox(
    "Select a Model:",
    available_models,
    index=0 if available_models else None,
)

st.success(f"Using model: {selected_model_name}")

# Define input prompts for different health conditions
input_prompts = {
    "diabetes": """
               As an expert specializing in assessing the suitability of fruits and foods for individuals with diabetes, your task involves analyzing input images featuring various food items. Your first objective is to identify the type of fruit or food present in the image. Subsequently, you must determine the glycemic index of the identified item. Based on this glycemic index, provide recommendations on whether individuals with diabetes can include the detected food in their diet. If the food is deemed suitable, specify the recommended quantity for consumption. Use Arabic languages for the response.
               """,
    "hypertension": """
               As an expert specializing in assessing the suitability of fruits and foods for individuals with high blood pressure (hypertension), your task involves analyzing input images featuring various food items. Your first objective is to identify the type of fruit or food present in the image. Subsequently, provide recommendations on whether individuals with hypertension can include the detected food in their diet. If the food is deemed suitable, specify the recommended quantity for consumption. Use Arabic languages for the response.
               """,
    "hypercholesterolemia": """
               As an expert specializing in assessing the suitability of fruits and foods for individuals with hypercholesterolemia, your task involves analyzing input images featuring various food items. Your first objective is to identify the type of fruit or food present in the image. Subsequently, provide recommendations on whether individuals with hypercholesterolemia can include the detected food in their diet. If the food is deemed suitable, specify the recommended quantity for consumption. Use Arabic languages for the response.
               """,
}

# Define a dictionary to map user-friendly health condition names to keys
health_conditions_map = {
    "Diabetes داء السكري": "diabetes",
    "Hypertension ارتفاع ضغط الدم": "hypertension",
    "Hypercholesterolemia ارتفاع نسبة الكوليسترول": "hypercholesterolemia",
}

def generate_gemini_response(selected_model_name, image_data, condition):
    try:
        # Initialize the model with the selected name
        model = genai.GenerativeModel(selected_model_name)
        
        # Generation config
        generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # Create prompt with image and text
        prompt = input_prompts[condition]
        
        # Simple try-except for different API versions
        try:
            response = model.generate_content(
                [prompt, image_data],
                generation_config=generation_config
            )
        except Exception as first_error:
            st.warning(f"First attempt failed: {str(first_error)}")
            # Try alternative format
            try:
                response = model.generate_content(
                    contents=[prompt, image_data],
                    generation_config=generation_config
                )
            except Exception as second_error:
                st.error(f"Both attempts failed: {str(second_error)}")
                return None

        return response.text
    except Exception as e:
        st.error(f"Error generating response with {selected_model_name}: {e}")
        return None

# Choose health condition
health_condition = st.radio("Choose a health condition:", list(health_conditions_map.keys()))

# Toggle between upload and take photo
upload_method = st.radio("Choose a method:", ("Upload a Photo", "Take a Photo"))

if upload_method == "Upload a Photo":
    # File upload and response display
    uploaded_file = st.file_uploader(label="Upload an image of your food", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        try:
            # Display the image
            img = Image.open(uploaded_file)
            st.image(img, caption="Uploaded Image", use_column_width=True)
            
            # Reset file position
            uploaded_file.seek(0)
            
            # Create the image data structure the API expects
            image_data = {
                "mime_type": uploaded_file.type,
                "data": uploaded_file.getvalue()
            }
            
            condition_key = health_conditions_map[health_condition]
            with st.spinner(f"Generating response using {selected_model_name}..."):
                response = generate_gemini_response(selected_model_name, image_data, condition_key)
            
            if response:
                st.subheader("Generated Response:")
                st.write(response)
            else:
                st.error("Failed to generate a response. Please try a different model or check your API key permissions.")

        except Exception as e:
            st.error(f"Error processing image: {e}")
else:
    # Take a photo using the camera input
    picture = st.camera_input("Take a picture")

    if picture:
        try:
            # Create the image data structure the API expects
            image_data = {
                "mime_type": "image/jpeg",
                "data": picture.getvalue()
            }
            
            condition_key = health_conditions_map[health_condition]
            with st.spinner(f"Generating response using {selected_model_name}..."):
                response = generate_gemini_response(selected_model_name, image_data, condition_key)
            
            if response:
                st.subheader("Generated Response:")
                st.write(response)
            else:
                st.error("Failed to generate a response. Please try a different model or check your API key permissions.")
        except Exception as e:
            st.error(f"Error processing image: {e}")
