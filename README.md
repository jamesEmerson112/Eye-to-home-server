# Eye-to-home-server

## Backend Setup (Flask)

### 1. Create and activate the virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Gemini API key
You must have a Google Gemini API key. Set it in your environment:
```bash
export GEMINI_API_KEY=your_api_key_here
```

### 4. Run the Flask app
```bash
python app.py
```

The app will be available at [http://127.0.0.1:5001](http://127.0.0.1:5001)

## Using the Gemini Image Analysis Endpoint

Send a POST request to `/analyze-image` with an image file:

```bash
curl -X POST -F "image=@path_to_your_image.jpg" http://127.0.0.1:5001/analyze-image
```

The response will contain Gemini's analysis and a pixel art prompt based on the image.
