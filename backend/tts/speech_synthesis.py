from tts.polly import Polly

PROFILE_NAME = 'adminuser'


class SpeechSynthesis(object):
    def __init__(self, model='polly'):
        if model == 'polly':
            self._model = Polly(profile_name=PROFILE_NAME)
        else:
            raise Exception('Unknown model: {}'.format(model))

    def text_to_speech(self, text: str):
        return self._model.text_to_speech(text)
