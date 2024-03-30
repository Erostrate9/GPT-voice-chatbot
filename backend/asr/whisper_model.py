import whisper
from openai import OpenAI


class WhisperModel:
    def __init__(self, model_name='tiny.en'):
        self.model = whisper.load_model(name=model_name)
        self.client = OpenAI()

    def transcribe_offline(self, audio_path):
        result = self.model.transcribe(audio_path)
        return result["text"]

    def transcribe_online(self, audio_input):
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_input,
            response_format="text",
            language="en",
            temperature=0.2
        )
        return transcription
