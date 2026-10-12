import base64
from google import genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

client = genai.Client()

# https://aistudio.google.com/docs/get-started#6-multimodal-generation
interaction = client.interactions.create(
    model="gemini-3.1-flash-image",
    input="Generate an image of a futuristic city skyline at sunset",
)

with open("generated_image.png", "wb") as f:
    f.write(base64.b64decode(interaction.output_image.data))