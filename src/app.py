import streamlit as st
from llm import LLM

# Initialize the agent
llm = LLM()

st.title("Machine Log Analyst")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):    
        response = llm.run(st.session_state.messages[-1])
        st.markdown(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})