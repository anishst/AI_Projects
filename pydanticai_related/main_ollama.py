from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

# 1. Configure the local Ollama model
ollama_model = OllamaModel(
    model_name='llama3.2',  # Replace with any model you have pulled in Ollama
    provider=OllamaProvider(base_url='http://localhost:11434/v1')
)

# 2. Initialize the Pydantic AI Agent
agent = Agent(
    model=ollama_model,
    system_prompt="You are a helpful, concise assistant living locally on the user's machine."
)

if __name__ == '__main__':
    # 3. Run a synchronous query against your local agent
    result = agent.run_sync('Explain what a Python dictionary is in one short sentence.')
    print("Agent Response:")
    print(result.output)