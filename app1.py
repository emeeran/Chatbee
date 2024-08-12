import os
import logging
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  # Import OpenAI directly
from persona import PERSONAS

# --- Load Environment Variables ---
load_dotenv()  # Load environment variables from .env file
openai_api_key = os.getenv("OPENAI_API_KEY")
if openai_api_key is None:
    st.error("OPENAI_API_KEY environment variable not set. Please check your .env file.")
    st.stop()

# --- Global Settings and Constants ---
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# --- Initialize Session State ---
def initialize_session_state():
    """Initializes session state."""
    default_values = {
        "messages": [],
        "model_params": {
            "model": "gpt-4",  # Default model
            "max_tokens": 1024,
            "temperature": 1.0,
            "top_p": 1.0,
        },
        "persona": "Default",
        "selected_tone": "Friendly",  # Default tone
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- Function to get response from OpenAI API ---
def get_openai_response(messages, model_params):
    """Gets response from OpenAI API."""
    try:
        response = OpenAI.chat.completions.create(
            model=model_params["model"],
            messages=messages,
            max_tokens=model_params["max_tokens"],
            temperature=model_params["temperature"],
            top_p=model_params["top_p"],
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return "Sorry, I encountered an error while generating a response."

# --- Main Streamlit Application ---
def main():
    """Main Streamlit app function."""
    st.set_page_config(
        page_title="Open-Chat",
        page_icon="💬",
    )

    initialize_session_state()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown(
            "<h3 style='text-align: center;'>Open-Chat Settings</h3>",
            unsafe_allow_html=True,
        )

        # Model Settings
        with st.expander("Model Settings", expanded=True):
            st.session_state.model_params["model"] = st.selectbox(
                "Choose Model:",
                options=["gpt-3.5-turbo", "gpt-4"],  # Update with GPT models
            )
            st.session_state.model_params["max_tokens"] = st.slider(
                "Max Tokens:", min_value=1, max_value=8000, value=1024, step=1
            )
            st.session_state.model_params["temperature"] = st.slider(
                "Temperature:", 0.0, 2.0, 1.0, 0.1
            )
            st.session_state.model_params["top_p"] = st.slider(
                "Top-p:", 0.0, 1.0, 1.0, 0.1
            )

            # Select Tone Drop-Down
            tone_options = ["Friendly", "Professional", "Casual", "Empathetic", "Formal"]
            st.session_state.selected_tone = st.selectbox(
                "Select Tone:",
                options=tone_options,
                index=tone_options.index("Friendly"),  # Default to Friendly
            )

        # Persona Settings
        with st.expander("Persona Settings", expanded=True):
            persona_options = list(PERSONAS.keys())
            st.session_state.persona = st.selectbox(
                "Select Persona:",
                options=persona_options,
                index=persona_options.index("Default"),
            )
            st.text_area(
                "Persona Description:",
                value=PERSONAS[st.session_state.persona],
                height=100,
                disabled=True,
            )

    # --- Main Chat Interface ---
    st.markdown(
        '<h1 style="text-align: center; color: #6ca395;">Open-Chat 💬</h1>',
        unsafe_allow_html=True,
    )

    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input
    prompt = st.chat_input("Enter your message:")
    if prompt:
        # Store user input in session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user input
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prepare the message history including the persona
        messages = [
            {"role": "system", "content": f"You are a {st.session_state.selected_tone} assistant."},
            {"role": "system", "content": PERSONAS[st.session_state.persona]},
            {"role": "user", "content": prompt},
        ] + st.session_state.messages[-5:]  # Use the last few messages for context

        # Get response from OpenAI API
        response = get_openai_response(messages, st.session_state.model_params)

        # Store assistant output in session state
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display assistant output
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()
