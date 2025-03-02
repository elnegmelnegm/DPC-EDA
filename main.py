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
    # Get available models
    available_models = genai.list_models()
    
    # Define preferred model names - prioritizing newer models first
    preferred_vision_models = ["gemini-1.5-flash", "gemini-1.5-pro-vision", "gemini-2.0-flash", "gemini-2.0-pro-vision"]
    
    # Filter for vision models
    gemini_vision_models = []
    gemini_text_models = []  # Fallback models
    
    for model in available_models:
        model_name = model.name
        # Skip deprecated models explicitly
        if "gemini-1.0" in model_name:
            continue
            
        if "gemini" in model_name:
            # Check if it's a vision-capable model
            if any(capability == "generateContent" for capability in model.supported_generation_methods):
                supports_image = False
                # Check if model supports image inputs
                for input_type in getattr(model, 'input_token_types', []):
                    if 'image' in input_type.lower():
                        supports_image = True
                        break
                
                if supports_image:
                    gemini_vision_models.append(model_name)
                else:
                    gemini_text_models.append(model_name)
    
    # If no models were found with detailed check, use a simpler approach
    if not gemini_vision_models:
        gemini_vision_models = [model.name for model in available_models 
                          if "gemini" in model.name.lower() 
                          and any(pref in model.name for pref in preferred_vision_models)]
    
    # Sort models to prioritize preferred ones
    def get_model_priority(model_name):
        for i, preferred in enumerate(preferred_vision_models):
            if preferred in model_name:
                return i
        return len(preferred_vision_models)  # Lower priority for non-preferred models
    
    gemini_vision_models.sort(key=get_model_priority)
    
    # Select default model
    default_model_index = 0
    
    # Debug model lists
    with st.expander("Debug: Available Models"):
        st.write("Vision Models:", gemini_vision_models)
        st.write("Text Models:", gemini_text_models)
    
    if not gemini_vision_models and not gemini_text_models:
        st.error("No suitable Gemini models found with your API key/project. Make sure you have access to Gemini models.")
        st.stop()
    
    # Model selection UI
    st.subheader("Model Selection")
    if gemini_vision_models:
        selected_model_name = st.selectbox(
            "Select a Vision Model:",
            gemini_vision_models,
            index=default_model_index,
        )
        st.success(f"Using Vision model: {selected_model_name}")
    else:
        selected_model_name = st.selectbox(
            "Select a Text Model (No Image Analysis):",
            gemini_text_models,
            index=0
        )
        st.warning("No vision models available. Image analysis will be limited. Using text model only.")
        st.success(f"Using Text model: {selected_model_name}")

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
            {"mime_type": uploaded_file.type, "data": uploaded_file.read()}
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
            
            # Generation config
            generation_config = {
                "temperature": 0.4,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }

            # Try with safety settings first
            try:
                safety_settings = {
                    "HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
                    "HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
                    "SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
                    "DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
                }
                
                response = model.generate_content(
                    prompt_parts,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
            except Exception as safety_error:
                st.warning(f"Trying without safety settings due to: {str(safety_error)}")
                # Fallback without safety settings
                response = model.generate_content(
                    prompt_parts,
                    generation_config=generation_config
                )

            return response.text
        except Exception as e:
            st.error(f"Error generating response with {selected_model_name}: {e}")
            st.error(f"Detailed error: {str(e)}")
            if "404" in str(e) and "not found" in str(e):
                st.error(f"The model '{selected_model_name}' might not be available. Try selecting a different model.")
            elif "403" in str(e):
                st.error("Permission denied. Your API key may not have access to this model.")
            return None

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
            
            # Reset the file position after opening
            uploaded_file.seek(0)
            
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

    if picture:
        # Process the captured photo
        try:
            condition_key = health_conditions_map[health_condition]
            with st.spinner(f"Generating response using {selected_model_name}..."):
                response = generate_gemini_response(selected_model_name, picture, condition_key)
            if response:
                st.subheader("Generated Response:")
                st.write(response)
            else:
                st.error("Failed to generate a response. Please check error messages above and try again or select a different model.")
        except Exception as e:
            st.error(f"Error processing image: {e}")
