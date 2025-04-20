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
        return jsonify({"result": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)
