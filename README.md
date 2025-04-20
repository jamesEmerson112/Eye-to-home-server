# Project Workflow Overview

This project is a full-stack web application that leverages both Google Gemini and Freepik AI APIs to analyze images, generate creative pixel art, and provide a seamless user experience through a Flask backend and a dynamic HTML/JavaScript frontend.

---

## 1. Project Structure

- **app.py**: The main Flask backend, handling API routes for image analysis and image generation.
- **generate_image_impl.py**: Contains the logic for calling the Freepik text-to-image API, abstracted for maintainability and debugging.
- **templates/index.html**: The main frontend interface, allowing users to trigger analysis and image generation, and view results in real time.
- **custom_instruction.txt**: Stores the prompt/instruction template used for image analysis.
- **output/**: Stores generated outputs, such as pixel artist descriptions and HTML result files.
- **images/**: Contains sample images for analysis.

---

## 2. Environment Setup

- Environment variables (such as API keys) are loaded from `.env` using `python-dotenv`.
- Required keys include `GOOGLE_API_KEY` for Gemini and `FREEPIK_API_KEY` for Freepik.

---

## 3. Image Analysis Workflow (`/analyze-image`)

- The user interacts with the frontend and clicks an "analyze" button for a specific image.
- The frontend sends a POST request to `/analyze-image` with the image ID.
- The backend (app.py) maps the image ID to a file in the `images/` directory.
- The prompt for analysis is loaded from `custom_instruction.txt`.
- The Gemini API is called with the image and prompt, and the response is returned to the frontend.
- The pixel artist description (text after "Pixel Artist’s Vivid & Beautiful Description:") is extracted and cached in `output/{image_id}.txt` for later use.
- The frontend displays the result in markdown format using Marked.js.

---

## 4. Image Generation Workflow (`/generate_image`)

- The frontend provides a "Test Generate Image" button.
- When clicked, a POST request is sent to `/generate_image`. For testing, if no prompt is provided, the backend reads the prompt from `output/2.txt`.
- The backend calls `generate_image_impl.py`, which:
  - Loads the Freepik API key from the environment.
  - Constructs a payload for the Freepik text-to-image endpoint, specifying pixel-art styling and the prompt.
  - Sends the request and returns the API response.
- The backend returns the result to the frontend.
- The frontend checks if the response contains a base64-encoded image (`data[0].base64`). If so, it displays the image directly in the result box using a data URL. If not, it shows the task status or error.

---

## 5. Frontend Details

- The frontend is a single HTML file using vanilla JavaScript for interactivity.
- Results from `/analyze-image` are rendered as markdown for rich formatting.
- Results from `/generate_image` are displayed as images if available, or as status/error messages otherwise.
- The UI is simple, with clear buttons and result boxes for each action.

---

## 6. Error Handling and Debugging

- All API calls are wrapped in try/except blocks, and errors are returned as JSON.
- The backend prints the prompt and payload for image generation to the console for debugging.
- If the required files (e.g., prompt or image) are missing, the backend returns a clear error message.
- The frontend displays errors in the result boxes for immediate feedback.

---

## 7. Extensibility

- The backend is modular: image generation logic is separated into its own file for easy updates or replacement.
- Prompts and instructions are stored in external text files, making it easy to update them without changing code.
- The frontend is designed to be easily extended with new buttons or result sections.

---

## 8. Typical User Flow

1. The user opens the web interface.
2. The user clicks "analyze" to analyze a sample image, viewing the structured description and pixel artist description.
3. The user clicks "Test Generate Image" to generate a new pixel art image based on the cached description.
4. The generated image (if available) is displayed directly in the browser.

---

## 9. Notes

- The project is designed for rapid prototyping and experimentation with AI image analysis and generation.
- All API keys and sensitive data should be kept in the `.env` file and never committed to version control.
- The codebase is well-commented and structured for easy onboarding of new developers.

---
