import cv2
import numpy as np
import requests
import time
import sys
import os
import threading
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ['GENAI_API_KEY'])



def fetch_stream(url):
    while True:
        try:
            print(f"Connecting to {url}")
            response = requests.get(url, stream=True, timeout=500)
            if response.status_code == 200:
                print(f"Connected to {url}")
                bytes_data = bytes()
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_data += chunk
                    a = bytes_data.find(b'\xff\xd8')
                    b = bytes_data.find(b'\xff\xd9')
                    if a != -1 and b != -1:
                        jpg = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        yield cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {str(e)}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            print("Retrying in 5 seconds...")
            time.sleep(5)

def generate_content():
    myfile = genai.upload_file("captured_image.jpg")
    model = genai.GenerativeModel("gemini-1.5-flash")
    result = model.generate_content(
        [myfile, "\n\n", "Describe the image."]
    ).text
    print(result)

def main():
    # Replace with your ESP32-CAM's IP address
    esp32_cam_url = "esp32-cam-ip-address-url"
    

    cv2.namedWindow("ESP32-CAM Stream", cv2.WINDOW_NORMAL)
    
    for frame in fetch_stream(esp32_cam_url):
        if frame is not None:
            cv2.imshow("ESP32-CAM Stream", frame)
            
        # Check for key presses
        key = cv2.waitKey(1) & 0xFF

        # Save the image when 'c' is pressed
        if key == ord('c'):
            filename = f"captured_image.jpg"
            cv2.imwrite(filename, frame)
            print(f"Image saved as {filename}")
            # Create a separate thread to handle content generation
            threading.Thread(target=generate_content).start()

        #Press 'q' to quit the video display
        if key == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()