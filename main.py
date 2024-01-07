import streamlit as st
from PIL import Image
import google.generativeai as genai

# ... (Your existing code)

def generate_gemini_response(uploaded_file):
    image_prompt = input_image_setup(uploaded_file)
    if image_prompt:
        prompt_parts = [input_prompt, image_prompt[0]]
        
        try:
            with st.spinner("Generating response..."):
                response = model.generate_content(prompt_parts)
            return response.text
        except Exception as e:
            st.error(f"Error generating response: {e}")

    return None

# ... (Your existing code)

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

# File upload and response display
uploaded_file = st.file_uploader(label="Upload an image of your food", type=["jpg", "jpeg", "png"])

if uploaded_file:
    try:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        response = generate_gemini_response(uploaded_file)
        st.success("Response generated successfully!")
        st.write(response)
    except Exception as e:
        st.error(f"Error processing image: {e}")
