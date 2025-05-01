# Vision DADDY  

Vision DADDY is an innovative project that transforms the way we capture and document moments. By integrating an ESP32-CAM mounted on goggles, this system allows users to stream a live video feed and capture images effortlessly with a keystroke. The captured images are processed through the Gemmini Vision API to generate detailed descriptions, creating a virtual memory bank.  

## Features  
- **Live Video Feed**: Stream visuals from an ESP32-CAM in real-time.  
- **Instant Image Capture**: Press "c" to save an image from the feed.  
- **Image Description**: Generate meaningful descriptions via the Gemmini Vision API.  
- **Hands-Free Operation**: Capture moments without using a phone or camera.  

## Applications  
- Personal memory archival  
- Remote surveillance  
- Assistive technology for visually impaired individuals  

## How It Works  
1. **Hardware Setup**: Mount the ESP32-CAM on goggles or a suitable frame and connect it to a network.  
2. **Live Feed Streaming**: A Python script streams the live feed from the ESP32-CAM.  
3. **Image Capture**: Press "c" to capture an image from the live feed.  
4. **Description Generation**: The captured image is sent to the Gemmini Vision API, which returns a detailed description.  

## Prerequisites  
- **Hardware**:  
  - ESP32-CAM module  
  - Goggles or a mountable frame  

- **Software**:  
  - Arduino IDE (for ESP32-CAM setup)  
  - Python 3.7+  
  - Required libraries:  
    - `opencv-python`  
    - `requests`  
    - `flask`  

- **API**: Access to the Gemmini Vision API  

## Installation  
1. Clone the repository:  
   ```bash
   git clone https://github.com/Seyamalam/Vision DADDY.git
   cd Vision DADDY
   ```  
2. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```  
3. Add your Gemmini Vision API key to the `.env` file:  
   ```env
   GENAI_API_KEY="your-gemmini-api-key"
   ```  

## Usage  
1. Run the Python script:  
   ```bash
   python file_name.py
   ```  
2. View the live feed on the displayed window.  
3. Press "c" to capture an image and generate its description.  

## Future Enhancements  
- **Voice Commands**: Integrate speech-to-text functionality for hands-free control.  
- **Mobile App**: Develop a companion app for easier accessibility.  
- **API Expansion**: Support additional APIs for varied use cases.  

## Contributing  
Contributions are welcome! Here's how you can contribute:  
1. Fork the repository  
2. Create a feature branch:  
   ```bash
   git checkout -b feature-name
   ```  
3. Commit your changes:  
   ```bash
   git commit -m "Description of feature"
   ```  
4. Push to the branch:  
   ```bash
   git push origin feature-name
   ```  
5. Submit a pull request    

## Acknowledgments  
- The **Gemmini Vision API** for image description generation  
- The **OpenCV** community for their robust computer vision tools  
- The **Python** community for supporting open-source projects  