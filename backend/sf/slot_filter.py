import copy
import json
from datetime import datetime
from typing import Any, Dict
from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.entity import BaseEntityStore, InMemoryEntityStore
from langchain.memory.utils import get_prompt_input_key
from langchain.prompts.base import BasePromptTemplate
from langchain.schema import BaseLanguageModel
from langchain.schema.messages import get_buffer_string
from pydantic import Field

from sf.prompt import DIET_PLAN_SLOT_EXTRACTION_PROMPT,CALORIE_CALCULATION_SLOT_EXTRACTION_PROMPT,RECIPE_RECOMMENDATION_SLOT_EXTRACTION_PROMPT,RECIPE_SEARCH_SLOT_EXTRACTION_PROMPT

DIET_PLAN_SLOT_DICT = {"height": "null", "weight": "null", "fitness_program": "null", "avoid_eating": "null"}
CALORIE_CALCULATION_SLOT_DICT = {"food": "null", "weight_or_number": "null"}
RECIPE_RECOMMENDATION_SLOT_DICT = {"ingredient": "null"}
RECIPE_SEARCH_SLOT_DICT = {"recipe_name": "null"}

class SlotMemory(BaseChatMemory):
    llm: BaseLanguageModel
    slot_extraction_prompt: BasePromptTemplate = DIET_PLAN_SLOT_EXTRACTION_PROMPT
    k: int = 10
    human_prefix: str = "Human"
    ai_prefix: str = "AI"
    chat_history_key: str = "text"
    slot_key: str = "slots"
    finish_key: str = "finish"
    intent_key: str = "intent"
    return_messages: bool = False
    default_slots = DIET_PLAN_SLOT_DICT
    current_slots = copy.deepcopy(default_slots)
    intent = 0
    finish = False
    entity_store: BaseEntityStore = Field(default_factory=InMemoryEntityStore)
    current_datetime = datetime.now().strftime("%Y/%m/%d %H:%M")

    def set_intent(self, intent):
        self.intent = intent
        if intent == 1:
            self.slot_extraction_prompt = DIET_PLAN_SLOT_EXTRACTION_PROMPT
            self.default_slots = DIET_PLAN_SLOT_DICT
            self.current_slots = copy.deepcopy(self.default_slots)
        elif intent == 2:
            self.slot_extraction_prompt = CALORIE_CALCULATION_SLOT_EXTRACTION_PROMPT
            self.default_slots = CALORIE_CALCULATION_SLOT_DICT
            self.current_slots = copy.deepcopy(self.default_slots)
        elif intent == 3:
            self.slot_extraction_prompt = RECIPE_RECOMMENDATION_SLOT_EXTRACTION_PROMPT
            self.default_slots = RECIPE_RECOMMENDATION_SLOT_DICT
            self.current_slots = copy.deepcopy(self.default_slots)
        elif intent == 4:
            self.slot_extraction_prompt = RECIPE_SEARCH_SLOT_EXTRACTION_PROMPT
            self.default_slots = RECIPE_SEARCH_SLOT_DICT
            self.current_slots = copy.deepcopy(self.default_slots)
        

    def finish_check(self):
        self.finish = all(value != "null" for value in self.current_slots.values())

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """根据对话历史和最新输入更新槽位信息，并检查是否已收集全部信息。"""
        text = inputs["text"]
        intent = inputs["intent"]
        self.set_intent(intent)
        buffer_string = self.buffer 
        slots = self.current_slots
        
        chain = LLMChain(llm=self.llm, prompt=self.slot_extraction_prompt)
        output = chain.predict(
            history=buffer_string, input=text, slots=json.dumps(slots), 
        )
        output = output.replace("None", "null")
        try:
            output_json = json.loads(output)
        except Exception as e:
            print(f"Error parsing output to JSON: {e}, output: {output}")
            output_json = slots
        
        self.current_slots.update({k: v for k, v in output_json.items() if v != "null"})
        self.finish_check()
        return {
            self.chat_history_key: buffer_string,
            self.intent_key: self.intent,
            self.finish_key: self.finish,
            self.slot_key: json.dumps(self.current_slots),  
        }