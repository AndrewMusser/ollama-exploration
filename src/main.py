def chat(query, engine):
    if engine == "llama":
        from langchain_community.llms import Ollama
        llm = Ollama(model="llama3.1")
        return llm.invoke(query)
    elif engine == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(api_key="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")
        return llm.invoke(query)

response = chat("What is 2 x 2?", "llama")
print(response)