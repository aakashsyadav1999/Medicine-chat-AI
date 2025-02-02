import streamlit as st
import os
import json
from PIL import Image
from src.components.main_script import MainScript

# Initialize the MainScript instance
bot = MainScript()

# Set page configuration
st.set_page_config(
    page_title="Medicine Chat AI Bot",
    page_icon="🧠",
    layout="wide"
)

# Define conversation memory
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []

# App Title
st.title("🧠 Medicine Chat AI")
st.markdown("A bot to assist with medicine-related queries.")

# Chat Display Area
st.markdown(
    """
    <style>
    .chat-card {background-color: #1e1e2f; color: white; border-radius: 10px; padding: 10px; margin-bottom: 8px;}
    .chat-user {background-color: #2b2b4f;}
    .chat-bot {background-color: #3a3a5c;}
    </style>
    """,
    unsafe_allow_html=True,
)

for role, content in st.session_state.conversation_history:
    user_style = "chat-card chat-user" if role == "user" else "chat-card chat-bot"
    st.markdown(f"<div class='{user_style}'>{content}</div>", unsafe_allow_html=True)

# User input at the bottom
input_container = st.empty()
user_input = input_container.text_area("Type your query here:", height=68)

# Image file uploader
uploaded_image = st.file_uploader("Upload an image for analysis (optional):", type=["jpg", "jpeg", "png"])

# Handle image encoding
encoded_image = None
if uploaded_image is not None:
    image_dir = "temp_image"
    os.makedirs(image_dir, exist_ok=True)

    image_path = os.path.join(image_dir, uploaded_image.name)
    with open(image_path, "wb") as f:
        f.write(uploaded_image.read())

    try:
        encoded_image = bot.encode_image(image_path)
        if not encoded_image:
            st.warning("Failed to encode the image.")
    except Exception as e:
        st.error(f"Image encoding failed: {e}")

# Send button
if st.button("Send") and user_input:
    st.session_state.conversation_history.append(("user", user_input))

    content_parts = [{"text": user_input}]
    if encoded_image:
        content_parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})

    generate_request = bot.build_generate_request(content_parts)

    try:
        with st.spinner("Thinking..."):
            raw_response = bot.generate_llm_response(generate_request)
            if raw_response:
                parsed_response = bot.parse_response(raw_response)
                if parsed_response:
                    st.session_state.conversation_history.append(("assistant", json.dumps(parsed_response, indent=4)))
                else:
                    st.error("Parsing the LLM response failed.")
            else:
                st.error("No response from LLM.")
    except Exception as e:
        st.error(f"Unexpected error during request: {e}")

    # Refresh the page to show new messages
    st.rerun()

# Clear conversation button
if st.button("Clear Conversation"):
    st.session_state.conversation_history = []
    st.success("Conversation cleared.")
    st.rerun()
