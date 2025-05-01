# VisionVault Project Proposal

## Introduction

VisionVault is an assistive technology system designed to empower blind and visually impaired users by providing real-time, AI-generated descriptions of their surroundings. Leveraging affordable hardware, cloud-based AI, and mobile accessibility, VisionVault aims to deliver hands-free, context-rich feedback to users in a seamless and secure manner.

## Objectives

- Enable blind users to receive instant, spoken descriptions of their environment.
- Provide a robust, extensible platform for future accessibility enhancements.
- Ensure privacy, security, and user control throughout the data flow.

## System Architecture

The proposed system consists of the following components:

```
[ESP32-CAM] --(WiFi, MJPEG HTTP Stream)--> [Python Server]
                                              |
                                              v
                                 [Gemini Vision API (cloud)]
                                              |
                                              v
                                 [Python Server: Receives Description]
                                              |
                                              v
                        [Sends Description via API/WebSocket/Push]
                                              |
                                              v
                                 [React Native App on Phone]
                                              |
                                              v
                        [Reads Description Aloud (Text-to-Speech)]
```

## Component Breakdown

### 1. ESP32-CAM
- Captures live video and streams it over WiFi as an MJPEG HTTP stream.
- Mounted on goggles or a wearable frame for hands-free operation.

### 2. Python Server
- Connects to the ESP32-CAM stream, decodes frames, and handles image capture events.
- On image capture, sends the image to the Gemini Vision API for description generation.
- Receives the description and stores it with a timestamp and metadata.
- Exposes an API/WebSocket endpoint to deliver new descriptions to the mobile app in real time.
- Handles user authentication, access control, and logging.

### 3. Gemini Vision API (Cloud)
- Receives images from the Python server.
- Generates detailed, context-aware descriptions of the images.
- Returns the description to the Python server.

### 4. React Native App (Mobile)
- Connects to the Python server via API/WebSocket.
- Receives new image descriptions in real time.
- Uses Text-to-Speech (TTS) to read descriptions aloud to the user.
- Provides a simple, accessible UI for browsing history, repeating descriptions, and adjusting preferences.
- Supports haptic and audio feedback for key events.

## Accessibility Features (from Future Plan)

- **Text-to-Speech (TTS):** All descriptions are read aloud automatically, with adjustable speech settings.
- **Voice Commands:** Users can control the app hands-free (e.g., "repeat description").
- **Audio/Haptic Cues:** Distinct sounds and vibrations for events like capture, errors, and new descriptions.
- **Contextual Descriptions:** AI provides not just object lists, but scene context and actionable information.
- **History & Recall:** Users can review or search past descriptions.
- **Customization:** Adjustable detail level, language, and notification preferences.
- **Privacy & Security:** User data is encrypted and access-controlled; users decide what is stored or shared.

## Implementation Plan

1. **ESP32-CAM Setup:**
   - Configure and mount the ESP32-CAM for reliable WiFi streaming.
2. **Python Server Development:**
   - Implement stream capture, image saving, Gemini API integration, and real-time API/WebSocket endpoints.
   - Add authentication, logging, and secure storage.
3. **Gemini Vision API Integration:**
   - Set up secure API calls and handle responses.
4. **React Native App Development:**
   - Build a simple, accessible UI with TTS and feedback features.
   - Integrate with the server for real-time updates.
5. **Testing & Iteration:**
   - Conduct user testing with blind/visually impaired users.
   - Refine features based on feedback.
6. **Deployment & Documentation:**
   - Prepare deployment scripts, user guides, and accessibility documentation.

## Conclusion

VisionVault will provide a powerful, extensible platform for blind and visually impaired users to access real-time, AI-powered scene descriptions through a secure, mobile-friendly interface. The modular architecture ensures future enhancements and integration with additional assistive technologies. 