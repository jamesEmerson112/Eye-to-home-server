import requests
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_key = os.environ.get("FREEPIK_API_KEY")
    with open("output/2.txt", "r", encoding="utf-8") as f:
        prompt = f.read()
    print("Prompt being sent:")
    print(prompt)
    # Minimal payload for debugging
    payload = {
        "prompt": prompt,
        "resolution": "2k",
        "aspect_ratio": "square_1_1"
    }
    print("Payload being sent:")
    print(payload)
    headers = {
        "x-freepik-api-key": api_key,
        "Content-Type": "application/json"
    }
    url = "https://api.freepik.com/v1/ai/mystic"
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        api_result = response.json()
        print("API result:")
        print(api_result)
        # Write result to output/result.html for visual inspection
        html_template_path = "output/result.html"
        try:
            with open(html_template_path, "r", encoding="utf-8") as f:
                html_content = f.read()
            # Replace the apiResult variable in the HTML with the new result
            import json
            import re
            new_json = json.dumps(api_result, indent=4)
            html_content = re.sub(
                r"(const apiResult = )\{.*?\};",
                f"\\1{new_json};",
                html_content,
                flags=re.DOTALL
            )
            with open(html_template_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"Updated {html_template_path} with the latest API result.")
        except Exception as e:
            print(f"Failed to update {html_template_path}: {e}")
    except Exception as e:
        print("API error:")
        print(str(e))

if __name__ == "__main__":
    main()
