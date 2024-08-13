import streamlit as st
import sqlite3
import openai
from openai import OpenAI
import time
import os

# Constants
MODEL_OPTIONS = ["gpt-4o-mini", "gpt-4o", "gpt-3-5"]
PERSONAS_OPTIONS = {
    "Analytical": "Provide detailed, logical analyses.",
    "Business_Consultant": "Offer strategic business advice and insights.",
    "Chef": "Share cooking tips, recipes, and culinary advice.",
    "Code_Reviewer": "Analyze code snippets for best practices and potential bugs.",
    "Concise": "Give brief, to-the-point responses.",
    "Creative": "Offer imaginative and original responses.",
    "Default": "Act as a helpful assistant.",  # Default persona
}
TONE_OPTIONS = ["Professional", "Casual", "Friendly", "Formal", "Humorous"]
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_PERSONA = "Default"

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Database setup
def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (role TEXT, content TEXT, timestamp REAL)''')
    conn.commit()
    return conn

st.set_page_config(page_title="Chatbee🐝", page_icon="🐝")

# Cache setup
@st.cache_data(ttl=3600)
def get_openai_response(messages, model, max_tokens, temperature):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content

# Process user input
def process_user_input(prompt):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare messages for API call
    messages = [
        {"role": "system", "content": f"You are acting as a {persona_key} persona. {persona}\n\nTone: {tone}"},
        *st.session_state.messages
    ]

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        response = get_openai_response(messages, model, max_tokens, temperature)
        full_response += response
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Add AI response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # Save to database
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO messages VALUES (?, ?, ?)", ("user", prompt, time.time()))
    c.execute("INSERT INTO messages VALUES (?, ?, ?)", ("assistant", full_response, time.time()))
    conn.commit()
    conn.close()

# Sidebar configuration
with st.sidebar:
    st.markdown("<h3 style='text-align: center;'>⚙️ Configurations</h3>", unsafe_allow_html=True)

    model = st.sidebar.selectbox("Model", MODEL_OPTIONS, index=MODEL_OPTIONS.index(DEFAULT_MODEL))
    persona_key = st.sidebar.selectbox("Persona", list(PERSONAS_OPTIONS.keys()), index=list(PERSONAS_OPTIONS.keys()).index(DEFAULT_PERSONA))
    persona = PERSONAS_OPTIONS[persona_key]
    tone = st.sidebar.selectbox("Tone", TONE_OPTIONS)

    with st.sidebar.expander("Advanced Settings"):
        max_tokens = st.slider("Max Tokens", min_value=50, max_value=2000, value=150, step=50)
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)

    st.sidebar.markdown("---")  # Add a separator
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main chat window
st.markdown('<h1 style="text-align: center; color: #6ca395;">Chatbee🐝</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #FF0000;">always at your service</p>', unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Hello, how can I help you?"):
    process_user_input(prompt)
