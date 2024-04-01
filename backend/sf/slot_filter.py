import copy
import json
from datetime import datetime
from typing import List
from langchain.chains.llm import LLMChain
from langchain.memory.chat_memory import BaseChatMemory
from langchain.prompts.base import BasePromptTemplate
from langchain.base_language import BaseLanguageModel
from dto.MessagePayload import MessagePayload

from sf.prompt import DIET_PLAN_SLOT_EXTRACTION_PROMPT, CALORIE_CALCULATION_SLOT_EXTRACTION_PROMPT, \
    RECIPE_RECOMMENDATION_SLOT_EXTRACTION_PROMPT, RECIPE_SEARCH_SLOT_EXTRACTION_PROMPT, ASK_SLOT_PROMPT

# slots need for each tasks
DIET_PLAN_SLOT_DICT = {"height": "null", "weight": "null", "fitness_program": "null", "age": "null",
                       "avoid_eating": "null"}
CALORIE_CALCULATION_SLOT_DICT = {"food": "null", "weight_or_number": "null"}
RECIPE_RECOMMENDATION_SLOT_DICT = {"ingredient": "null"}
RECIPE_SEARCH_SLOT_DICT = {"recipe_name": "null"}

"""
This class and the prompt used refer to the structure of Zehua Wen's slot memory class: https://github.com/iMagist486/Chatbot-Slot-Filling/blob/main/chains/slot_memory.py
This class aims to extract the user input slots using the cue learning feature of generative large language modeling and save these slots locally until the slots for entire task is completed (finish == false) before emptying them.
"""
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
    current_datetime = datetime.now().strftime("%Y/%m/%d %H:%M")
    buffer = []

    # set local intent, slot dict, and slots extraction prompt
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

    # set finish cheack if the slots requiring is finished
    def finish_check(self):
        self.finish = all(value != "null" for value in self.current_slots.values())

    # load the slots extraction and store them in local
    def load_memory_variables(self, query: MessagePayload) -> MessagePayload:
        text = query.text
        intent = query.intent
        if intent != self.intent:
            self.set_intent(intent)
        if(query.slots and len(query.slots)>0):
            self.current_slots = query.slots
        slots = self.current_slots
        chain = LLMChain(llm=self.llm, prompt=self.slot_extraction_prompt)
        output = chain.predict(
            history=self.buffer, input=text, slots=json.dumps(slots),
        )
        print('output: ', output)
        output = output.replace("None", "null")
        try:
            output_json = json.loads(output)
        except Exception as e:
            print(f"Error parsing output to JSON: {e}, output: {output}")
            output_json = slots

        self.current_slots.update({k: v for k, v in output_json.items() if v is not None and v != "null"})
        self.finish_check()
        self.buffer = text
        return MessagePayload(text=self.buffer, intent=intent, finish=self.finish, slots=self.current_slots)

    # initial the slot memory
    def clear(self) -> None:
        """Clear memory contents."""
        self.chat_memory.clear()
        self.intent = 0
        self.current_slots = copy.deepcopy(self.default_slots)
        self.finish = False

    # ask for empty slots
    def ask_slots(self):
        # Setting the task description based on the current intent
        task_descriptions = {
            1: "designing a diet plan",
            2: "calculating calorie intake",
            3: "recommending recipes based on ingredients",
            4: "providing detailed steps for a recipe"
        }
        task_description = task_descriptions.get(self.intent, "assisting with your request")

        # Generate a description of the current slot
        slots_description = json.dumps(self.current_slots, indent=2)

        # Generate query text using ASK_SLOT_PROMPT template and langchain call to GPT
        chain = LLMChain(llm=self.llm, prompt=ASK_SLOT_PROMPT)
        question = chain.predict(
            task_description=task_description, slots=slots_description,
        )

        return question
