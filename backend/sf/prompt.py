
from langchain.prompts.prompt import PromptTemplate


_DEFAULT_DIET_PLAN__SLOT_EXTRACTION_TEMPLATE = """
You are an AI assistant, reading the transcript of a conversation between an AI and a human.
From the last line of the conversation, extract all proper named entity(here denoted as slots) that match about making a diet plan.
Named entities required for making a diet plan include height, weight, fitness program, avoid eating.

The output should be returned in the following json format.
{{
    "height": "Height of the user, including numbers and units, e.g.: 180 cm"
    "weight": "Weight of the user, including numbers and units, e.g.: 70 kg"
    "age": "Age of the user, only the number of years. e.g.: 23"
    "fitness_program": "The user's current fitness program, such as wanting to gain weight, build muscle, lose weight, or eat normally."
    "avoid_eating": "User taboos, such as allergic foods, no meat, no sugar, or no taboos."
}}

If there is no match for each slot, assume "null".(e.g., user is simply saying hello or having a brief conversation).

EXAMPLE
Conversation history:
Person #1: I want to create a diet plan.
AI: "Hi, may I ask your height?"
Current Slots: {{"height": "null", "weight": "null", "age":"null", "fitness_program": "null", "avoid_eating": "null"}}
Last line:
Person #1: 180 CM
Output Slots: {{"height": "180 CM", "weight": "null", "age":"null", "fitness_program": "null", "avoid_eating": "null"}}
END OF EXAMPLE

EXAMPLE
Conversation history:
Person #1: I'm 183cm tall, and weigh 70kg. I want to create a diet plan.
AI: OK, may I ask your Age?
Current Slots: {{"height": "183 CM", "weight": "null", "age":"23", "fitness_program": "null", "avoid_eating": "null"}}
Last line:
Person #1: I'm 23 years old
Output Slots: {{"height": "183 CM", "weight": "70 KG","age":"23", "fitness_program": "null", "avoid_eating": "null"}}
END OF EXAMPLE

Output Slots must be in json format!

Begin!
Conversation history (for reference only):
{history}
Current Slots:
{slots}
Last line of conversation (for extraction):
Human: {input}

Output Slots:"""
DIET_PLAN_SLOT_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input", "slots"],
    template=_DEFAULT_DIET_PLAN__SLOT_EXTRACTION_TEMPLATE,
)




_DEFAULT_CALORIE_CALCULATION_SLOT_EXTRACTION_TEMPLATE = """
You are an AI assistant, reading the transcript of a conversation between an AI and a human.
From the last line of the conversation, extract all proper named entity(here denoted as slots) that match about calculating calorie of foods.
Named entities required for calculating calorie of foods include food and weight or number.

The output should be returned in the following json format.
{{
    "food": "a list contains all food's name, in user input order"
    "weight_or_number": "a list contains all weight of the input foods, including numbers and units, in same order with food"
}}

If there is no match for each slot, assume "null".(e.g., user is simply saying hello or having a brief conversation).

EXAMPLE
Conversation history:
Person #1: Can you calculate the calories for me?.
AI: "Hi, Which foods do you want to count calories for?"
Current Slots: {{"food": "null", "weight_or_number": "null"}}
Last line:
Person #1: Apples and bananas
Output Slots: {{"food": ["apple","banana"], "weight_or_number": "null"}}
END OF EXAMPLE

EXAMPLE
Conversation history:
Person #1: Can you help me count the calories in these apples and bananas?
AI: OK, may I ask your Weight or number of apples and bananas?
Current Slots: {{"food": ["apple","bananas"], "weight_or_number": "null"}}
Last line:
Person #1: 1 KG apples and 1 banana
Output Slots: {{"food": ["apple","bananas"], "weight_or_number": ["1 KG","1 piece"]}}
END OF EXAMPLE

Output Slots must be in json format!

Begin!
Conversation history (for reference only):
{history}
Current Slots:
{slots}
Last line of conversation (for extraction):
Human: {input}

Output Slots:"""
CALORIE_CALCULATION_SLOT_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input", "slots"],
    template=_DEFAULT_CALORIE_CALCULATION_SLOT_EXTRACTION_TEMPLATE,
)




_DEFAULT_RECIPE_RECOMMENDATION__SLOT_EXTRACTION_TEMPLATE = """
You are an AI assistant, reading the transcript of a conversation between an AI and a human.
From the last line of the conversation, extract all proper named entity(here denoted as slots) that match about recommending recipes.
Named entities required for recommending recipes include ingredient.

The output should be returned in the following json format.
{{
    "ingredient": "a list contains all foods user input"

}}

If there is no match for each slot, assume "null".(e.g., user is simply saying hello or having a brief conversation).

EXAMPLE
Conversation history:
Person #1: can you recommend me some recipes?
AI: Hi, can I ask you what kind of food you have now??
Current Slots: {{"ingredient": "null"}}
Last line:
Person #1: egg and tomato
Output Slots: {{"ingredient": ["egg","tomato"]}}
END OF EXAMPLE

Output Slots must be in json format!

Begin!
Conversation history (for reference only):
{history}
Current Slots:
{slots}
Last line of conversation (for extraction):
Human: {input}

Output Slots:"""
RECIPE_RECOMMENDATION_SLOT_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input", "slots"],
    template=_DEFAULT_RECIPE_RECOMMENDATION__SLOT_EXTRACTION_TEMPLATE,
)



_DEFAULT_RECIPE_SEARCH__SLOT_EXTRACTION_TEMPLATE = """
You are an AI assistant, reading the transcript of a conversation between an AI and a human.
From the last line of the conversation, extract all proper named entity(here denoted as slots) that match about providing human detailed steps for the recipe they input.
Named entities required for providing human detailed steps for the recipe they input include the name of recipe.

The output should be returned in the following json format.
{{
    "recipe_name": "the name of recipe use input"
}}

If there is no match for each slot, assume "null".(e.g., user is simply saying hello or having a brief conversation).

EXAMPLE
Conversation history:
Person #1: Can you show me the cooking steps?
AI: Which dish would you like to make?
Current Slots: {{"recipe_name": "null"}}
Last line:
Person #1: omelet
Output Slots: {{"recipe_name": "omelet"}}
END OF EXAMPLE

Output Slots must be in json format!

Begin!
Conversation history (for reference only):
{history}
Current Slots:
{slots}
Last line of conversation (for extraction):
Human: {input}

Output Slots:"""
RECIPE_SEARCH_SLOT_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["history", "input", "slots"],
    template=_DEFAULT_RECIPE_SEARCH__SLOT_EXTRACTION_TEMPLATE,
)

_ASK_SLOT_TEMPLATE = """
You are an AI designed to assist with {task_description}. To proceed, you need to gather certain information from the user, but some details are missing. Given the current slots, generate a polite and concise question to ask the user for the missing information.

Current Slots and Descriptions:
- height: The height of the user in cm or inches.
- weight: The weight of the user in kg or pounds.
- age: The age of the user
- fitness_program: The user's goal, such as losing weight or gaining muscle.
- avoid_eating: Any dietary restrictions or allergies the user has.
- food: The type of food the user is inquiring about.
- weight_or_number: The weight or quantity of the food.
- ingredient: Ingredients available for recipe recommendations.
- recipe_name: The name of the recipe for which the user seeks detailed steps.

Current Slots:
{slots}


Generate a question to ask for the missing information.
"""

ASK_SLOT_PROMPT = PromptTemplate(input_variables=["task_description", "slots"], template=_ASK_SLOT_TEMPLATE)