import os
from dotenv import load_dotenv
import requests

def generate_image(prompt):
    """
    Calls the Freepik text-to-image API with the given prompt for pixel art.
    Returns the API response as a dictionary.
    """
    url = "https://api.freepik.com/v1/ai/text-to-image"

    # Load environment variables from .env (for local development and scripts)
    load_dotenv()
    # Get API key from environment variable for security
    api_key = os.environ.get("FREEPIK_API_KEY")
    if not api_key:
        return {"error": "FREEPIK_API_KEY environment variable not set."}

    # Build the payload for the new text-to-image endpoint
    payload = {
        "guidance_scale": 1,
        "image": {"size": "smartphone_horizontal_20_9"},
        "num_images": 1,
        "prompt": prompt,
        "styling": {"style": "pixel-art"},
        "realism": "true",
        "creative_detailing": 1
    }

    # Debug: print the prompt and payload
    # print("Prompt being sent to Freepik API:")
    # print(prompt)
    # print("Payload being sent to Freepik API:")
    # print(payload)

    # Set up the request headers, including the API key
    headers = {
        "x-freepik-api-key": api_key,
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request to the Freepik text-to-image API
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an error for bad HTTP status codes
        return response.json()  # Return the parsed JSON response
    except Exception as e:
        # Return any error as a dictionary
        return {"error": str(e)}
