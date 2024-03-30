import { useState } from "react";
import Title from "./Title";
import axios from "axios";
import RecordMessage from "./RecordMessage";
import Message from "./Message";
import {getTextToSpeechBlobUrl, createBlobURL, convertBlobUrlToText} from "../api/ApiUtil";
axios.defaults.withCredentials = true

const Controller = () => {
  const USER = "me";
  const AI = "Cooking Assistant";

  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<any[]>([]);

  const  handleSubmit = async () => {
    const userInput = inputValue.trim();
    console.log(userInput);
    if (!userInput){
      setInputValue('');
      return;
    }
    // construct user message
    const myMessage = { sender: USER, blobUrl: null, text:userInput};
    const messagesArr = [...messages, myMessage];
    setMessages(messagesArr);
    // construct ai message
    const aiMessage = await getAiResponse(userInput);
    messagesArr.push(aiMessage);
    setMessages(messagesArr)
    setInputValue('');
    // const messagePayload = {
    //   text: inputValue, // 用户输入的文本
    //   intent: 0,        // 根据你的需求，这里是固定值
    //   finish: false,    // 根据你的需求，这里是固定值
    //   slots: {}         // 根据你的需求，这里是固定值
    // };

    // axios.post('http://localhost:3000/receive-message', messagePayload)
    // .then(response => {
    //   // 这里处理后端的响应
    //   console.log(response);
    //   // 这里是你原来的逻辑，将消息添加到 messages 数组中
    //   const myMessage = { sender: "me", blobUrl: null, text: inputValue};
    //   const messagesArr = [...messages, myMessage];
    //   setMessages(messagesArr);
    //   setInputValue('');
    // })
    // .catch(error => {
    //   // 处理请求失败的情况
    //   console.error('There was an error!', error);
    // });
  };

  const getAiResponse = async (inputText: string) => {
    const resposne = inputText.trim();
    // tts
    const blobUrl = await getTextToSpeechBlobUrl(resposne);
    // play audio
    const audio = new Audio();
    audio.src = blobUrl;
    audio.play();
    return { sender: AI, blobUrl: blobUrl, text: resposne};
  }

  const handleStop = async (blobUrl: string) => {
    console.log('handleStop');
    setIsLoading(true);
    // speech to text
    const asrText = await convertBlobUrlToText(blobUrl, 'online');
    if (!asrText){
      setIsLoading(false);
      console.log("Failed to recognize user's voice input.")
      return;
    }
    // Append recorded message to messages
    const myMessage = { sender: USER, blobUrl: blobUrl, text: asrText };
    const messagesArr = [...messages, myMessage];
    // Get AI response
    const aiMessage =  await getAiResponse(asrText);
    messagesArr.push(aiMessage);
    setMessages(messagesArr);
    setIsLoading(false);
  };

  return (
    <div className="h-screen overflow-y-hidden">
      {/* Title */}
      <Title setMessages={setMessages} aiName={AI}/>

      <div className="flex flex-col justify-between h-screen">
        {/* Conversation */}
        <div className="flex-1 mt-5 px-5 flex-grow overflow-y-auto">
          {
          messages?.map((audio, index) => {
            return <Message audio={audio} key={index + audio.sender}/>
          })
          }
          {messages.length == 0 && !isLoading && (
            <div className="text-center font-light italic mt-10">
              Send {AI} a message...
            </div>
          )}
          {isLoading && (
            <div className="text-center font-light italic mt-10 animate-pulse">
              Gimme a few seconds...
            </div>
          )}
        </div>
        {/* Recorder */}
        <div className="pb-16 w-full py-2 border-t text-center bg-gradient-to-r from-sky-500 to-green-500">
          <div className="flex justify-center items-center w-full">
            <div>
              <RecordMessage handleStop={handleStop} />
            </div>
            <div>
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                className="bg-gray-200 appearance-none border-2 border-gray-200 rounded py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleSubmit(); // Invoke handleSubmit when Enter is pressed
                  }
                }}
              />
              <button onClick={handleSubmit}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >Send</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Controller;
