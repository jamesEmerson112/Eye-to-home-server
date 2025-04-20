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
    # Accept file upload via multipart/form-data
    if "image" not in request.files:
        return jsonify({"error": "No image file uploaded."}), 400

    image_file = request.files["image"]
    if image_file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    # Save uploaded file to images/ directory
    filename = secure_filename(image_file.filename)
    images_dir = "uploads"
    os.makedirs(images_dir, exist_ok=True)
    save_path = os.path.join(images_dir, filename)
    image_file.save(save_path)

    # Read prompt from custom_instruction.txt
    try:
        with open("custom_instruction.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
    except Exception as e:
        return jsonify({"error": f"Failed to read custom_instruction.txt: {e}"}), 500

    try:
        # Upload the saved image file to Gemini API
        myfile = client.files.upload(file=save_path)
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
        output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
        pixel_desc = ""
        if marker in result.text:
            pixel_desc = result.text.split(marker, 1)[1].strip()
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(pixel_desc)

        # Delete the uploaded image after processing
        try:
            os.remove(save_path)
        except Exception as e:
            print(f"Warning: Failed to delete uploaded image {save_path}: {e}")

        return jsonify({"result": result.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

from generate_image_impl import generate_image

import glob

@app.route("/generate_image", methods=["POST"])
def generate_image_route():
    data = request.get_json(silent=True)
    prompt = None
    txt_file_used = None
    if data and "prompt" in data:
        prompt = data["prompt"]
    else:
        # Use the most recent .txt file in output/ as the prompt
        txt_files = sorted(glob.glob("output/*.txt"), key=os.path.getmtime, reverse=True)
        if txt_files:
            txt_file_used = txt_files[0]
            with open(txt_file_used, "r", encoding="utf-8") as f:
                prompt = f.read()
        else:
            return jsonify({"error": "No prompt provided and no .txt file found in output/."}), 400
    result = generate_image(prompt)
    # Remove the used .txt file after generating the image
    if txt_file_used:
        try:
            os.remove(txt_file_used)
        except Exception as e:
            print(f"Warning: Failed to delete used prompt file {txt_file_used}: {e}")
    return jsonify(result)

import threading
import time

import json

def background_generate_image_worker():
    while True:
        txt_files = sorted(glob.glob("output/*.txt"), key=os.path.getmtime, reverse=True)
        if txt_files:
            txt_file = txt_files[0]
            with open(txt_file, "r", encoding="utf-8") as f:
                prompt = f.read()
            result = generate_image(prompt)
            print(f"Processed {txt_file} with generate_image. Result: {result}")
            # Save the latest result for polling
            try:
                with open("output/generated_image.json", "w", encoding="utf-8") as out_f:
                    json.dump(result, out_f)
            except Exception as e:
                print(f"Warning: Failed to save generated image result: {e}")
            try:
                os.remove(txt_file)
            except Exception as e:
                print(f"Warning: Failed to delete used prompt file {txt_file}: {e}")
        time.sleep(5)

def background_analyze_image_worker():
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    while True:
        image_files = sorted(glob.glob(os.path.join(uploads_dir, "*.*")), key=os.path.getmtime)
        for image_path in image_files:
            filename = os.path.basename(image_path)
            print(f"Auto-analyzing uploaded image: {filename}")
            # Read prompt from custom_instruction.txt
            try:
                with open("custom_instruction.txt", "r", encoding="utf-8") as f:
                    prompt = f.read()
            except Exception as e:
                print(f"Failed to read custom_instruction.txt: {e}")
                continue
            try:
                myfile = client.files.upload(file=image_path)
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
                output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.txt")
                pixel_desc = ""
                if marker in result.text:
                    pixel_desc = result.text.split(marker, 1)[1].strip()
                    os.makedirs(output_dir, exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(pixel_desc)
                print(f"Analysis complete for {filename}. Result cached to {output_path}")
            except Exception as e:
                print(f"Error analyzing {filename}: {e}")
            # Delete the image after processing
            try:
                os.remove(image_path)
            except Exception as e:
                print(f"Warning: Failed to delete uploaded image {image_path}: {e}")
        time.sleep(5)

@app.route("/latest_generated_image", methods=["GET"])
def latest_generated_image():
    try:
        with open("output/generated_image.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"No generated image available: {e}"}), 404

if __name__ == "__main__":
    threading.Thread(target=background_generate_image_worker, daemon=True).start()
    threading.Thread(target=background_analyze_image_worker, daemon=True).start()
    app.run(debug=True, port=5001)
