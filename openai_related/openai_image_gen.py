from base64 import b64decode

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

PROMPT = "A super computer"

response = client.images.generate(
    model="gpt-image-2.5-flare",
    prompt=PROMPT,
)

# https://realpython.com/generate-images-openai/
# set size and quality
# quality: "low", "medium", "high", "xhigh", "max", or "auto".
# response = client.images.generate(
#     model="gpt-image-2.5-flare",
#     prompt=PROMPT,
#     size="1024x1024",
#     quality="high", 
# )

with open("super_computer.png", mode="wb") as png:
    png.write(b64decode(response.data[0].b64_json))