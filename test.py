from google import genai

import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
myfile = client.files.upload(file="images/1.jpeg")
print(f"{myfile=}")

result = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        myfile,
        "\n\n",
        "Given this image:\n\n1. First, describe the image\n2. Then, detail the recipe to bake this item in JSON format. Include item names and quantities for the recipe",
    ],
)
print(f"{result.text=}")
