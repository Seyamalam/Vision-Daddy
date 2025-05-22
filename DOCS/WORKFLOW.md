# VisionVault - Enhanced Workflow with Mobile App Integration

## Project Goal

To create a robust, wearable camera system using an ESP32-CAM that automatically captures scenes, analyzes them for significant changes, and provides continuous, configurable, and on-demand auditory descriptions via Text-to-Speech (TTS) on a companion mobile app with enhanced user feedback and error handling.

## Components

1.  **ESP32-CAM:**
    *   Mounted on goggles or similar headwear.
    *   Runs `camera-feed.ino` firmware (unchanged).
    *   Connects to the local WiFi network.
    *   Continuously captures video frames.
    *   Streams the video feed as MJPEG over HTTP on the local network.

2.  **Python Backend Server (Modified `take-pic.py`):**
    *   Runs on a computer connected to the same WiFi network using `asyncio` for non-blocking operations.
    *   **Connection Handling:** Attempts to continuously fetch the MJPEG stream from the ESP32-CAM's IP address, implementing **robust reconnection logic** with backoff if the stream connection fails.
    *   Runs a WebSocket server to listen for connections and commands from the mobile app(s). Manages individual client states (active/inactive, description interval).
    *   **Scene Change Detection:** Stores the last frame successfully analyzed by the API. Compares new frames against the stored frame using a defined similarity metric (e.g., SSIM).
    *   **Configurable Timer Loop:** Manages an internal state (e.g., "active" or "inactive") per client. When a client is active:
        *   A timer loop runs based on the client's configured interval (`n` seconds).
        *   On each timer tick, grabs the latest video frame.
        *   **Performs scene change check:** If the frame is too similar to the last analyzed frame, **skips the API call** for this tick to save costs and avoid redundancy.
        *   If the scene *has* changed significantly, sends the image frame to the Google Generative AI (Gemini) API.
        *   Stores the frame as the new "last analyzed frame" upon successful API response.
        *   Broadcasts the received description text via WebSocket to the specific active client.
    *   **API Error Handling:** Wraps API calls with error handling for network issues, API key problems, rate limits, etc. Communicates error status back to the relevant mobile client via WebSocket.
    *   **WebSocket Command Handling:** Listens for:
        *   `"start"`: Marks client as active, sets interval, starts timer if needed.
        *   `"stop"`: Marks client as inactive, stops timer if no clients are active.
        *   `"set_interval"`: Updates the description interval `n` for the specific client.
        *   `"describe_now"`: Immediately grabs the current frame, **bypasses the scene change check**, calls the API, and sends the description back to the requesting client.

3.  **React Native Mobile App:**
    *   Runs on the user's smartphone, connected to the same WiFi network.
    *   **Connection Handling:** Connects to the Python Backend Server using WebSockets, implementing **automatic reconnection logic** if the connection drops.
    *   **UI & Controls:**
        *   Provides "Start Describing" / "Stop Describing" buttons (or toggle).
        *   Provides controls (e.g., slider, input) to **configure the description interval `n`**.
        *   Includes a **"Describe Now" button** for on-demand analysis.
        *   Displays **status indicators** (connection status, server status, errors).
        *   Features a **scrollable description history** area showing the last few received descriptions.
    *   **WebSocket Communication:**
        *   Sends commands: `"start"`, `"stop"`, `"set_interval"` (with value), `"describe_now"`.
        *   Listens for incoming messages: `"description"` (contains text) and `"error"` or `"status"` messages from the server.
    *   **User Feedback:**
        *   Uses a Text-to-Speech (TTS) engine to read each received description aloud.
        *   Provides **haptic feedback** (vibration) when a new description message is received.
        *   Updates the description history view.
        *   Displays error messages received from the server.

4.  **Google Generative AI API:**
    *   External cloud service.
    *   Receives image data from the Python server.
    *   Analyzes the image and returns a textual description.

## Step-by-Step Workflow (Automatic Mode Example)

1.  **Initialization:**
    *   ESP32-CAM is powered on, connects to WiFi, starts streaming.
    *   Python Backend Server starts, attempts connection to ESP32 stream (retrying if needed), starts WebSocket server (inactive state).
    *   Mobile App launches, attempts WebSocket connection to Python server (retrying if needed). Displays "Disconnected" or "Connected" status.

2.  **Configuration (Optional):**
    *   User adjusts the desired description interval (e.g., sets `n=20` seconds) using the app UI.
    *   App sends `{"command": "set_interval", "value": 20}` to the server. Server acknowledges and stores the interval for this client.

3.  **User Action (Start):**
    *   User taps "Start Describing".
    *   App sends `{"command": "start"}`. Server marks client as active and starts its internal timer loop for this client (if not already running for others) using the client's interval `n`. App UI updates status to "Active".

4.  **Timer Tick & Scene Check:**
    *   The server's timer ticks for the active client.
    *   Server grabs the latest frame from the (hopefully connected) ESP32 stream.
    *   Server compares the frame to the last successfully analyzed frame for significant changes.

5.  **API Call (Conditional):**
    *   **If Scene Changed:** Server sends the frame to Google API. Handles potential API errors (sending status/error message to app if failure occurs).
    *   **If Scene NOT Changed:** Server does nothing further for this tick.

6.  **Description Broadcast & Feedback:**
    *   (If API was called and successful) Server receives the description text.
    *   Server updates its "last analyzed frame" reference.
    *   Server sends `{"type": "description", "text": "..."}` via WebSocket to the specific client.
    *   Mobile App receives the message.
    *   App triggers **haptic feedback**.
    *   App adds the description to the **history view**.
    *   App triggers **TTS** to speak the description.

7.  **(Repeat steps 4-6 every `n` seconds for active clients)**

8.  **User Action (On-Demand):**
    *   User taps "Describe Now".
    *   App sends `{"command": "describe_now"}`.
    *   Server immediately grabs frame, calls API (bypassing scene check), handles errors, receives description.
    *   Server sends description back to the requesting client.
    *   App provides haptic feedback, updates history, speaks description (as in step 6).

9.  **User Action (Stop):**
    *   User taps "Stop Describing".
    *   App sends `{"command": "stop"}`. Server marks client as inactive. If no clients remain active, the server stops the main timer loop. App UI updates status to "Inactive".

## Key Technologies

*   **Video Streaming:** MJPEG over HTTP (ESP32-CAM -> Python Server)
*   **Backend:** Python (using `asyncio`, libraries like `websockets` or framework extensions, `aiohttp` or `requests` (async variant), `opencv-python`, `scikit-image` or similar for SSIM/scene change, `google-generativeai`)
*   **Frontend:** React Native (using state management, WebSocket client library, TTS library, Haptics library)
*   **Communication:** WebSockets (Python Server <-> Mobile App)
*   **Scene Change Detection:** Image Similarity Algorithm (e.g., SSIM, histogram comparison)
*   **AI:** Google Generative AI (Gemini) API
*   **Audio Output:** Text-to-Speech (TTS) library within React Native
*   **Tactile Feedback:** Haptics API within React Native

## Security Considerations

This system involves network communication and external API calls. It's important to consider the following security aspects, especially given the potential privacy implications of a wearable camera:

1.  **Network Environment:**
    *   **Assumption:** This system is designed primarily for use on a **trusted local network** (e.g., home WiFi).
    *   **Risk:** Running on untrusted or public networks significantly increases exposure to eavesdropping and unauthorized access.
    *   **Mitigation:** Use strong WiFi security (WPA2/WPA3) on the local network. Avoid using the system on public WiFi.

2.  **ESP32 Video Stream (HTTP):**
    *   **Risk:** The MJPEG stream from the ESP32 to the Python server is unencrypted (HTTP). Anyone on the same local network could potentially intercept or view this raw video feed if they discover the ESP32's IP address.
    *   **Mitigation:** Rely on the security of the trusted local WiFi network (WPA2/WPA3) as the primary protection layer. Implementing HTTPS on the ESP32 itself is complex and resource-intensive, often impractical for this hardware.

3.  **WebSocket Communication (Python Server <-> Mobile App):**
    *   **Risk (Default):** Standard WebSockets (`ws://`) are unencrypted. Commands and descriptions could be intercepted on the local network.
    *   **Mitigation (Recommended):** Configure the Python WebSocket server to use **Secure WebSockets (`wss://`)**. This requires generating SSL/TLS certificates (e.g., self-signed for local use) for the server and configuring the React Native app to trust them. This encrypts the traffic between the app and the server.
    *   **Risk (Unauthorized Access):** Without authentication, any device on the network could connect to the WebSocket server and send commands (potentially causing DoS or exhausting API quotas) or receive description broadcasts.
    *   **Mitigation (Authentication):** Implement a simple **authentication mechanism**. For example, the app could send a pre-shared secret token upon connection, which the server validates before accepting commands (`start`, `stop`, `set_interval`, `describe_now`) or adding the client to the broadcast list. Reject connections/commands from unauthenticated clients.

4.  **API Key Security (Python Server):**
    *   **Risk:** The Google Generative AI API key is a sensitive credential.
    *   **Mitigation:** Store the API key securely using environment variables (`.env` file loaded securely) or a dedicated secrets management system. Ensure the host computer running the Python server is adequately secured against unauthorized access.

5.  **Denial of Service (DoS):**
    *   **Risk:** Malicious or malfunctioning clients could flood the server with connections or commands (especially `describe_now` or rapid `set_interval` changes).
    *   **Mitigation (Rate Limiting):** Implement **rate limiting** on the Python server for incoming WebSocket connections and commands per client/IP address.

6.  **Input Validation:**
    *   **Risk:** Malformed commands or values (e.g., non-numeric interval) could cause errors.
    *   **Mitigation:** The Python server should strictly **validate and sanitize** all inputs received via WebSocket commands before processing them.

7.  **Resource Management:**
    *   **Risk:** Improper handling of client disconnects or errors could leave resources (timers, connections) dangling.
    *   **Mitigation:** Ensure the Python server cleans up resources associated with a client (e.g., stops their timer task) when they disconnect or send a `stop` command.

## Required Changes Summary (Highlights)

*   **`take-pic.py` (Python Server):**
    *   Full `asyncio` implementation.
    *   Robust ESP32 stream connection/reconnection logic.
    *   WebSocket server handling connect/disconnect, detailed command parsing (`start`, `stop`, `set_interval`, `describe_now`).
    *   Implement scene change detection logic (store last frame, compare new frames).
    *   Controllable `asyncio` timer loop per client or managed globally.
    *   Detailed API error handling and status reporting via WebSocket.
    *   Manage client state (active, interval).
    *   **(Security) Implement WSS (Secure WebSockets).**
    *   **(Security) Add authentication layer for WebSocket clients.**
    *   **(Security) Implement rate limiting for commands.**
    *   **(Security) Add input validation for WebSocket messages.**
*   **New React Native App:**
    *   Robust WebSocket client with auto-reconnect.
    *   UI for Start/Stop, Interval configuration, "Describe Now" button, Status display, Description history view.
    *   Send appropriate commands.
    *   Handle incoming description and error/status messages.
    *   Integrate TTS and Haptics libraries.
    *   Manage application state (connection status, active status, history list).
    *   **(Security) Configure WebSocket client for WSS and certificate handling (if needed).**
    *   **(Security) Implement logic to send authentication token.** 