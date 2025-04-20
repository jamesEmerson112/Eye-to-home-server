import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from google import genai

load_dotenv()

app = Flask(__name__)

# Ensure the Google API key is set
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable not set.")

client = genai.Client(api_key=GOOGLE_API_KEY)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze-image", methods=["POST"])
def analyze_image():
    data = request.get_json()
    if not data or "image_id" not in data:
        return jsonify({"error": "No image_id provided."}), 400

    image_id = str(data["image_id"])
    image_map = {
        "1": "images/1.jpeg",
        "2": "images/2.jpeg",
        "3": "images/3.jpeg"
    }
    image_path = image_map.get(image_id)
    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": f"Image {image_id} not found."}), 404

    mime_type = "image/jpeg"  # All are .jpeg

    try:
        myfile = client.files.upload(file=image_path)
        # Read prompt from custom_instruction.txt
        try:
            with open("custom_instruction.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            return jsonify({"error": f"Failed to read custom_instruction.txt: {e}"}), 500

        result = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                myfile,
                "\n\n",
                prompt,
            ],
        )

        # Extract and cache the pixel artist description
        marker = "Pixel Artist’s Vivid & Beautiful Description:"
        output_dir = "output"
        output_path = os.path.join(output_dir, f"{image_id}.txt")
        pixel_desc = ""
        if marker in result.text:
            pixel_desc = result.text.split(marker, 1)[1].strip()
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(pixel_desc)

        return jsonify({"result": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from generate_image_impl import generate_image

@app.route("/generate_image", methods=["POST"])
def generate_image_route():
    data = request.get_json(silent=True)
    prompt = None
    if data and "prompt" in data:
        prompt = data["prompt"]
    else:
        # For testing, read prompt from output/2.txt if not provided
        try:
            with open("output/2.txt", "r", encoding="utf-8") as f:
                prompt = f.read()
        except Exception as e:
            return jsonify({"error": f"Failed to read output/2.txt: {e}"}), 500
    result = generate_image(prompt)
    print(result)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
