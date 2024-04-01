import os
import requests
from openai import OpenAI
import re

"""
Class Action(): a class to perform tasks intended by the user
"""
class Action(object):

    def __init__(self):
        self.client = OpenAI()
    
    # Calculate bmi based on height weight age
    def calculate_bmi(self, height, weight, age):
        bmi = weight / ((height / 100) ** 2)
        consumption = 1.2 * (655 + (9.6 * weight) + (1.8 * height) - (4.7 * age))
        return bmi, consumption

    # Conversion of height units to standard units
    def parse_height(self,height_str):
        match = re.match(r"(\d+(\.\d+)?)[\s]?(cm|in|inches)$", height_str, re.IGNORECASE)
        if match:
            value, _, unit = match.groups()
            if 'cm' in unit.lower():
                return float(value)
            elif 'in' in unit.lower():  # Covers 'in' and 'inches'
                return float(value) * 2.54  # Inch to centimeter conversion
        return None  # Unmatched or incorrectly formatted

    # Conversion of weight units to standard units
    def parse_weight(self,weight_str):
        match = re.match(r"(\d+(\.\d+)?)[\s]?(kg|lb|pounds)$", weight_str, re.IGNORECASE)
        if match:
            value, _, unit = match.groups()
            if 'kg' in unit.lower():
                return float(value)
            elif 'lb' in unit.lower() or 'pounds' in unit.lower():
                return float(value) * 0.453592  # Conversion of pounds to kilograms
        return None  # Unmatched or incorrectly formatted

    # Calculate the user's bmi index and calorie consumption, and call the GPT API to generate the appropriate diet plan.
    def calculate_bmi_and_diet_plan(self, slots):
        height_str = slots["height"]
        weight_str = slots["weight"]
        age = re.search(r'\d+', slots["age"]).group(0)
        age = int(age)

        fitness_program = slots["fitness_program"]
        avoid_eating = slots["avoid_eating"]

        height = self.parse_height(height_str)
        weight = self.parse_weight(weight_str)
        print(height)
        print(weight)

        bmi, consumption = self.calculate_bmi(height, weight, age)
        bmi = weight / ((height / 100) ** 2)
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":f"Given that a person has a BMI of {bmi:.2f} and a daily calorie consumption of roughly {consumption:.2f} calories, this person is avoiding eating {avoid_eating}, and fitness program is {fitness_program}, recommend a diet plan for that person. (Output only the diet plan and don't say anything else.)"}
                ],
            max_tokens=150,
        )
        diet_plan_content = response.choices[0].message.content
        return f"Hello, your BMI is {bmi:.2f}, your daily calorie consumption is roughly {consumption:.2f} calories, and the recommended diet plan is:\n{diet_plan_content}"

    # Calling the GPT model to calculate the calories of the food
    def calculate_calorie_intake(self,slots):
        foods = slots["food"]
        quantities = slots["weight_or_number"]
        if len(foods) != len(quantities):
            return "Error: Foods and quantities lists must have the same length."
        prompt_parts = []
        prompt_parts.append("Calculate the total calories for:\n")
        for food, quantity in zip(foods, quantities):
            prompt_parts.append(f"{quantity} of {food}.")
        prompt = " ".join(prompt_parts)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":prompt}
                ],
            max_tokens=150,
        )
        return f"here is the calories calculation steps:\n {response.choices[0].message.content}."

    # The GPT model is invoked to recommend recipes based on the user's existing ingredients.
    def recommend_recipes_based_on_ingredients(self,slots):
        ingredients = slots["ingredient"]
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role":"system","content":f"Recommend recipes based on these ingredients: {', '.join(ingredients)}."}
                ],
            max_tokens=150,
        )
        return  response.choices[0].message.content

    # Calls the recipe-by-api-ninja API to search for all recipes with the same recipe name as the user input, 
    # returning the apology text if it is not there, or the first recipe in the list if it exists.
    def provide_detailed_steps_for_recipe(self,slots):
        recipe_name = slots["recipe_name"]
        url = 'https://recipe-by-api-ninjas.p.rapidapi.com/v1/recipe'
        querystring = {"query":recipe_name}
        recipe_details = requests.get(url, headers={"X-RapidAPI-Key": os.getenv("X_RAPIDAPI_KEY"), "X-RapidAPI-Host": "recipe-by-api-ninjas.p.rapidapi.com"},params=querystring)
        response_dict = recipe_details.json()
        if response_dict == []:
            return "We apologize for not finding the recipe you were searching for."
        else:
            response = response_dict[1]
            return f"The steps you need to complete if you want to make a {response['title']} are: {response['instructions']}"


    def handle_out_of_scope(self):
        return "I'm sorry we can't support your request at this time, I can help you in these areas below: 1: 'Designing a diet plan', 2: 'Calculate calorie intake', 3: 'Recommend recipes based on ingredients', 4: 'Provide detailed steps for recipes'."

    def api_handler(self, intent: str, slots: dict):
        if intent == 0:
            return self.handle_out_of_scope()
        elif intent == 1:
            return self.calculate_bmi_and_diet_plan(slots)
        elif intent == 2:
            return self.calculate_calorie_intake(slots)
        elif intent == 3:
            return self.recommend_recipes_based_on_ingredients(slots)
        elif intent == 4:
            return self.provide_detailed_steps_for_recipe(slots)
        else:
            return "Invalid intent."


