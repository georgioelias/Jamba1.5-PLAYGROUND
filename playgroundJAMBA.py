import streamlit as st
import os
from ai21 import AI21Client
from ai21.models.chat import ChatMessage
import requests

# Initialize the AI21 client
st.secrets["AI21_API_KEY"]  # Use Streamlit secrets for API key

client = AI21Client(api_key=api_key)

# Streamlit app
st.title("AI21 Chat App")

# Sidebar for user inputs
st.sidebar.header("Chat Settings")
system_prompt = st.sidebar.text_area("System Prompt", "You are a helpful AI assistant.")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
max_tokens = st.sidebar.number_input("Max Tokens", 1, 1000, 250)
model = st.sidebar.selectbox("Model", ["jamba-1.5-mini", "jamba-1.5-large"])

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        ChatMessage(role="system", content=system_prompt)
    ]

# Display chat messages
for message in st.session_state.messages[1:]:  # Skip the system message
    with st.chat_message(message.role):
        st.write(message.content)

# User input
user_input = st.chat_input("Your message")

if user_input:
    # Add user message to chat history
    st.session_state.messages.append(ChatMessage(role="user", content=user_input))
    
    with st.chat_message("user"):
        st.write(user_input)

    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            full_response = response.choices[0].message.content
            message_placeholder.markdown(full_response)
        except requests.exceptions.RequestException as e:
            st.error(f"Network error: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            if hasattr(e, 'response'):
                st.error(f"Response content: {e.response.content}")

    # Add AI response to chat history
    if full_response:
        st.session_state.messages.append(ChatMessage(role="assistant", content=full_response))

# Display the current system prompt
st.sidebar.text_area("Current System Prompt", st.session_state.messages[0].content, disabled=True)

# Button to update system prompt
if st.sidebar.button("Update System Prompt"):
    st.session_state.messages[0] = ChatMessage(role="system", content=system_prompt)
    st.sidebar.success("System prompt updated!")

# Display API key status
if api_key:
    st.sidebar.success("API Key is set")
else:
    st.sidebar.error("API Key is not set")