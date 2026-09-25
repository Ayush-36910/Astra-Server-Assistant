# Astra AI Brain 🧠

This is the cloud backend server for **Astra**, a portable, voice-activated AI assistant built with ESP32. 

## How it Works ⚙️
1. **Ears (STT):** Receives audio from the ESP32 microphone and converts it to text using the ultra-fast **Groq (Whisper-Large-V3)** API.
2. **Brain (LLM):** Processes the text and generates a smart, concise response in Devanagari script using **Google Gemini 3.6-flash**.
3. **Voice (TTS):** Converts the text response back into a natural-sounding Indian voice (MP3) using **Edge-TTS** and streams it back to the ESP32 amplifier.

## Tech Stack 🛠️
* **Framework:** FastAPI (Python)
* **AI Models:** Groq (Whisper), Google Gemini
* **Audio Processing:** Edge-TTS

## Note
This API is designed to be hosted 24/7 on cloud platforms (like Render) to act as the permanent backend for the Astra ESP32 hardware.
