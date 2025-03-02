import streamlit as st
from PIL import Image
import google.generativeai as genai

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

# Model Selection
try:
    available_models = genai.list_models()
    gemini_vision_models = []
    gemini_text_models = [] # Fallback models if no vision models

    for model in available_models:
        model_name = model.name
        if "gemini" in model_name:
            if "vision" in model_name:
                gemini_vision_models.append(model_name)
            elif not "vision" in model_name and ("gemini-1.5" in model_name or "gemini-2.0" in model_name or "gemini-pro" in model_name): # Add gemini-pro as fallback
                gemini_text_models.append(model_name)

    if not gemini_vision_models and not gemini_text_models:
        st.error("No suitable Gemini models found with your API key/project.")
        st.stop()

    if gemini_vision_models:
        default_vision_model_index = 0
        for i, model in enumerate(gemini_vision_models):
            if "gemini-1.5-flash" in model or "gemini-2.0-flash" in model: #Prioritize flash models
                default_vision_model_index = i
                break

        st.subheader("Model Selection")
        selected_model_name = st.selectbox(
            "Select a model to use:",
            gemini_vision_models + gemini_text_models, # Combine vision and text models
            index=default_vision_model_index if gemini_vision_models else 0, # Default to vision or first text
            format_func=lambda name: f"{name} (Vision Support)" if name in gemini_vision_models else f"{name} (Text Only)"
        )

        if "gemini-pro-vision" in selected_model_name:
            st.warning("You have selected Gemini Pro Vision. Please note that `gemini-pro-vision` has been deprecated on July 12, 2024. Consider switching to a different model, for example `gemini-1.5-flash` or another model from the dropdown.")

        st.success(f"Using model: {selected_model_name}")

    else:
        st.subheader("Model Selection")
        selected_model_name = st.selectbox(
            "Select a model to use:",
            gemini_text_models,
            index=0
        )
        st.warning("No vision models available. Image analysis will be limited if you select a text-only model.")
        st.success(f"Using model: {selected_model_name} (Text Only)")


except Exception as e:
    st.error(f"Error listing models: {e}")
    st.error("Please check your API key and Google Cloud project configuration.")
    st.stop()


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

def generate_gemini_response(selected_model_name, uploaded_file, condition):
    image_prompt = input_image_setup(uploaded_file)
    if image_prompt:
        prompt_parts = [input_prompts[condition], image_prompt[0]]

        try:
            # Initialize the model with the selected name
            model = genai.GenerativeModel(selected_model_name)

            # Check if the model supports safety settings and apply if needed
            safety_settings = None
            try:
                safety_settings = {
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                }
                response = model.generate_content(
                    prompt_parts,
                    safety_settings=safety_settings
                )
            except:
                response = model.generate_content(prompt_parts) # Try without safety settings if error

            return response.text
        except Exception as e:
            st.error(f"Error generating response with {selected_model_name}: {e}")
            st.error(f"Detailed error: {str(e)}")
            if "404" in str(e) and "not found" in str(e):
                st.error(f"The model '{selected_model_name}' might not support the generateContent method or is not found.")
            elif "403" in str(e):
                st.error("Permission denied. Your API key may not have access to this model.")
            return None

    return None # Return None if image_prompt is None

# Choose health condition
health_condition = st.radio("Choose a health condition:", list(health_conditions_map.keys()))

# Toggle between upload and take photo
upload_method = st.radio("Choose a method:", ("Upload a Photo", "Take a Photo"))

if upload_method == "Upload a Photo":
    # File upload and response display
    uploaded_file = st.file_uploader(label="Upload an image of your food", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        try:
            condition_key = health_conditions_map[health_condition]
            with st.spinner(f"Generating response using {selected_model_name}..."):
                response = generate_gemini_response(selected_model_name, uploaded_file, condition_key)
            if response:
                st.text("Uploaded File: " + uploaded_file.name)
                st.subheader("Generated Response:")
                st.write(response)
            else:
                st.error("Failed to generate a response. Please check error messages above and try again or select a different model.")

        except Exception as e:
            st.error(f"Error processing image: {e}")
else:
    # Take a photo using the camera input
    picture = st.camera_input("Take a picture")

    if picture: # Only process if picture is taken
        st.image(picture, caption="Captured Photo", use_column_width=True)

        # Process the captured photo
        try:
            condition_key = health_conditions_map[health_condition]
            with st.spinner(f"Generating response using {selected_model_name}..."):
                response = generate_gemini_response(selected_model_name, picture, condition_key) # Pass picture as uploaded_file
            if response:
                st.subheader("Generated Response:")
                st.write(response)
            else:
                st.error("Failed to generate a response. Please check error messages above and try again or select a different model.")
        except Exception as e:
            st.error(f"Error processing image: {e}")
