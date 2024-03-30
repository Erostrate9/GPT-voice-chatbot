from asr.speech_recognizer import SpeechRecognizer
from tts.speech_synthesis import SpeechSynthesis
from intent.intent_detection import IntentDetector
from action.api import Action
from sf.slot_filter import SlotMemory
from fastapi.responses import StreamingResponse, Response
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

import time

app = FastAPI()
# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:4173"
]

# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

asr = SpeechRecognizer(model_name='tiny.en')
tts = SpeechSynthesis(model="polly")
intent_detector = IntentDetector(model_name='gpt-3.5-turbo-0613')
action = Action()
sf = SlotMemory(llm=ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613"))

class MessagePayload(BaseModel):
    text: str
    intent: int = 0
    finish: bool = False
    slots: dict = []


# Check health
@app.get("/health")
async def check_health():
    return {"response": "healthy"}


@app.post('/speech-to-text')
async def audio_to_text(
        audio: UploadFile = File(),
        mode: str = 'online'
):
    transcribe_start_time = time.time()
    if mode == 'online' or mode == 'offline':
        text = asr.speech_to_text(audio, mode)
        transcribe_end_time = time.time()
        return {
            'status': 'ok',
            'text': text,
            'transcribe_time': transcribe_end_time - transcribe_start_time
        }
    else:
        return {
            'status': 'failed'
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


def handle_out_of_scope():
    return "I'm sorry we can't support your request at this time, I can help you in these areas below: 1: 'Designing a diet plan', 2: 'Calculate calorie intake', 3: 'Recommend recipes based on ingredients', 4: 'Provide detailed steps for recipes'."


@app.post("/receive-message/")
async def receive_message(message_payload: MessagePayload):
    message_dict = message_payload.model_dump()
    message_dict = intent_detector.intent_detection(message_dict)
    if message_dict["intent"] != 0 or message_dict["intent"] != 5:
        message_dict = sf.load_memory_variables(message_dict)
        if message_dict["finish"] == False:
            # TODO if some slots are "null" should ask user for that input
            response = sf.ask_slot(message_dict)
            message_payload.text = response
            message_payload.intent = message_dict["intent"]
            message_payload.slots = message_dict["slots"]
            return Response(content=message_payload)
        else:
            response = action.api_handler(message_dict)
            message_payload.text = response
            message_payload.intent = message_dict["intent"]
            message_payload.slots = message_dict["slots"]
            sf.clear()
            return Response(content=message_payload)
    message_payload.text = handle_out_of_scope()
    return Response(content=message_payload)
