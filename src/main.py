from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import RunnableSequence
import datetime
from custom_tools import LogTool, DateTimeTool
from langchain_ollama import ChatOllama

chat_history = []

def create_agent():

    # Clear out all temporary data. 
    import glob
    import os
    temp_files = glob.glob('../data/*')
    for f in temp_files:
        os.remove(f)
    
    date_time_tool = DateTimeTool()
    log_tool = LogTool()

    llm = ChatOllama(model="llama3.1", temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "you answer questions about fruit",
                # """
                #     You are an expert capable of reporting on the status of industrial machines by reading their logs.
                #     You receive four pieces of information from the user:
                #     1. A specific query about the machine status.
                #     2. The IP address of the machine. 
                #     3. A date and time range.
                #     4. The list of log entries. 
                #     You use the IP address and date and time range to parse through the log entries and answer the specific query.                    
                # """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # chain = LLMChain(llm=llm, prompt=prompt)
    sequence = prompt | llm

    from langchain_community.chat_message_histories import ChatMessageHistory
    from langchain_core.runnables.history import RunnableWithMessageHistory
    message_history = ChatMessageHistory()
    agent_with_chat_history = RunnableWithMessageHistory(
        agent_executor,
        # This is needed because in most real world scenarios, a session id is needed
        # It isn't really used here because we are using a simple in memory ChatMessageHistory
        lambda session_id: message_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )

    return sequence

# Function to format chat history into a single string
def format_chat_history(history):
    return "\n".join([f"Human: {h['human']}\nAI: {h['ai']}" for h in history])

def run_agent(agent, input_text):

    # Consolidate input information. 
    input_variables = {
        "input": input_text,
        "chat_history": chat_history,  # if you have previous history, include it here
        "agent_scratchpad": "",  # initial agent state
    }

    # Run the chain.
    response = agent.invoke(input_variables)

    # Add the latest conversation to the history
    chat_history.append({"human": input_variables['input'], "ai": response})

    return response

if __name__ == "__main__":
    # Example of running the agent directly from the command line
    agent = create_agent()
    print('Hi! How can I help you?')
    while True:
        input_text = input()
        print(run_agent(agent, input_text))