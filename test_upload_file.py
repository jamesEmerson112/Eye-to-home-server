from google import genai

import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
myfile = client.files.upload(file="images/1.jpeg")
print(f"{myfile=}")

result = client.models.generate_content(
    model="gemini-2.5-flash-preview-04-17",
    contents=[
        myfile,
        "\n\n",
        "Given this image:\n\n1. First, describe the image in at least 250 tokens\n2. Then, as a pixel art draw, re-describe the image",
    ],
)
print(f"{result.text=}")
