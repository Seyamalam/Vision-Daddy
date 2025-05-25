uvicorn server:app --host 0.0.0.0 --port 8000 --reload

(cd ~/llama.cpp/build && ./bin/llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99)


cd dia-tts-server && python server.py


https://8003-01jvyxcckwn7v10c56ara2prnw.cloudspaces.litng.ai






For Future Reference:
1) Make the Vision Tab Use the Configured Server URL
Read the server URL from AsyncStorage in the Vision tab, not a hardcoded value.
2) Allow Dynamic ESP32 IP Configuration
Make the backend accept the ESP32 stream URL as a parameter (via env var, config file, or API).
3) Optionally, add an endpoint to update the ESP32 stream URL at runtime.
4) Allow Custom Prompts from the App
Let users enter a custom prompt in the app, which is sent to the /vision endpoint.
5) Add Authentication
Secure the backend and/or app with API keys or user accounts.
6) Improve Error Handling and User Feedback
7) Show more detailed error messages in the app.
8) (Optional) Add Direct Camera Support
Let the app capture and send images directly, as an alternative to the ESP32 stream.
9) (Optional) Add WebSocket/Push for Live Updates
For real-time status or streaming.


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


Vision Tab: User Journey & Process Flow
1. App Startup & Backend Check
When the user opens the Vision tab, the app:
Checks if the backend server is reachable.
Polls the backend for ESP32 camera connection status.
Shows a status indicator (connected/disconnected).
2. Manual Mode (Auto-Capture OFF)
UI Elements:
“Capture” button is visible.
No interval or auto-TTS controls are shown.
User Action:
User taps “Capture” to request a vision analysis.
Process:
App sends a POST request to /vision on the backend.
Backend grabs the latest ESP32 frame, sends it to the AI backend, and returns a description.
App displays the AI response.
User can tap the “🔊 Play” button to hear the response via Groq TTS.
3. Auto-Capture Mode (Auto-Capture ON)
UI Elements:
“Capture” button is hidden.
Interval selector (dropdown/modal) appears (choose 2, 3, 5, or 10 seconds).
“Auto TTS” toggle appears.
User Action:
User enables auto-capture and optionally enables auto-TTS.
Process:
If Auto TTS is OFF:
App automatically sends vision requests at the selected interval.
Each response is displayed in the app.
User can manually tap “🔊 Play” to hear any response.
If Auto TTS is ON:
App sends a vision request.
When a response is received, it is immediately sent to Groq TTS.
The app plays the audio as soon as it’s ready.
After the audio finishes, the app waits for the selected interval, then sends the next vision request.
This loop continues until the user disables auto-capture or auto-TTS.
4. History & Logs
The app maintains a history of recent AI responses.
A log panel shows backend connectivity, ESP32 status, and capture/TTS events for transparency and debugging.
5. Error Handling
If the backend or ESP32 is unreachable, the app displays an error message.
If TTS or vision requests fail, errors are logged and shown in the log panel.
