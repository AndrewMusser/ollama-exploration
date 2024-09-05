import streamlit as st
from go import create_agent, run_agent

# Initialize the agent
agent = create_agent()

# Initialize session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state to clear the input field
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

st.title("LangChain Chat Bot")

# Input text from the user
user_input = st.text_input("You:", value=st.session_state.user_input, key="input")

if st.button("Send"):
    if user_input:
        # Add user input to chat history
        st.session_state.chat_history.append({"role": "user", "message": user_input})

        # Run the agent with the current user input and chat history
        agent_response = run_agent(agent, user_input)

        # Add agent response to chat history
        st.session_state.chat_history.append({"role": "agent", "message": agent_response})

        # Clear the input box by resetting the session state
        st.session_state.user_input = ""

# Display the chat history
st.write("Chat History:")
for exchange in st.session_state.chat_history:
    if exchange["role"] == "user":
        st.text_area("You:", value=exchange["message"], height=50, key=str(exchange) + "_user", disabled=True)
    else:
        st.text_area("Agent:", value=exchange["message"], height=50, key=str(exchange) + "_agent", disabled=True)

# Optionally, you can add a button to clear the chat history
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.session_state.user_input = ""  # Also clear the input box
