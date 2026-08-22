"""

Prerequisites:

Librarys to install:
langchain
langchain-ollama
langchain-chroma
pandas

Models to pull:
ollama pull llama3.2
ollama pull mxbai-embed-large (for embeddings)
ollam list (to see the models you have pulled)
src video:
https://www.youtube.com/watch?v=E4l91XKQSgw&t=390s

"""

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

model = OllamaLLM(model="llama3.2")

template = """
You are an exeprt in answering questions about a pizza restaurant

Here are some relevant reviews: {reviews}

Here is the question to answer: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# without retriever
# result = chain.invoke({"reviews": [], "question": "What is the best pizza in town?"})
# print(result)

# with retriever
while True:
    print("\n\n-------------------------------")
    question = input("Ask your question (q to quit): ")
    print("\n\n")
    if question == "q":
        break
    
    reviews = retriever.invoke(question)
    result = chain.invoke({"reviews": reviews, "question": question})
    print(result)