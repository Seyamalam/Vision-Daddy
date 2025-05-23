\
import os
import requests
import cv2
import numpy as np
import google.generativeai as genai
from flask import Flask, render_template, Response, request, jsonify
from dotenv import load_dotenv
import threading
import time

load_dotenv()

genai.configure(api_key=os.environ.get(\'GENAI_API_KEY\'))

app = Flask(__name__)

# Global variable to store the ESP32-CAM URL
ESP32_CAM_URL = os.environ.get(\'ESP32_CAM_URL\', "http://<your-esp32-cam-ip-here>") # Replace with your ESP32-CAM IP or set as ENV var

def fetch_esp32_stream():
    """Fetches frames from the ESP32-CAM stream."""
    while True:
        try:
            print(f"Connecting to ESP32-CAM stream at {ESP32_CAM_URL}")
            response = requests.get(ESP32_CAM_URL, stream=True, timeout=10)
            if response.status_code == 200:
                print(f"Connected to ESP32-CAM stream at {ESP32_CAM_URL}")
                bytes_data = bytes()
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    a = bytes_data.find(b\'\\xff\\xd8\') # JPEG start
                    b = bytes_data.find(b\'\\xff\\xd9\') # JPEG end
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        # Yield the frame for the Response object
                        yield (b\'--frame\\r\\n\'
                               b\'Content-Type: image/jpeg\\r\\n\\r\\n\' + jpg + b\'\\r\\n\')
            else:
                print(f"ESP32-CAM stream error: {response.status_code}")
                time.sleep(5) # Wait before retrying
        except requests.exceptions.RequestException as e:
            print(f"ESP32-CAM connection error: {str(e)}")
            time.sleep(5) # Wait before retrying
        except Exception as e:
            print(f"Unexpected error in ESP32-CAM stream: {str(e)}")
            time.sleep(5)

@app.route(\'/\')
def index():
    """Serves the main HTML page."""
    return render_template(\'index.html\')

@app.route(\'/video_feed\')
def video_feed():
    """Provides the ESP32-CAM video stream."""
    if not ESP32_CAM_URL or ESP32_CAM_URL == "http://<your-esp32-cam-ip-here>":
        return "ESP32_CAM_URL not configured.", 500
    return Response(fetch_esp32_stream(),
                    mimetype=\'multipart/x-mixed-replace; boundary=frame\')

@app.route(\'/v1/chat/completions\', methods=[\'POST\'])
def chat_completions():
    """Handles AI image description requests."""
    data = request.json
    instruction = "Describe the image." # Default instruction or could be passed from frontend
    image_base64 = None

    if data and \'messages\' in data:
        for message in data[\'messages\']:
            if message[\'role\'] == \'user\' and isinstance(message[\'content\'], list):
                for content_item in message[\'content\']:
                    if content_item[\'type\'] == \'text\':
                        instruction = content_item[\'text\'] # Allow overriding instruction
                    elif content_item[\'type\'] == \'image_url\' and \'image_url\' in content_item:
                        image_base64 = content_item[\'image_url\'][\'url\']
                        # The image_base64 is expected to be a data URL, e.g., "data:image/jpeg;base64,..."
                        # We need to extract the actual base64 part.
                        if \';base64,\' in image_base64:
                            image_base64 = image_base64.split(\';base64,\')[1]


    if not image_base64:
        return jsonify({"error": "No image data provided"}), 400
    if not genai.api_key:
         return jsonify({"error": "GENAI_API_KEY not configured on the server."}), 500

    try:
        # Convert base64 to image bytes for Google AI
        # Google AI SDK expects image bytes or a file path.
        # For base64, we need to decode it.
        # However, the SDK\'s upload_file directly supports PIL Images or file paths.
        # A simpler way for direct bytes is to use the generative model with ImagePart.
        import base64
        image_bytes = base64.b64decode(image_base64)
        
        # Using a temporary file as upload_file is more straightforward with current genai SDK
        temp_image_path = "temp_uploaded_image.jpg"
        with open(temp_image_path, "wb") as f:
            f.write(image_bytes)

        print(f"Instruction: {instruction}")
        print(f"Image received, size: {len(image_bytes)} bytes")

        gemini_file = genai.upload_file(path=temp_image_path, display_name="User Uploaded Image")
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Ensure the prompt structure matches what the model expects
        # For gemini-1.5-flash, you can send the image and text in a list
        response = model.generate_content([instruction, gemini_file])
        
        # Clean up the temporary file
        os.remove(temp_image_path)
        genai.delete_file(gemini_file.name)


        if response and response.text:
            return jsonify({"choices": [{"message": {"content": response.text}}]})
        else:
            # Try to get more detailed error if available
            error_message = "AI service returned an empty response."
            if response and hasattr(response, \'prompt_feedback\') and response.prompt_feedback:
                error_message += f" Prompt feedback: {response.prompt_feedback}"
            return jsonify({"error": error_message}), 500

    except Exception as e:
        print(f"Error during AI content generation: {str(e)}")
        # Clean up temp file in case of error too
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        if \'gemini_file\' in locals() and gemini_file:
             try:
                genai.delete_file(gemini_file.name)
             except Exception as del_e:
                print(f"Error deleting temp genai file: {del_e}")
        return jsonify({"error": f"Failed to generate content: {str(e)}"}), 500

if __name__ == \'__main__\':
    # Make sure to create a .env file with your GENAI_API_KEY and optionally ESP32_CAM_URL
    # Example .env:
    # GENAI_API_KEY=your_google_ai_api_key_here
    # ESP32_CAM_URL=http://192.168.1.XX 
    app.run(debug=True, host=\'0.0.0.0\', port=8080)
