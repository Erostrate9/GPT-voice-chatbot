from asr.speech_recognizer import SpeechRecognizer
from tts.speech_synthesis import SpeechSynthesis
from intent.intent_detection import IntentDetector
from action.api import Action
from sf.slot_filter import SlotMemory
from fastapi.responses import Response
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dto.MessagePayload import MessagePayload
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


def handle_out_of_scope():
    return "I'm sorry we can't support your request at this time, I can help you in these areas below: 1: 'Designing a diet plan', 2: 'Calculate calorie intake', 3: 'Recommend recipes based on ingredients', 4: 'Provide detailed steps for recipes'."


@app.post("/chat")
async def chat(query: MessagePayload):
    print(query)
    if query.intent == intent_detector.label2id["Out-Of-Scope"]:
        query.intent = intent_detector.intent_detection(query.text)
        print("detected intent: " + str(query.intent))
    if query.intent != intent_detector.label2id["Out-Of-Scope"]:
        message_dict = sf.load_memory_variables(query)
        if not message_dict.finish:
            # if some slots are "null" should ask user for that input
            message_dict.text = sf.ask_slots()
            return message_dict
        else:
            # do action
            message_dict.text = action.api_handler(message_dict.intent, message_dict.slots)
            sf.clear()
            return message_dict
    resDto = MessagePayload(intet=query.intent, text=handle_out_of_scope())
    print(resDto)
    return resDto
