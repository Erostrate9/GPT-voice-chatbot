from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)


class IntentDetector(object):
    def __init__(self, model_name='gpt-3.5-turbo-0613'):
        self.intents = [
            {"label": 0, "description": "Out-Of-Scope"},
            {"label": 1, "description": "Diet-Plan-Design"},
            {"label": 2, "description": "Food-Calorie-Calculation"},
            {"label": 3, "description": "Recipe-Recommendation"},
            {"label": 4, "description": "Recipe-Search"}
        ]
        self.id2label = {intent['label']: intent['description'] for intent in self.intents}
        self.label2id = {intent['description']: intent['label'] for intent in self.intents}
        examples = [
            {'text': 'I want to lose weight, can you create a diet plan for me?', 'intent': 'Diet-Plan-Design'},
            {'text': 'I am 180cm tall and weigh 70kg, I want to build muscle, can you design a diet plan for me?',
             'intent': 'Diet-Plan-Design'},
            {'text': 'How many calories are in two apples and a banana?', 'intent': "Food-Calorie-Calculation"},
            {
                'text': 'I had a McDonald\'s big mac for dinner and a large box of fries, how many calories did I take in?',
                'intent': "Food-Calorie-Calculation"},
            {'text': 'What can I cook with chicken breast and rice?', 'intent': "Recipe-Recommendation"},
            {'text': 'I have a steak and a potato. Can you give me a suggestion for dinner?',
             'intent': "Recipe-Recommendation"},
            {'text': 'I would like to know how to make a cheese omelette.', 'intent': 'Recipe-Search'},
            {'text': 'Please tell me how to make a piece of lasagna?', 'intent': 'Recipe-Search'},
            {'text': "hello", 'intent': 'Out-Of-Scope'},
        ]
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{text}"),
                ("ai", "{intent}"),
            ]
        )

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

        final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                 """
                You are a Kitchen Assistance Intent Detector. 
                Your task is to classify the text into one of the predefined intents. 
                See below all the possible intents:
                ###
                label: 0
                intent: Out-Of-Scope 
                description: text does not contains any above intents will be classified as Out of scope
                ###
                label: 1, 
                intent: Diet-Plan-Design
                description: Design a diet plan for the user based on user inputs
                ###
                label: 2
                intent: Food-Calorie-Calculation
                description: Calculate the calorie total of all foods entered by the user
                ###
                label: 3
                intent: Recipe-Recommendation
                description: Provides recipe suggestions based on available ingredients provided by the user.
                ###
                label: 4
                intent: Recipe-Search
                description: Provides a detailed process for a recipe based on the name of the recipe provided by the user.
                ###
                See below a couple of examples:
                """),
                few_shot_prompt,
                ("human", "{text}"),
            ]
        )

        model = ChatOpenAI(temperature=0, model=model_name)
        self.chain = final_prompt | model

    def intent_detection(self, text):
        inp = {'text': text}
        response = self.chain.invoke(inp).content
        intent = 0
        if response in self.label2id.keys():
            intent = self.label2id[response]
        return intent
