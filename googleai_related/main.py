# setup: pip install -U google-genai
# https://aistudio.google.com/learn/developer-guide-gemini-3-5-flash?utm_source=google&utm_medium=cpc&utm_campaign=Cloud-SS-DR-AIS-FY26-global-gsem-1713578&utm_content=text-ad&utm_term=KW_gemini%202.5%20flash%20image&gad_source=1&gad_campaignid=23417416052&gbraid=0AAAAACn9t66WRHje7yLtQee4T_TutP019&gclid=CjwKCAjw56zWBhB0EiwAdPOQOURAM73XRrdj993WIBmPTKvgdmsqyk2Ay6PxQhCzZd5rG4y5TQ4D8RoCFSIQAvD_BwE
# Interactions API
import os
from google import genai
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the client (it automatically detects GEMINI_API_KEY from your environment)
client = genai.Client()

# Generate text content
response = client.models.generate_content(
    model='gemini-3.8-flash',
    contents='Give me a 3-item checklist for launching a Python project.',
)

# Print the result
print(response.text)