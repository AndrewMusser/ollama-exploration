from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory

class LLM():
    def __init__(self):
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an assistant, and you speak in {language}. Respond in 20 words or fewer",
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
    
    def run(self, input_text):

        response = self._runnable_with_history.invoke(
            {"language": "english", "input": input_text},
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