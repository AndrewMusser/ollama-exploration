from langchain_core.prompts import ChatPromptTemplate

def create_agent():

    # Clear out all temporary data. 
    import glob
    import os
    temp_files = glob.glob('../data/*')
    for f in temp_files:
        os.remove(f)

    from langchain_community.tools.tavily_search import TavilySearchResults
    search = TavilySearchResults()

    from langchain_community.document_loaders import WebBaseLoader
    from langchain_community.vectorstores import FAISS
    from langchain_openai import OpenAIEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    loader = WebBaseLoader("https://docs.smith.langchain.com/overview")
    docs = loader.load()
    documents = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=200
    ).split_documents(docs)
    vector = FAISS.from_documents(documents, OpenAIEmbeddings())
    retriever = vector.as_retriever()

    from langchain.tools.retriever import create_retriever_tool
    retriever_tool = create_retriever_tool(
        retriever,
        "langsmith_search",
        "Search for information about LangSmith. For any questions about LangSmith, you must use this tool!",
    )

    # Import things that are needed generically
    from langchain.pydantic_v1 import BaseModel, Field
    from langchain.tools import BaseTool, StructuredTool, tool
    @tool
    def time_tool() -> str:
        """Use this tool to look up the current time on this workstation. You will need to use this tool first for any queries related to dates (i.e. last week, 2 Fridays ago, 3 days from now, etc)"""
        import datetime
        now = datetime.datetime.now()
        return str(now)

    from custom_tools import LogTool
    log_tool = LogTool()

    tools = [search, retriever_tool, time_tool, log_tool]

    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                    You are an expert capable of reporting on the status of industrial machines by reading their logs. 
                    You receive queries from users about the status of a machine within a certain timeframe, query the logs for that timeframe, and summarize the results to answer the query.
                    You must always start by determining the requested timeframe. If it is not included in the query, search through the chat_history. And if you can't find it there, ask the user for more information on the timeframe.
                    A machine can be queried by its IP address. If the user does not provide an IP address, assume 127.0.0.1. 
                """,
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    from langchain.agents import create_tool_calling_agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    from langchain.agents import AgentExecutor
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

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

    return agent_with_chat_history

def run_agent(agent, input_text):
    response = agent.invoke(
        {"input": input_text},
        # This is needed because in most real world scenarios, a session id is needed
        # It isn't really used here because we are using a simple in memory ChatMessageHistory
        config={"configurable": {"session_id": "<foo>"}},
    )
    return response["output"]

if __name__ == "__main__":
    # Example of running the agent directly from the command line
    agent = create_agent()
    print('Hi! How can I help you?')
    while True:
        input_text = input()
        print(run_agent(agent, input_text))