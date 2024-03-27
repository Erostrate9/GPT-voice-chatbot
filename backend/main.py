from asr.speech_recognizer import SpeechRecognizer
from tts.speech_synthesis import SpeechSynthesis
from fastapi.responses import StreamingResponse, Response
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import time

app = FastAPI()
asr = SpeechRecognizer(model_name='tiny.en')
tts = SpeechSynthesis(model="polly")

# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
]


# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check health
@app.get("/health")
async def check_health():
    return {"response": "healthy"}

@app.post('/speech-to-text')
async def audio_to_text(
    audio: UploadFile = File()
):
    transcribe_start_time = time.time()
    # read byte flow
    bt = audio.file.read()
    text = asr.speech_to_text(bt)
    transcribe_end_time = time.time()
    return {
        'status': 'ok',
        'text': text,
        'transcribe_time': transcribe_end_time - transcribe_start_time
    }

@app.post('/text-to-speech')
async def text_to_speech(text: str = Form()):
    content = tts.text_to_speech(text)
    return Response(content=content, media_type="audio/mpeg")

# Post bot response
# Note: Not playing back in browser when using post request.
@app.post("/post-audio")
async def post_audio(file: UploadFile = File(...)):
    # Convert audio to text - production
    # Save the file temporarily
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
    audio_input = open(file.filename, "rb")
    # Convert audio to text - production
    text = asr.speech_to_text(audio_input.read())
    # Convert chat response to audio
    audio_output = tts.text_to_speech(text)
    # Guard: Ensure output
    if not audio_output:
        raise HTTPException(status_code=400, detail="Failed audio output")
    # Create a generator that yields chunks of data
    # def iterfile():
    #     yield audio_output
    # return StreamingResponse(iterfile(), media_type="application/octet-stream")
    return Response(content=audio_output, media_type="audio/mpeg")
