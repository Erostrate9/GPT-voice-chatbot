import io
import librosa
from asr.whisper_model import WhisperModel
from fastapi import File, Form, UploadFile


class SpeechRecognizer(object):
    def __init__(self, model_name='tiny.en'):
        self.model = WhisperModel(model_name)

    def speech_to_text(self, bt):
        # # convert into BinaryIO
        memory_file = io.BytesIO(bt)
        # # obtain audio data
        data, sample_rate = librosa.load(memory_file)
        # # resample into 16000
        resample_data = librosa.resample(data, orig_sr=sample_rate, target_sr=16000)
        # asr
        text = self.model.transcribe(data)
        print(text)

        return text
