import { ReactMediaRecorder } from "react-media-recorder";
import RecordIcon from "./RecordIcon";
import { useState } from "react";

type Props = {
  handleStop: any;
};

const MessageRecorder = ({ handleStop }: Props) => {
  const [isRecording, setIsRecording] = useState(false);

  return (
    <ReactMediaRecorder
      audio
      onStop={handleStop}
      render={({ status, startRecording, stopRecording }) => {
        const toggleRecording = () => {
          if (isRecording) {
            stopRecording();
          } else {
            startRecording();
          }
          setIsRecording(!isRecording);
        };
        return (
        <div className="mt-2">
          <button
            onClick={toggleRecording}
            className="bg-white p-4 rounded-full"
          >
            <RecordIcon
              classText={
                status == "recording"
                  ? "animate-pulse text-red-500"
                  : "text-sky-500"
              }
            />
          </button>
          <p className="mt-2 text-white font-light">{status}</p>
        </div>
      )}}
    />
  );
};

export default MessageRecorder;
