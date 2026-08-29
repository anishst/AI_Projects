"""

Prerequisites:

Librarys to install:
langchain
langchain-ollama
langchain-chroma
pandas
langchain-experimental
pypdf
ollama pull llama3.2
ollama pull mxbai-embed-large

Models to pull:
ollama pull llama3.2
ollama pull mxbai-embed-large (for embeddings)
ollam list (to see the models you have pulled)
src video:
https://www.youtube.com/watch?v=E4l91XKQSgw&t=390s

"""
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import build_or_get_retriever

def main():
    # Load vector store retriever from data folder
    retriever = build_or_get_retriever(data_folder="./data")

    # Initialize Ollama LLM
    model = OllamaLLM(model="llama3.2")

    # Define prompt template
    template = """
You are an expert assistant answering questions based on context provided from local documents.

Here is the relevant context:
{reviews}

Here is the question to answer:
{question}
"""
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    # Conversational Q&A Loop
    while True:
        print("\n-------------------------------")
        question = input("Ask your question (q to quit): ")
        if question.lower().strip() == "q":
            break

        print("\nRetrieving relevant chunks and generating response...\n")
        # Retrieve relevant semantic chunks
        retrieved_docs = retriever.invoke(question)
        # print(retrieved_docs)
        
        # Combine document contents
        context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Run chain
        result = chain.invoke({"reviews": context_text, "question": question})
        print(result)

if __name__ == "__main__":
    main()