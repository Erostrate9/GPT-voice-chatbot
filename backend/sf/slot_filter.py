import copy
import json
from datetime import datetime
from typing import Any, Dict, List
from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory
from langchain.memory.entity import BaseEntityStore, InMemoryEntityStore
from langchain.memory.utils import get_prompt_input_key
from langchain.prompts.base import BasePromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.schema.messages import get_buffer_string
from langchain_openai import ChatOpenAI
from pydantic import Field

from sf.prompt import DIET_PLAN_SLOT_EXTRACTION_PROMPT, CALORIE_CALCULATION_SLOT_EXTRACTION_PROMPT, \
    RECIPE_RECOMMENDATION_SLOT_EXTRACTION_PROMPT, RECIPE_SEARCH_SLOT_EXTRACTION_PROMPT, ASK_SLOT_PROMPT

DIET_PLAN_SLOT_DICT = {"height": "null", "weight": "null", "fitness_program": "null", "age": "null",
                       "avoid_eating": "null"}
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
    buffer = []

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

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables."""
        return [self.slot_key, self.chat_history_key, self.inform_check_key]

    def finish_check(self):
        self.finish = all(value != "null" for value in self.current_slots.values())

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        text = inputs["text"]
        intent = inputs["intent"]
        if intent != self.intent:
            self.set_intent(intent)

        slots = self.current_slots

        chain = LLMChain(llm=self.llm, prompt=self.slot_extraction_prompt)
        output = chain.predict(
            history=self.buffer, input=text, slots=json.dumps(slots),
        )

        output = output.replace("None", "null")
        try:
            output_json = json.loads(output)
        except Exception as e:
            print(f"Error parsing output to JSON: {e}, output: {output}")
            output_json = slots

        self.current_slots.update({k: v for k, v in output_json.items() if v != "null"})
        self.finish_check()
        self.buffer = text

        return {
            self.chat_history_key: self.buffer,
            self.intent_key: self.intent,
            self.finish_key: self.finish,
            self.slot_key: self.current_slots,
        }

    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()
        self.entity_store.clear()
        self.intent = 0
        self.current_slots = copy.deepcopy(self.default_slots)

    def ask_slots(self):
        # 根据当前意图设置任务描述
        task_descriptions = {
            1: "designing a diet plan",
            2: "calculating calorie intake",
            3: "recommending recipes based on ingredients",
            4: "providing detailed steps for a recipe"
        }
        task_description = task_descriptions.get(self.intent, "assisting with your request")

        # 生成当前槽位状态的描述
        slots_description = json.dumps(self.current_slots, indent=2)

        # 使用ASK_SLOT_PROMPT模板和langchain调用GPT生成询问文本
        chain = LLMChain(llm=self.llm, prompt=ASK_SLOT_PROMPT)
        question = chain.predict(
            task_description=task_description, slots=slots_description,
        )

        return question
