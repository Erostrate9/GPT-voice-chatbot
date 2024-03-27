type Props = {
    audio: any;
}
function Message({audio} :Props) {
    return (
        <div
          className={
            "flex flex-col " +
            (audio.sender == "rachel" && "flex items-end")
          }
        >
          {/* Sender */}
          <div className="mt-4 ">
            <p
              className={
                audio.sender == "rachel"
                  ? "text-right mr-2 italic text-green-500"
                  : "ml-2 italic text-blue-500"
              }
            >
              {audio.sender}
            </p>

            {/* Message */}
            <div>{audio.text}</div>
            {audio.blobUrl && <audio
              src={audio.blobUrl}
              className="appearance-none"
              controls
            />}
          </div>
        </div>
      );
}
export default Message;