from langchain_ollama import OllamaLLM

# Initialize the LLM with specific options
llm = OllamaLLM(
    model="qwen3:0.6b",
)

# Generate text from a prompt
text = """
write a program to read excel file using python pandas
"""

response = llm.invoke(text)
print(response)
