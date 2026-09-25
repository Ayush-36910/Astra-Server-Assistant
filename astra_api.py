import os
import time
import asyncio
import edge_tts
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from google import genai
from google.genai import types
from groq import Groq
from dotenv import load_dotenv

# load keys
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GEMINI_API_KEY or not GROQ_API_KEY:
    print("Error: API Keys missing! Check .env file.")
    exit()

# initialize clints
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="Astra Complete Brain Server")

system_instruction = """
You are Astra, a highly intelligent and fast AI voice assistant. 
Follow these strict rules:
1. Keep answers brief, conversational, and directly to the point.
2. If the user asks a question in Hindi or Hinglish, output the final answer STRICTLY in Devanagari script (हिंदी).
3. Do not use markdown formatting like asterisks (**) or bullet points. Use plain text.
"""

print("Booting Astra API Server & Initializing Memory...")
chat = gemini_client.chats.create(
    model='gemini-3.6-flash',
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7 
    )
)

async def generate_audio(text, voice="hi-IN-SwaraNeural", output_file="reply.mp3"):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

# endpoint which will recieve an audio file
@app.post("/ask-voice", response_class=FileResponse)
async def ask_voice_endpoint(audio_file: UploadFile = File(...)):
    print("\n[ESP32 -> Server] Ek nayi audio file aayi hai...")
    
    # 1. save temparpry audio file 
    temp_input_path = "temp_input.wav"
    with open(temp_input_path, "wb") as f:
        f.write(await audio_file.read())
        
    # 2. GROQ STT (sound into text)
    print("[Groq] Aawaz ko text mein convert kar raha hai...")
    with open(temp_input_path, "rb") as file:
        transcription = groq_client.audio.transcriptions.create(
          file=(audio_file.filename, file.read()),
          model="whisper-large-v3",
          temperature=0.0 # Hallucination rokne ke liye
        )
    user_text = transcription.text
    print(f"[User Ka Sawaal]: {user_text}")
    
    # 3. GEMINI LLM (question's answers)
    print("[Gemini] Jawab soch raha hai...")
    reply_text = "माफ़ करना, सर्वर अभी व्यस्त है।" # Default error message
    
    for attempt in range(3):
        try:
            response = chat.send_message(user_text)
            reply_text = response.text
            break # if status = true then break the loop
        except Exception as e:
            if "503" in str(e):
                print(f"[Server thoda busy hai... Retrying {attempt+1}/3]")
                time.sleep(2)
            else:
                print(f"API Error: {e}")
                break
                
    print(f"[Astra Ka Jawab]: {reply_text}")
    
    # 4. EDGE-TTS (text to voice)
    output_audio_path = "reply.mp3"
    await generate_audio(reply_text, output_file=output_audio_path)
    
    # 5. send the audio file
    return FileResponse(output_audio_path, media_type="audio/mpeg")
