from fastapi import HTTPException, Response
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
from tempfile import gettempdir


class Polly:
    def __init__(self, profile_name='adminuser'):
        self._session = Session(profile_name=profile_name)
        self._polly = self._session.client("polly")

    def text_to_speech(self, text, voice_id='Joanna', output_format='mp3'):
        try:
            response = self._polly.synthesize_speech(
                Text=text,
                VoiceId=voice_id,
                OutputFormat=output_format
            )
        except (BotoCoreError, ClientError) as error:
            # The service returned an error, exit gracefully
            print(error)
            raise HTTPException(status_code=500, detail=str(error))

        # Access the audio stream from the response
        if "AudioStream" in response:
            # Note: Closing the stream is important because the service throttles on the
            # number of parallel connections. Here we are using contextlib.closing to
            # ensure the close method of the stream object will be called automatically
            # at the end of the with statement's scope.
            with closing(response["AudioStream"]) as stream:
                output = os.path.join(gettempdir(), "speech.wav")

                try:
                    # Open a file for writing the output as a binary stream
                    # with open(output, "wb") as file:
                        # file.write(stream.read())
                    return stream.read()
                except IOError as error:
                    # Could not write to file, exit gracefully
                    print(error)
                    raise HTTPException(status_code=500, detail=str(error))

        else:
            # The response didn't contain audio data, exit gracefully
            print("Could not stream audio")
            raise HTTPException(status_code=500, detail="The response didn't contain audio data")
