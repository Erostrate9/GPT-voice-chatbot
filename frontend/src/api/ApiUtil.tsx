import axios from 'axios';
const URL = 'http://localhost:8000/';
const TTS = URL + 'text-to-speech';
const ASR = URL + 'speech-to-text';
 

export function createBlobURL(data: any) {
    const blob = new Blob([data], { type: "audio/mpeg" });
    const url = window.URL.createObjectURL(blob);
    return url;
};

export async function getTextToSpeechBlobUrl(text: string): Promise<string> {
  try {
    const formData = new FormData();
    formData.append('text', text);

    const response = await axios.post( TTS, formData, {
      responseType: 'blob', // Expecting a blob response from the API
      withCredentials: true,
    });
    return createBlobURL(response.data);
  } catch (error) {
    console.error('Error fetching text-to-speech audio:', error);
    return '';
  }
};

export async function convertBlobUrlToText(blobUrl: string, mode: string): Promise<string> {
    try {
      const response = await fetch(blobUrl);
      const blob = await response.blob();
  
      // Construct audio to send file
      const formData = new FormData();
      formData.append("audio", blob, "myFile.wav");
      formData.append("mode", mode);
  
      // Send form data to API endpoint
      const result = await axios.post(ASR, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Access-Control-Allow-Credentials': true,
        },
        withCredentials: true,
      });
  
      if (result.data && result.data.status === 'ok') {
        return result.data.text;
      } else {
        console.error('Speech to text conversion failed', result.data);
        return '';
      }
    } catch (error) {
      console.error('Error converting blob URL to text:', error);
      return '';
    }
};