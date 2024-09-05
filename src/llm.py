from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from custom_tools import LogTool, DateTimeTool

class LLM():
    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an expert at analyzing machine logs. You always respond consicely in 40 words or less."
                ),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )
        self._model = ChatOllama(model="llama3.1", temperature=0)
        self._runnable = self._prompt | self._model
        self._runnable_with_history = RunnableWithMessageHistory(
            self._runnable,
            self._get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def _get_session_history(self, session_id):
        return SQLChatMessageHistory(session_id, "sqlite:///../data/memory.db")
    
    def run(self, user_input):

        # Retrieve the current date and time.
        date_time_tool = DateTimeTool()
        date, time = date_time_tool.retrieve_date_and_time()

        # Retrieve the IP address of the machine.
        ip = self._model.invoke(f"""
            Please extract the IP address from the following query. 
            Return a string containing only the IP address, and nothing else.
            ### QUERY:
            {user_input}                    
        """).content

        # Retrieve the logs for the machine.
        log_tool = LogTool()
        from datetime import datetime
        logs = log_tool.run(ip)

        prompt = f"""
            ### USER QUERY:
            {user_input}

            ### CURRENT DATE: 
            {date}

            ### CURRENT TIME: 
            {time}

            ### MACHINE LOGS:
            {logs}
        """
        
        response = self._runnable_with_history.invoke(
            {"language": "english", "input": prompt},
            config={"configurable": {"session_id": "2"}},
        )
        return response.content

if __name__ == "__main__":
    # Example of running the agent directly from the command line
    llm = LLM()
    print('Hi! How can I help you?')
    while True:
        input_text = input()
        print(llm.run(input_text))