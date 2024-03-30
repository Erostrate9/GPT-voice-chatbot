from asr.whisper_model import WhisperModel


class SpeechRecognizer(object):
    def __init__(self, model_name='tiny.en'):
        self.model = WhisperModel(model_name)

    def speech_to_text(self, file, mode):
        text = ''
        with open(file.filename, "wb") as buffer:
            buffer.write(file.file.read())
        audio_input = open(file.filename, "rb")
        if mode == 'offline':
            text = self.model.transcribe_offline(file.filename)
        elif mode == 'online':
            text = self.model.transcribe_online(audio_input)
        print(text)
        return text
