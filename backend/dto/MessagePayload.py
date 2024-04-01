from pydantic import BaseModel
class MessagePayload(BaseModel):
    text: str
    intent: int = 0
    finish: bool = False
    slots: dict = {}