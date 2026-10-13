# https://pydantic.dev/docs/ai/models/ollama/
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

class WeatherReport(BaseModel):
    city: str
    temperature_celsius: float
    condition: str

ollama_model = OllamaModel(
    'llama3.2', 
    provider=OllamaProvider(base_url='http://localhost:11434/v1')
)

# Use output_type instead of result_type
weather_agent = Agent(
    model=ollama_model,
    output_type=WeatherReport,  # <-- FIX HERE
    system_prompt="Provide realistic weather data for the requested city."
)

if __name__ == '__main__':
    result = weather_agent.run_sync('How is the weather in Tokyo right now?')
    print("Structured Output Result:")
    print(result.output)
    print(f"City: {result.output.city}, Temp: {result.output.temperature_celsius}°C")