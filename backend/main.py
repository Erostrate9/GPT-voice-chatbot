from asr.speech_recognizer import SpeechRecognizer
from tts.speech_synthesis import SpeechSynthesis
from intent.intent_detection import IntentDetector
from sf.slot_filter import SlotMemory
from sf.prompt import generate_dynamic_prompt
from fastapi.responses import StreamingResponse, Response
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import time

app = FastAPI()
asr = SpeechRecognizer(model_name='tiny.en')
tts = SpeechSynthesis(model="polly")
intent_detector = IntentDetector(model_name='gpt-3.5-turbo-0613')
sf = SlotMemory()

class MessagePayload(BaseModel):
    text: str
    intent: int = 0
    finish: bool = False
    slots: dict = []

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





@app.post("/receive-message/")
async def receive_message(message_payload: MessagePayload):
    message_dict = message_payload.model_dump()
    intetnt_dict = intent_detector.intent_detection(message_dict)
    if intetnt_dict["intent"] != 0 or intetnt_dict["intent"] != 5:  
        slot_dict = sf.load_memory_variables(intetnt_dict)
        if slot_dict["finish"] == False:
            # need to modify
            return Response(content=generate_dynamic_prompt(slot_dict["slot"],slot_dict["text"]), media_type="audio/mpeg")
    return {"received_data": message_payload}
